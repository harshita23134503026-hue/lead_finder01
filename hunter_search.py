#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import Optional
import config
from hunter_client import HunterAPIClient
from hunter_searcher import HunterLeadSearcher
from data_processor import HunterDataProcessor
from csv_exporter import CSVExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_api_key(api_key: str) -> bool:
    """Validate that API key is provided and not empty."""
    return bool(api_key and api_key.strip())


def run_search(domain: Optional[str] = None, company: Optional[str] = None,
              first_name: Optional[str] = None, last_name: Optional[str] = None,
              verify: bool = False, extract_urls: Optional[list] = None,
              max_results: int = 50, output_file: Optional[str] = None) -> bool:
    """Execute complete Hunter.io search workflow."""

    if not validate_api_key(config.HUNTER_API_KEY):
        logger.error("ERROR: HUNTER_API_KEY not set in environment variables")
        logger.error("Please set your API key:")
        logger.error("  1. Create a .env file with: HUNTER_API_KEY=your_api_key_here")
        logger.error("  2. Or set environment variable: export HUNTER_API_KEY=your_api_key_here")
        return False

    try:
        logger.info("=" * 60)
        logger.info("Hunter.io Lead Finder - Starting Search")
        logger.info("=" * 60)

        client = HunterAPIClient(config.HUNTER_API_KEY)

        if not client.verify_connection():
            logger.error("Failed to authenticate with Hunter.io API")
            return False

        logger.info("Authentication successful!")

        searcher = HunterLeadSearcher(client)
        leads = searcher.search(
            domain=domain,
            company=company,
            email=last_name,
            first_name=first_name,
            last_name=last_name,
            verify=verify,
            extract_urls=extract_urls,
            max_results=max_results
        )

        if not leads:
            logger.warning("No leads found matching your criteria")
            return False

        logger.info(f"Collected {len(leads)} leads from Hunter.io")

        processed_leads = HunterDataProcessor.clean_and_normalize(leads)

        if not processed_leads:
            logger.warning("No leads remaining after data processing")
            return False

        logger.info(f"Proceeding with {len(processed_leads)} validated leads")

        output_path = CSVExporter.export(processed_leads, output_file, csv_headers=config.CSV_HEADERS_HUNTER)

        stats = CSVExporter.get_file_stats(output_path)
        logger.info("=" * 60)
        logger.info("Search Complete - Summary:")
        logger.info(f"  Total leads exported: {stats.get('total_leads', 0)}")
        logger.info(f"  Unique companies: {stats.get('unique_companies', 0)}")
        logger.info(f"  Emails found: {stats.get('emails_available', 0)}")
        logger.info(f"  Phones found: {stats.get('phones_available', 0)}")
        logger.info(f"  File size: {stats.get('file_size_kb', 0)} KB")
        logger.info(f"  Saved to: {output_path}")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"Search workflow failed: {str(e)}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Hunter.io Lead Finder - Automated lead collection tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hunter_search.py --domain "apple.com" --limit 50
  python hunter_search.py --domain "google.com" --verify
  python hunter_search.py --first-name "John" --last-name "Doe" --domain "company.com"
  python hunter_search.py --company "Apple" --limit 100
        """
    )

    parser.add_argument(
        "--domain",
        type=str,
        help='Company domain to search (e.g., "apple.com", "google.com")'
    )
    parser.add_argument(
        "--company",
        type=str,
        help='Company name to search (auto-converts to domain)'
    )
    parser.add_argument(
        "--first-name",
        type=str,
        help='First name for email finder'
    )
    parser.add_argument(
        "--last-name",
        type=str,
        help='Last name for email finder'
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        default=False,
        help='Verify email deliverability'
    )
    parser.add_argument(
        "--extract-urls",
        nargs="+",
        help='URLs to extract emails from'
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of leads to collect (default: 50)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help='Output CSV filename (default: auto-generated with timestamp)'
    )

    args = parser.parse_args()

    if not any([args.domain, args.company, args.first_name, args.extract_urls]):
        parser.print_help()
        logger.error("\nERROR: Please provide at least one search criterion")
        sys.exit(1)

    success = run_search(
        domain=args.domain,
        company=args.company,
        first_name=args.first_name,
        last_name=args.last_name,
        verify=args.verify,
        extract_urls=args.extract_urls,
        max_results=args.limit,
        output_file=args.output
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
