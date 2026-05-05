#!/usr/bin/env python3
"""
Campaign Management CLI - Send targeted email campaigns to LinkedIn leads.
"""

import argparse
import sys
import os
import logging
from typing import Optional
from database_manager import DatabaseManager
from credit_tracker import CreditTracker
from email_agent_manager import EmailAgentManager
from email_campaign import EmailCampaign
from lead import run_search

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from environment."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    config = {
        "gmail_email": os.getenv("GMAIL_EMAIL", ""),
        "gmail_password": os.getenv("GMAIL_APP_PASSWORD", ""),
        "sendgrid_key": os.getenv("SENDGRID_API_KEY", ""),
        "initial_credits": float(os.getenv("INITIAL_CREDITS", "1000"))
    }

    return config


def cmd_search_and_export(args):
    """Search for leads and export to CSV."""
    logger.info("Starting lead search...")

    success = run_search(
        keywords=args.keywords,
        company=args.company,
        location=args.location,
        industry=args.industry,
        max_results=args.limit,
        output_file=args.output
    )

    return 0 if success else 1


def cmd_configure_agents(args):
    """Configure email agents."""
    config = load_config()
    db_manager = DatabaseManager()
    agent_manager = EmailAgentManager(db_manager)

    if args.add_gmail:
        if not config["gmail_email"] or not config["gmail_password"]:
            logger.error("Gmail credentials not found in .env")
            return 1

        agent_manager.add_agent(config["gmail_email"], "gmail")
        logger.info(f"Added Gmail agent: {config['gmail_email']}")

    if args.add_sendgrid:
        if not config["sendgrid_key"]:
            logger.error("SendGrid API key not found in .env")
            return 1

        agent_manager.add_agent("sendgrid", "sendgrid")
        logger.info("Added SendGrid agent")

    agent_manager.display_agent_status()
    return 0


def cmd_send_campaign(args):
    """Send email campaign."""
    config = load_config()
    db_manager = DatabaseManager()
    credit_tracker = CreditTracker(config["initial_credits"], db_manager)
    agent_manager = EmailAgentManager(db_manager)

    if not os.path.isfile(args.csv_file):
        logger.error(f"CSV file not found: {args.csv_file}")
        return 1

    credit_tracker.display_status()

    campaign = EmailCampaign(
        campaign_name=args.campaign_name or "Campaign",
        db_manager=db_manager,
        credit_tracker=credit_tracker,
        agent_manager=agent_manager
    )

    gmail_config = None
    if config["gmail_email"] and config["gmail_password"]:
        gmail_config = {
            "email": config["gmail_email"],
            "password": config["gmail_password"]
        }

    if not campaign.configure_email_service(gmail_config, config.get("sendgrid_key")):
        logger.error("Failed to configure email service")
        return 1

    total_loaded, after_filter = campaign.load_csv(args.csv_file, args.min_score)
    logger.info(f"Loaded: {total_loaded} leads, After filtering: {after_filter} leads")

    if after_filter == 0:
        logger.error("No leads to send after filtering")
        return 1

    results = campaign.send_campaign_batch(batch_size=args.batch_size, custom_template=args.template)

    campaign.display_status()

    return 0 if results["sent"] > 0 else 1


def cmd_status(args):
    """Check system status."""
    config = load_config()
    db_manager = DatabaseManager()
    credit_tracker = CreditTracker(config["initial_credits"], db_manager)
    agent_manager = EmailAgentManager(db_manager)

    logger.info("System Status:")
    logger.info("=" * 60)

    credit_tracker.display_status()

    agent_manager.display_agent_status()

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Campaign Manager - Send targeted email campaigns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python campaign_cli.py search --keywords "Manager" --location "USA" --limit 50
  python campaign_cli.py configure --add-gmail
  python campaign_cli.py send --csv leads_2024.csv --campaign "Manager Outreach"
  python campaign_cli.py status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    search_parser = subparsers.add_parser("search", help="Search for leads")
    search_parser.add_argument("--keywords", type=str, help="Search keywords")
    search_parser.add_argument("--company", type=str, help="Company filter")
    search_parser.add_argument("--location", type=str, help="Location filter")
    search_parser.add_argument("--industry", type=str, help="Industry filter")
    search_parser.add_argument("--limit", type=int, default=50, help="Max leads (default: 50)")
    search_parser.add_argument("--output", type=str, help="Output CSV filename")
    search_parser.set_defaults(func=cmd_search_and_export)

    config_parser = subparsers.add_parser("configure", help="Configure email agents")
    config_parser.add_argument("--add-gmail", action="store_true", help="Add Gmail agent")
    config_parser.add_argument("--add-sendgrid", action="store_true", help="Add SendGrid agent")
    config_parser.set_defaults(func=cmd_configure_agents)

    send_parser = subparsers.add_parser("send", help="Send email campaign")
    send_parser.add_argument("--csv", dest="csv_file", required=True, help="CSV file with leads")
    send_parser.add_argument("--campaign", dest="campaign_name", help="Campaign name")
    send_parser.add_argument("--batch-size", type=int, default=10, help="Batch size (default: 10)")
    send_parser.add_argument("--min-score", type=float, default=60.0, help="Min quality score (default: 60)")
    send_parser.add_argument("--template", type=str, help="Custom email template file")
    send_parser.set_defaults(func=cmd_send_campaign)

    status_parser = subparsers.add_parser("status", help="Check system status")
    status_parser.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
