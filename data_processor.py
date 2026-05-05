import logging
from typing import List, Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    @staticmethod
    def clean_and_normalize(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize lead data."""
        processed_leads = []

        for lead in leads:
            try:
                processed_lead = {
                    "Name": DataProcessor._clean_string(lead.get("name", "Unknown")),
                    "LinkedIn URL": DataProcessor._validate_url(lead.get("linkedin_url", "")),
                    "Email": DataProcessor._clean_email(lead.get("email", "N/A")),
                    "Phone": DataProcessor._clean_phone(lead.get("phone", "N/A")),
                    "Job Title": DataProcessor._clean_string(lead.get("job_title", "N/A")),
                    "Company": DataProcessor._clean_string(lead.get("company", "N/A")),
                    "Location": DataProcessor._clean_string(lead.get("location", "N/A")),
                    "Extraction Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                if processed_lead["Name"] != "Unknown":
                    processed_leads.append(processed_lead)
                    logger.debug(f"Processed lead: {processed_lead['Name']}")
                else:
                    logger.warning("Skipped lead with unknown name")

            except Exception as e:
                logger.warning(f"Failed to process lead: {str(e)}")
                continue

        logger.info(f"Processed {len(processed_leads)} leads")
        return processed_leads

    @staticmethod
    def _clean_string(value: str) -> str:
        """Clean and normalize string values."""
        if not value or value == "N/A":
            return "N/A"

        cleaned = value.strip()
        return cleaned if cleaned else "N/A"

    @staticmethod
    def _clean_email(email: str) -> str:
        """Validate and clean email."""
        if not email or email == "N/A":
            return "N/A"

        email = email.strip().lower()
        if "@" in email and "." in email.split("@")[-1]:
            return email
        return "N/A"

    @staticmethod
    def _clean_phone(phone: str) -> str:
        """Clean and normalize phone number."""
        if not phone or phone == "N/A":
            return "N/A"

        cleaned = "".join(c for c in phone if c.isdigit() or c in "+-() ")
        return cleaned.strip() if cleaned else "N/A"

    @staticmethod
    def _validate_url(url: str) -> str:
        """Validate and return LinkedIn URL."""
        if not url:
            return "N/A"

        url = url.strip()
        if url.startswith("https://www.linkedin.com/in/"):
            return url
        return "N/A"

    @staticmethod
    def validate_lead(lead: Dict[str, Any]) -> bool:
        """Check if lead has minimum required data."""
        return (
            lead.get("Name") not in ["Unknown", "N/A", ""] and
            lead.get("LinkedIn URL") != "N/A"
        )
