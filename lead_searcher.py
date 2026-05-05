import logging
from typing import List, Dict, Any, Optional
from linkedin_client import LinkedInAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadSearcher:
    def __init__(self, api_client: LinkedInAPIClient):
        self.api_client = api_client
        self.leads = []

    def search(self, keywords: Optional[str] = None, company: Optional[str] = None,
              location: Optional[str] = None, industry: Optional[str] = None,
              max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Execute search with given criteria and collect leads.
        """
        logger.info("Starting lead search...")
        logger.info(f"Search criteria - Keywords: {keywords}, Company: {company}, Location: {location}, Industry: {industry}")

        try:
            results = self.api_client.search_people(
                keywords=keywords,
                company=company,
                location=location,
                industry=industry,
                max_results=max_results
            )

            self.leads = self._deduplicate(results)
            logger.info(f"Found {len(self.leads)} unique leads after deduplication")
            return self.leads

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def _deduplicate(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate leads based on LinkedIn URL."""
        seen = set()
        unique_leads = []

        for lead in leads:
            url = lead.get("linkedin_url")
            if url and url not in seen:
                seen.add(url)
                unique_leads.append(lead)
            elif url:
                logger.debug(f"Duplicate found: {url}")

        return unique_leads

    def get_leads(self) -> List[Dict[str, Any]]:
        """Get currently collected leads."""
        return self.leads

    def clear_leads(self):
        """Clear current leads."""
        self.leads = []
        logger.info("Leads cleared")
