import logging
import csv
import uuid
import time
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path
import os

from database_manager import DatabaseManager
from credit_tracker import CreditTracker
from email_agent_manager import EmailAgentManager
from email_sender import HybridEmailSender
from email_personalization import EmailPersonalization
from aiml_engine import LeadQualityScorer
from rate_limiter import HumanBehaviorSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailCampaign:
    """Orchestrate email campaigns with multi-agent sending."""

    def __init__(self, campaign_name: str, db_manager: DatabaseManager = None,
                credit_tracker: CreditTracker = None, agent_manager: EmailAgentManager = None):
        self.campaign_id = str(uuid.uuid4())[:8]
        self.campaign_name = campaign_name
        self.db_manager = db_manager or DatabaseManager()
        self.credit_tracker = credit_tracker or CreditTracker()
        self.agent_manager = agent_manager or EmailAgentManager(self.db_manager)
        self.email_sender = None
        self.personalizer = EmailPersonalization()
        self.quality_scorer = LeadQualityScorer()

        self.leads = []
        self.sent_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.created_at = datetime.now()

        logger.info(f"Created campaign: {campaign_name} (ID: {self.campaign_id})")

    def load_csv(self, csv_file: str, min_quality_score: float = 60.0) -> Tuple[int, int]:
        """
        Load leads from CSV file and filter by quality score.
        Returns (total_loaded, after_filtering)
        """
        if not os.path.isfile(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            return 0, 0

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.leads = list(reader)

            logger.info(f"Loaded {len(self.leads)} leads from CSV")

            filtered_leads = []
            for lead in self.leads:
                if self.db_manager.email_already_sent(lead.get("Email", "")):
                    self.skipped_count += 1
                    logger.debug(f"Skipped already-sent email: {lead.get('Email')}")
                    continue

                quality_score = self.quality_scorer.score_lead({
                    "job_title": lead.get("Job Title", ""),
                    "company": lead.get("Company", ""),
                    "industry": lead.get("Industry", ""),
                    "email": lead.get("Email", ""),
                    "phone": lead.get("Phone", ""),
                    "location": lead.get("Location", "")
                })

                if quality_score >= min_quality_score:
                    lead["quality_score"] = quality_score
                    filtered_leads.append(lead)

            self.leads = filtered_leads
            logger.info(f"Filtered to {len(self.leads)} high-quality leads (min score: {min_quality_score})")

            self.db_manager.create_campaign(self.campaign_id, self.campaign_name, len(self.leads))

            return len(self.leads) + self.skipped_count, len(self.leads)

        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            return 0, 0

    def configure_email_service(self, gmail_config: Dict = None, sendgrid_key: str = None) -> bool:
        """Configure email service (Gmail and/or SendGrid)."""
        try:
            self.email_sender = HybridEmailSender(gmail_config, sendgrid_key)

            if gmail_config:
                if self.email_sender.gmail_sender.validate_credentials():
                    logger.info("Gmail credentials validated")
                    self.agent_manager.add_agent(gmail_config["email"], "gmail")
                else:
                    logger.error("Gmail credentials invalid")

            if sendgrid_key:
                if self.email_sender.sendgrid_sender.validate_credentials():
                    logger.info("SendGrid credentials validated")
                else:
                    logger.error("SendGrid credentials invalid")

            return True

        except Exception as e:
            logger.error(f"Error configuring email service: {str(e)}")
            return False

    def send_campaign_batch(self, batch_size: int = 10, custom_template: str = None) -> Dict[str, Any]:
        """Send emails to leads in batches with agent rotation."""
        if not self.email_sender:
            logger.error("Email service not configured")
            return {"success": False, "message": "Email service not configured"}

        if not self.leads:
            logger.error("No leads loaded")
            return {"success": False, "message": "No leads loaded"}

        if not self.credit_tracker.check_sufficient_credits("email_send_gmail", len(self.leads)):
            logger.error("Insufficient credits for campaign")
            return {"success": False, "message": "Insufficient credits"}

        logger.info(f"Starting campaign send: {self.campaign_name}")
        logger.info(f"Total leads: {len(self.leads)}, Batch size: {batch_size}")

        campaign_results = {
            "campaign_id": self.campaign_id,
            "campaign_name": self.campaign_name,
            "total_leads": len(self.leads),
            "sent": 0,
            "failed": 0,
            "bounced": 0,
            "start_time": datetime.now(),
            "results": []
        }

        for i, lead in enumerate(self.leads):
            try:
                email = lead.get("Email", "")

                if not email or email == "N/A":
                    logger.warning(f"Skipping lead without email")
                    self.skipped_count += 1
                    continue

                agent = self.agent_manager.get_next_agent()
                if not agent:
                    logger.error("No available agents")
                    break

                wait_time = HumanBehaviorSimulator.get_random_delay(5, 15)
                logger.info(f"[{i+1}/{len(self.leads)}] Sending to {email} (wait: {wait_time:.1f}s)")
                time.sleep(wait_time)

                personalized = self.personalizer.personalize_email(lead, custom_template)
                subject = personalized["subject"]
                body = personalized["body"]
                html_body = f"<p>{body.replace(chr(10), '<br>')}</p>"

                success, message, service = self.email_sender.send_email(
                    email, subject, body, html_body
                )

                if success:
                    self.db_manager.log_email_sent(email, self.campaign_id, agent['email_account'], subject)
                    self.agent_manager.record_send(agent['email_account'], True, False)
                    self.credit_tracker.deduct_credits(f"email_send_{service}", 1)

                    campaign_results["sent"] += 1
                    campaign_results["results"].append({
                        "email": email,
                        "status": "sent",
                        "agent": agent['email_account'],
                        "timestamp": datetime.now()
                    })
                    self.sent_count += 1
                else:
                    logger.warning(f"Failed to send to {email}: {message}")

                    fallback_agent = self.agent_manager.rotate_on_failure(agent['email_account'])
                    if fallback_agent:
                        logger.info(f"Retrying with fallback agent: {fallback_agent['email_account']}")
                        success, message, service = self.email_sender.send_email(email, subject, body, html_body)

                        if success:
                            self.db_manager.log_email_sent(email, self.campaign_id, fallback_agent['email_account'], subject)
                            self.credit_tracker.deduct_credits(f"email_send_{service}", 1)
                            campaign_results["sent"] += 1
                            campaign_results["results"].append({
                                "email": email,
                                "status": "sent",
                                "agent": fallback_agent['email_account'],
                                "timestamp": datetime.now()
                            })
                            self.sent_count += 1
                        else:
                            campaign_results["failed"] += 1
                            self.failed_count += 1
                    else:
                        campaign_results["failed"] += 1
                        self.failed_count += 1

            except Exception as e:
                logger.error(f"Error sending to {email}: {str(e)}")
                campaign_results["failed"] += 1
                self.failed_count += 1

        campaign_results["end_time"] = datetime.now()
        campaign_results["duration"] = (campaign_results["end_time"] - campaign_results["start_time"]).total_seconds()

        logger.info("=" * 80)
        logger.info("CAMPAIGN RESULTS")
        logger.info("=" * 80)
        logger.info(f"Campaign: {self.campaign_name} (ID: {self.campaign_id})")
        logger.info(f"Total Leads: {campaign_results['total_leads']}")
        logger.info(f"Successfully Sent: {campaign_results['sent']}")
        logger.info(f"Failed: {campaign_results['failed']}")
        logger.info(f"Duration: {campaign_results['duration']:.1f} seconds")
        logger.info(f"Credit Balance: {self.credit_tracker.get_balance():.2f}")
        logger.info("=" * 80)

        return campaign_results

    def get_campaign_status(self) -> Dict[str, Any]:
        """Get current campaign status."""
        return {
            "campaign_id": self.campaign_id,
            "campaign_name": self.campaign_name,
            "created_at": self.created_at,
            "total_leads": len(self.leads),
            "sent": self.sent_count,
            "failed": self.failed_count,
            "skipped": self.skipped_count,
            "remaining": len(self.leads) - self.sent_count,
            "credit_balance": self.credit_tracker.get_balance()
        }

    def display_status(self):
        """Display campaign status."""
        status = self.get_campaign_status()
        logger.info("=" * 60)
        logger.info("CAMPAIGN STATUS")
        logger.info("=" * 60)
        logger.info(f"Name: {status['campaign_name']}")
        logger.info(f"ID: {status['campaign_id']}")
        logger.info(f"Total Leads: {status['total_leads']}")
        logger.info(f"Sent: {status['sent']} | Failed: {status['failed']} | Remaining: {status['remaining']}")
        logger.info(f"Credits: {status['credit_balance']:.2f}")
        logger.info("=" * 60)
