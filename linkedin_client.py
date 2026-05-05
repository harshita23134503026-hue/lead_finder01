import requests
import logging
import time
from typing import Dict, List, Optional, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInAPIClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = config.LINKEDIN_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-RestLi-Protocol-Version": "2.0.0"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     json_data: Optional[Dict] = None, retries: int = 0) -> Optional[Dict]:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(url, json=json_data, params=params, timeout=config.REQUEST_TIMEOUT)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.text else {}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and retries < config.MAX_RETRIES:
                wait_time = config.RETRY_DELAY ** (retries + 1)
                logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                return self._make_request(method, endpoint, params, json_data, retries + 1)

            logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if retries < config.MAX_RETRIES:
                logger.info(f"Retrying... (attempt {retries + 1}/{config.MAX_RETRIES})")
                time.sleep(config.RETRY_DELAY)
                return self._make_request(method, endpoint, params, json_data, retries + 1)
            return None

    def search_people(self, keywords: Optional[str] = None, company: Optional[str] = None,
                     location: Optional[str] = None, industry: Optional[str] = None,
                     max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for people using LinkedIn API v2 Lite Profile API."""

        results = []
        start = 0
        count = min(10, max_results)

        while len(results) < max_results:
            params = {
                "start": start,
                "count": count
            }

            search_query = []
            if keywords:
                search_query.append(f'keywords:"{keywords}"')
            if company:
                search_query.append(f'companies:"{company}"')
            if location:
                search_query.append(f'geoUrn:"geo_{location}"')

            if search_query:
                params["query"] = " AND ".join(search_query)
            else:
                logger.warning("No search criteria provided")
                break

            logger.info(f"Searching with params: {params}")
            response = self._make_request("GET", "/search/queries/people", params=params)

            if not response or "elements" not in response:
                logger.warning("No results found or API error occurred")
                break

            for element in response.get("elements", []):
                if len(results) >= max_results:
                    break

                profile_data = self._extract_profile_data(element)
                if profile_data:
                    results.append(profile_data)

            if len(response.get("elements", [])) < count:
                break

            start += count

        logger.info(f"Total results collected: {len(results)}")
        return results

    def _extract_profile_data(self, element: Dict) -> Optional[Dict[str, Any]]:
        """Extract relevant profile data from API response."""
        try:
            entity = element.get("entity", {})
            profile = entity.get("*", {})

            name = self._get_nested_value(profile, ["localizedFirstName"]) + " " + \
                   self._get_nested_value(profile, ["localizedLastName"])

            profile_url = f"https://www.linkedin.com/in/{self._get_nested_value(profile, ['publicIdentifier'])}"

            position = self._get_nested_value(profile, ["position", 0, "title"])
            company = self._get_nested_value(profile, ["position", 0, "companyName"])
            location = self._get_nested_value(profile, ["geoLocation", "city"])
            email = self._get_nested_value(profile, ["email"])
            phone = self._get_nested_value(profile, ["phoneNumber"])

            return {
                "name": name.strip(),
                "linkedin_url": profile_url,
                "email": email or "N/A",
                "phone": phone or "N/A",
                "job_title": position or "N/A",
                "company": company or "N/A",
                "location": location or "N/A"
            }

        except Exception as e:
            logger.warning(f"Failed to extract profile data: {str(e)}")
            return None

    @staticmethod
    def _get_nested_value(d: Dict, keys: List[str], default: str = "") -> str:
        """Safely get nested dictionary value."""
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key, {})
            elif isinstance(d, list):
                try:
                    d = d[int(key)] if isinstance(key, int) or key.isdigit() else d.get(key, {})
                except (IndexError, TypeError):
                    return default
            else:
                return default
        return str(d) if d else default

    def verify_connection(self) -> bool:
        """Verify API connection and authentication."""
        try:
            response = self._make_request("GET", "/me")
            if response and "id" in response:
                logger.info(f"Successfully authenticated as: {response.get('id')}")
                return True
            return False
        except Exception as e:
            logger.error(f"Authentication verification failed: {str(e)}")
            return False
