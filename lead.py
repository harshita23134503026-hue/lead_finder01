#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import Optional
import config
from linkedin_client import LinkedInAPIClient
from lead_searcher import LeadSearcher
from data_processor import DataProcessor
from csv_exporter import CSVExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_token(token: str) -> bool:
    """Validate that access token is provided and not empty."""
    return bool(token and token.strip())


def run_search(keywords: Optional[str] = None, company: Optional[str] = None,
              location: Optional[str] = None, industry: Optional[str] = None,
              max_results: int = 50, output_file: Optional[str] = None) -> bool:
    """Execute complete lead search workflow."""

    if not validate_token(config.LINKEDIN_ACCESS_TOKEN):
        logger.error("ERROR: LINKEDIN_ACCESS_TOKEN not set in environment variables")
        logger.error("Please set your access token:")
        logger.error("  1. Create a .env file with: LINKEDIN_ACCESS_TOKEN=your_token_here")
        logger.error("  2. Or set environment variable: export LINKEDIN_ACCESS_TOKEN=your_token_here")
        return False

    try:
        logger.info("=" * 60)
        logger.info("LinkedIn Lead Finder - Starting Search")
        logger.info("=" * 60)

        client = LinkedInAPIClient(config.LINKEDIN_ACCESS_TOKEN)

        if not client.verify_connection():
            logger.error("Failed to authenticate with LinkedIn API")
            return False

        logger.info("Authentication successful!")

        searcher = LeadSearcher(client)
        leads = searcher.search(
            keywords=keywords,
            company=company,
            location=location,
            industry=industry,
            max_results=max_results
        )

        if not leads:
            logger.warning("No leads found matching your criteria")
            return False

        logger.info(f"Collected {len(leads)} leads from API")

        processed_leads = DataProcessor.clean_and_normalize(leads)

        if not processed_leads:
            logger.warning("No leads remaining after data processing")
            return False

        logger.info(f"Proceeding with {len(processed_leads)} validated leads")

        output_path = CSVExporter.export(processed_leads, output_file or "")

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
        description="LinkedIn Lead Finder - Automated lead collection tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lead.py --keywords "Manager" --location "USA" --limit 50
  python lead.py --company "Apple" --output apple_leads.csv
  python lead.py --keywords "Video Editor" --location "USA" --industry "Media"
  python lead.py --keywords "Freelancer" --limit 100
        """
    )

    parser.add_argument(
        "--keywords",
        type=str,
        help='Search keywords (e.g., "Manager", "Video Editor", "Freelancer")'
    )
    parser.add_argument(
        "--company",
        type=str,
        help='Filter by company name (e.g., "Apple", "Google")'
    )
    parser.add_argument(
        "--location",
        type=str,
        help='Filter by location (e.g., "USA", "India", "London")'
    )
    parser.add_argument(
        "--industry",
        type=str,
        help='Filter by industry (e.g., "Technology", "Media")'
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

    if not any([args.keywords, args.company, args.location, args.industry]):
        parser.print_help()
        logger.error("\nERROR: Please provide at least one search criterion")
        sys.exit(1)

    success = run_search(
        keywords=args.keywords,
        company=args.company,
        location=args.location,
        industry=args.industry,
        max_results=args.limit,
        output_file=args.output
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
