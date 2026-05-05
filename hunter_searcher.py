import logging
from typing import List, Dict, Any, Optional
from hunter_client import HunterAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HunterLeadSearcher:
    def __init__(self, api_client: HunterAPIClient):
        self.api_client = api_client
        self.leads = []

    def search(self, domain: Optional[str] = None, company: Optional[str] = None,
              email: Optional[str] = None, first_name: Optional[str] = None,
              last_name: Optional[str] = None, verify: bool = False,
              extract_urls: Optional[List[str]] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Execute search with given criteria and collect leads.
        Supports domain search, email finder, email verifier, and email extraction.
        """
        logger.info("Starting Hunter.io search...")
        logger.info(f"Search criteria - Domain: {domain}, Company: {company}, Email: {email}")

        try:
            results = []

            if domain:
                logger.info(f"Searching domain: {domain}")
                domain_results = self.api_client.search_domain(domain, max_results)
                results.extend(domain_results)

            elif company:
                logger.info(f"Searching company: {company}")
                domain_results = self._search_company_domain(company, max_results)
                results.extend(domain_results)

            if email and domain:
                logger.info(f"Finding email for {first_name} {last_name} at {domain}")
                email_result = self.api_client.email_finder(first_name or "", last_name or "", domain)
                if email_result:
                    results.append(email_result)

            if verify:
                logger.info("Verifying emails...")
                results = self._verify_emails(results)

            if extract_urls:
                logger.info(f"Extracting emails from {len(extract_urls)} URLs")
                for url in extract_urls:
                    extracted = self.api_client.extract_emails(url)
                    results.extend(extracted)

            self.leads = self._deduplicate(results)
            logger.info(f"Found {len(self.leads)} unique leads after deduplication")
            return self.leads

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def _search_company_domain(self, company: str, max_results: int) -> List[Dict[str, Any]]:
        """Convert company name to domain and search."""
        domain = self._extract_domain_from_company(company)
        if domain:
            return self.api_client.search_domain(domain, max_results)
        logger.warning(f"Could not extract domain from company: {company}")
        return []

    def _extract_domain_from_company(self, company: str) -> Optional[str]:
        """Extract domain from company name (simple heuristic)."""
        company_lower = company.lower().replace(" ", "")
        common_tlds = ["com", "io", "net", "org", "co"]

        for tld in common_tlds:
            domain = f"{company_lower}.{tld}"
            logger.info(f"Trying domain: {domain}")
            return domain

        return None

    def _deduplicate(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate leads based on email address."""
        seen = set()
        unique_leads = []

        for lead in leads:
            email = lead.get("email")
            if email and email != "N/A" and email not in seen:
                seen.add(email)
                unique_leads.append(lead)
            elif email and email != "N/A":
                logger.debug(f"Duplicate found: {email}")

        return unique_leads

    def _verify_emails(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify each lead's email and add verification status."""
        verified_leads = []

        for lead in leads:
            email = lead.get("email")
            if email and email != "N/A":
                verification = self.api_client.email_verifier(email)
                if verification:
                    lead.update({
                        "verified": verification.get("valid", False),
                        "deliverable": verification.get("deliverable", False)
                    })
                verified_leads.append(lead)
            else:
                verified_leads.append(lead)

        return verified_leads

    def get_leads(self) -> List[Dict[str, Any]]:
        """Get currently collected leads."""
        return self.leads

    def clear_leads(self):
        """Clear current leads."""
        self.leads = []
        logger.info("Leads cleared")
