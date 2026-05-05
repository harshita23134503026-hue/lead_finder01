import requests
import logging
import time
from typing import Dict, List, Optional, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HunterAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = config.HUNTER_API_BASE_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     json_data: Optional[Dict] = None, retries: int = 0) -> Optional[Dict]:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"

        # Add API key to params
        if params is None:
            params = {}
        if "domain" not in params:
            params["domain"] = ""
        params["api_key"] = self.api_key

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

    def search_domain(self, domain: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for all emails on a domain."""
        results = []
        limit = min(100, max_results)
        offset = 0

        while len(results) < max_results:
            params = {
                "domain": domain,
                "limit": limit,
                "offset": offset
            }

            logger.info(f"Searching domain: {domain} (offset: {offset})")
            response = self._make_request("GET", "/domain-search", params=params)

            if not response or "data" not in response:
                logger.warning("No results found or API error occurred")
                break

            data = response.get("data", {})
            emails = data.get("emails", [])

            if not emails:
                break

            for email_data in emails:
                if len(results) >= max_results:
                    break
                results.append(self._extract_domain_search_data(email_data, domain))

            if len(emails) < limit:
                break

            offset += limit

        logger.info(f"Total results collected: {len(results)}")
        return results

    def email_finder(self, first_name: str, last_name: str, domain: str) -> Optional[Dict[str, Any]]:
        """Find email for a specific person by name and domain."""
        params = {
            "domain": domain,
            "first_name": first_name,
            "last_name": last_name
        }

        logger.info(f"Finding email for {first_name} {last_name} at {domain}")
        response = self._make_request("GET", "/email-finder", params=params)

        if not response or "data" not in response:
            logger.warning("Email not found or API error occurred")
            return None

        data = response.get("data", {})
        if data:
            return self._extract_email_finder_data(data, domain)
        return None

    def email_verifier(self, email: str) -> Optional[Dict[str, Any]]:
        """Verify if an email address is deliverable."""
        params = {
            "email": email
        }

        logger.info(f"Verifying email: {email}")
        response = self._make_request("GET", "/email-verifier", params=params)

        if not response or "data" not in response:
            logger.warning("Verification failed or API error occurred")
            return None

        data = response.get("data", {})
        return {
            "email": email,
            "valid": data.get("status") == "valid",
            "status": data.get("status", "unknown"),
            "deliverable": data.get("deliverable", False),
            "smtp_server": data.get("smtp_server", "N/A"),
            "result": data.get("result", "N/A")
        }

    def extract_emails(self, url: str) -> List[Dict[str, Any]]:
        """Extract emails from a website URL."""
        params = {
            "url": url
        }

        logger.info(f"Extracting emails from: {url}")
        response = self._make_request("GET", "/email-extractor", params=params)

        if not response or "data" not in response:
            logger.warning("No emails extracted or API error occurred")
            return []

        data = response.get("data", {})
        emails = data.get("emails", [])

        results = []
        for email in emails:
            results.append({
                "email": email,
                "url": url,
                "type": "extracted"
            })

        logger.info(f"Extracted {len(results)} emails from {url}")
        return results

    def _extract_domain_search_data(self, email_data: Dict, domain: str) -> Dict[str, Any]:
        """Extract relevant data from domain search response."""
        try:
            return {
                "name": f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                "email": email_data.get("value", "N/A"),
                "domain": domain,
                "confidence": email_data.get("confidence", 0),
                "phone": email_data.get("phone", "N/A"),
                "job_title": email_data.get("position", "N/A"),
                "company": email_data.get("company", "N/A"),
                "location": email_data.get("city", "N/A")
            }
        except Exception as e:
            logger.warning(f"Failed to extract domain search data: {str(e)}")
            return {}

    def _extract_email_finder_data(self, data: Dict, domain: str) -> Dict[str, Any]:
        """Extract relevant data from email finder response."""
        try:
            return {
                "name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
                "email": data.get("email", "N/A"),
                "domain": domain,
                "confidence": data.get("confidence", 0),
                "phone": data.get("phone", "N/A"),
                "job_title": data.get("position", "N/A"),
                "company": data.get("company", "N/A"),
                "location": data.get("city", "N/A")
            }
        except Exception as e:
            logger.warning(f"Failed to extract email finder data: {str(e)}")
            return {}

    def verify_connection(self) -> bool:
        """Verify API connection and authentication."""
        try:
            params = {"domain": "hunter.io"}
            response = self._make_request("GET", "/domain-search", params=params)
            if response and "data" in response:
                logger.info("Successfully authenticated with Hunter.io API")
                return True
            return False
        except Exception as e:
            logger.error(f"Authentication verification failed: {str(e)}")
            return False
