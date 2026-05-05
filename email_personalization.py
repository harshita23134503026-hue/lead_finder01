import logging
import random
from typing import Dict, Any, List, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailPersonalization:
    """Generate personalized emails based on lead profile."""

    def __init__(self):
        self.greeting_templates = [
            "Hi {first_name},",
            "Hello {first_name},",
            "Hey {first_name},",
            "Hi there {first_name},"
        ]

        self.opening_templates = {
            "Manager": [
                "I noticed you're leading the team at {company}.",
                "Your leadership at {company} caught my attention.",
                "I saw your profile and your work at {company} is impressive."
            ],
            "Video Editor": [
                "Your work in video editing is impressive.",
                "I noticed your expertise in {job_title}.",
                "Your portfolio at {company} shows great video work."
            ],
            "Freelancer": [
                "Your freelance work caught my attention.",
                "I'm impressed by your independent projects.",
                "Your freelance portfolio is excellent."
            ],
            "Developer": [
                "Your development expertise is impressive.",
                "I saw your technical background.",
                "Your coding experience at {company} is notable."
            ],
            "Default": [
                "I came across your profile and was impressed.",
                "Your background seems like a great fit.",
                "I think you might be interested in an opportunity."
            ]
        }

        self.cta_templates = {
            "quick_call": "Would you be open to a quick 15-minute call this week?",
            "call_next_week": "Are you available for a brief call next week?",
            "email_back": "Could you reply if you're interested in learning more?",
            "linkedin_message": "Feel free to reach out via LinkedIn if this interests you.",
            "direct_response": "If this resonates with you, please let me know!"
        }

        self.closing_templates = [
            "Looking forward to connecting!",
            "Thanks for your time!",
            "Hope to hear from you soon!",
            "Best regards!",
            "Cheers!"
        ]

    def extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name."""
        if not full_name or full_name == "N/A":
            return "there"
        names = full_name.split()
        return names[0] if names else "there"

    def identify_job_category(self, job_title: str) -> str:
        """Identify job category for template selection."""
        if not job_title or job_title == "N/A":
            return "Default"

        job_lower = job_title.lower()

        categories = {
            "Manager": ["manager", "director", "lead", "head", "ceo", "vp"],
            "Video Editor": ["video editor", "editor", "motion", "colorist"],
            "Freelancer": ["freelancer", "contractor", "independent", "founder"],
            "Developer": ["developer", "engineer", "programmer", "architect"]
        }

        for category, keywords in categories.items():
            if any(keyword in job_lower for keyword in keywords):
                return category

        return "Default"

    def generate_subject_lines(self, lead: Dict[str, Any], count: int = 3) -> List[str]:
        """Generate multiple subject line options."""
        subjects = []
        company = lead.get("company", "").replace("Company", "")
        first_name = self.extract_first_name(lead.get("name", ""))

        templates = [
            f"Opportunity for {first_name}",
            f"Quick question regarding your role at {company}",
            f"Potential opportunity - {lead.get('job_title', 'Your Profile')}",
            f"Would love to connect with you, {first_name}",
            f"Interesting possibility for someone with your background",
        ]

        selected = random.sample(templates, min(count, len(templates)))
        logger.debug(f"Generated {len(selected)} subject lines for {lead.get('email')}")
        return selected

    def personalize_email(self, lead: Dict[str, Any], template_body: str = None,
                         campaign_name: str = "") -> Dict[str, str]:
        """Generate personalized email for a lead."""
        try:
            first_name = self.extract_first_name(lead.get("name", ""))
            company = lead.get("company", "")
            job_title = lead.get("job_title", "")
            location = lead.get("location", "")
            job_category = self.identify_job_category(job_title)

            greeting = random.choice(self.greeting_templates).format(first_name=first_name)

            opening = random.choice(self.opening_templates.get(job_category, self.opening_templates["Default"]))
            opening = opening.format(first_name=first_name, company=company, job_title=job_title)

            cta = random.choice(list(self.cta_templates.values()))

            closing = random.choice(self.closing_templates)

            if template_body:
                body = template_body
            else:
                body = f"""
{greeting}

{opening}

I wanted to reach out because I think there might be a great opportunity for you.

{cta}

{closing}
"""

            subject = random.choice(self.generate_subject_lines(lead, 1))[0]

            logger.debug(f"Personalized email for {lead.get('email')}")

            return {
                "subject": subject,
                "body": body.strip(),
                "personalization_level": "high" if all([company != "N/A", job_title != "N/A"]) else "medium"
            }

        except Exception as e:
            logger.warning(f"Error personalizing email: {str(e)}")
            return {
                "subject": f"Opportunity for {first_name}",
                "body": f"Hi {first_name},\n\nI came across your profile and was impressed.\n\nWould you be open to discussing an opportunity?\n\nBest regards!",
                "personalization_level": "low"
            }

    def add_unsubscribe_footer(self, body: str, unsubscribe_url: str = "") -> str:
        """Add unsubscribe footer (legal requirement)."""
        footer = """

---
You're receiving this email because of mutual interest.
If you'd rather not receive emails like this, you can unsubscribe.
This message was sent to a professional address.
"""
        if unsubscribe_url:
            footer = footer.replace("unsubscribe", f'<a href="{unsubscribe_url}">unsubscribe</a>')

        return body + footer

    def validate_personalization(self, personalized_email: Dict[str, str]) -> Tuple[bool, str]:
        """Validate personalized email for quality."""
        subject = personalized_email.get("subject", "")
        body = personalized_email.get("body", "")

        if len(subject) < 5:
            return False, "Subject too short"

        if len(body) < 50:
            return False, "Body too short"

        if body.count("{") > 0 or body.count("}") > 0:
            return False, "Unresolved template variables"

        return True, "Valid"
