#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import config
from linkedin_client import LinkedInAPIClient
from lead_searcher import LeadSearcher
from data_processor import DataProcessor
from hunter_client import HunterAPIClient
from hunter_searcher import HunterLeadSearcher
from data_processor import HunterDataProcessor
from csv_exporter import CSVExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_tokens(linkedin_token: str, hunter_key: str) -> bool:
    """Validate that at least one API credential is provided."""
    return bool((linkedin_token and linkedin_token.strip()) or
                (hunter_key and hunter_key.strip()))


def run_linkedin_search(keywords: Optional[str] = None, company: Optional[str] = None,
                       location: Optional[str] = None, industry: Optional[str] = None,
                       max_results: int = 50) -> Tuple[str, list]:
    """Execute LinkedIn search in a separate thread."""
    try:
        if not config.LINKEDIN_ACCESS_TOKEN:
            logger.warning("LinkedIn API token not configured, skipping LinkedIn search")
            return "linkedin", []

        logger.info("=" * 60)
        logger.info("LinkedIn Search - Starting")
        logger.info("=" * 60)

        client = LinkedInAPIClient(config.LINKEDIN_ACCESS_TOKEN)

        if not client.verify_connection():
            logger.error("Failed to authenticate with LinkedIn API")
            return "linkedin", []

        logger.info("LinkedIn authentication successful!")

        searcher = LeadSearcher(client)
        leads = searcher.search(
            keywords=keywords,
            company=company,
            location=location,
            industry=industry,
            max_results=max_results
        )

        if not leads:
            logger.warning("No LinkedIn leads found")
            return "linkedin", []

        logger.info(f"Collected {len(leads)} LinkedIn leads")
        processed_leads = DataProcessor.clean_and_normalize(leads)

        if processed_leads:
            logger.info(f"Proceeding with {len(processed_leads)} validated LinkedIn leads")
            output_path = CSVExporter.export(processed_leads, "linkedin_leads",
                                            csv_headers=config.CSV_HEADERS_LINKEDIN)
            logger.info(f"LinkedIn results saved to: {output_path}")
            return "linkedin", processed_leads

        return "linkedin", []

    except Exception as e:
        logger.error(f"LinkedIn search failed: {str(e)}", exc_info=True)
        return "linkedin", []


def run_hunter_search(domain: Optional[str] = None, company: Optional[str] = None,
                     verify: bool = False, max_results: int = 50) -> Tuple[str, list]:
    """Execute Hunter.io search in a separate thread."""
    try:
        if not config.HUNTER_API_KEY:
            logger.warning("Hunter.io API key not configured, skipping Hunter search")
            return "hunter", []

        logger.info("=" * 60)
        logger.info("Hunter.io Search - Starting")
        logger.info("=" * 60)

        client = HunterAPIClient(config.HUNTER_API_KEY)

        if not client.verify_connection():
            logger.error("Failed to authenticate with Hunter.io API")
            return "hunter", []

        logger.info("Hunter.io authentication successful!")

        searcher = HunterLeadSearcher(client)
        leads = searcher.search(
            domain=domain,
            company=company,
            verify=verify,
            max_results=max_results
        )

        if not leads:
            logger.warning("No Hunter.io leads found")
            return "hunter", []

        logger.info(f"Collected {len(leads)} Hunter.io leads")
        processed_leads = HunterDataProcessor.clean_and_normalize(leads)

        if processed_leads:
            logger.info(f"Proceeding with {len(processed_leads)} validated Hunter.io leads")
            output_path = CSVExporter.export(processed_leads, "hunter_leads",
                                            csv_headers=config.CSV_HEADERS_HUNTER)
            logger.info(f"Hunter.io results saved to: {output_path}")
            return "hunter", processed_leads

        return "hunter", []

    except Exception as e:
        logger.error(f"Hunter.io search failed: {str(e)}", exc_info=True)
        return "hunter", []


def run_dual_search(linkedin_keywords: Optional[str] = None,
                   linkedin_company: Optional[str] = None,
                   linkedin_location: Optional[str] = None,
                   linkedin_industry: Optional[str] = None,
                   hunter_domain: Optional[str] = None,
                   hunter_company: Optional[str] = None,
                   verify: bool = False,
                   max_results: int = 50) -> bool:
    """Execute dual search pipeline with concurrent execution."""

    if not validate_tokens(config.LINKEDIN_ACCESS_TOKEN, config.HUNTER_API_KEY):
        logger.error("ERROR: Neither LinkedIn nor Hunter.io API credentials configured")
        logger.error("Please set at least one API key in your .env file")
        return False

    try:
        logger.info("=" * 60)
        logger.info("Dual Lead Pipeline - Starting Concurrent Search")
        logger.info("=" * 60)

        results = {"linkedin": [], "hunter": []}

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []

            if config.LINKEDIN_ACCESS_TOKEN:
                future_linkedin = executor.submit(
                    run_linkedin_search,
                    linkedin_keywords, linkedin_company, linkedin_location,
                    linkedin_industry, max_results
                )
                futures.append(future_linkedin)

            if config.HUNTER_API_KEY:
                future_hunter = executor.submit(
                    run_hunter_search,
                    hunter_domain, hunter_company, verify, max_results
                )
                futures.append(future_hunter)

            for future in as_completed(futures):
                source, leads = future.result()
                results[source] = leads

        linkedin_leads = results.get("linkedin", [])
        hunter_leads = results.get("hunter", [])

        logger.info("=" * 60)
        logger.info("Pipeline Complete - Summary:")
        logger.info(f"  LinkedIn leads: {len(linkedin_leads)}")
        logger.info(f"  Hunter.io leads: {len(hunter_leads)}")
        logger.info(f"  Total leads: {len(linkedin_leads) + len(hunter_leads)}")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"Dual search pipeline failed: {str(e)}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Dual Lead Pipeline - Search both LinkedIn and Hunter.io simultaneously",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lead_pipeline.py --linkedin-keywords "Manager" --hunter-domain "apple.com"
  python lead_pipeline.py --linkedin-location "USA" --hunter-domain "google.com" --verify
  python lead_pipeline.py --linkedin-company "Apple" --hunter-company "Apple"
        """
    )

    # LinkedIn arguments
    parser.add_argument(
        "--linkedin-keywords",
        type=str,
        help='LinkedIn search keywords'
    )
    parser.add_argument(
        "--linkedin-company",
        type=str,
        help='LinkedIn company filter'
    )
    parser.add_argument(
        "--linkedin-location",
        type=str,
        help='LinkedIn location filter'
    )
    parser.add_argument(
        "--linkedin-industry",
        type=str,
        help='LinkedIn industry filter'
    )

    # Hunter.io arguments
    parser.add_argument(
        "--hunter-domain",
        type=str,
        help='Hunter.io domain to search'
    )
    parser.add_argument(
        "--hunter-company",
        type=str,
        help='Hunter.io company to search'
    )

    # Common arguments
    parser.add_argument(
        "--verify",
        action="store_true",
        default=False,
        help='Verify Hunter.io emails'
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum results per search (default: 50)"
    )

    args = parser.parse_args()

    if not any([args.linkedin_keywords, args.linkedin_company, args.linkedin_location,
               args.linkedin_industry, args.hunter_domain, args.hunter_company]):
        parser.print_help()
        logger.error("\nERROR: Please provide at least one search criterion")
        sys.exit(1)

    success = run_dual_search(
        linkedin_keywords=args.linkedin_keywords,
        linkedin_company=args.linkedin_company,
        linkedin_location=args.linkedin_location,
        linkedin_industry=args.linkedin_industry,
        hunter_domain=args.hunter_domain,
        hunter_company=args.hunter_company,
        verify=args.verify,
        max_results=args.limit
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
