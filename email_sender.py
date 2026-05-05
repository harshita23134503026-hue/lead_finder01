import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Tuple, Optional, List
from rate_limiter import HumanBehaviorSimulator
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GmailSender:
    """Send emails via Gmail SMTP."""

    def __init__(self, email: str, app_password: str):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.connection = None

    def connect(self) -> bool:
        """Establish SMTP connection."""
        try:
            self.connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.connection.starttls()
            self.connection.login(self.email, self.app_password)
            logger.info(f"Connected to Gmail: {self.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gmail: {str(e)}")
            return False

    def disconnect(self):
        """Close SMTP connection."""
        if self.connection:
            try:
                self.connection.quit()
                logger.debug("Disconnected from Gmail")
            except Exception as e:
                logger.warning(f"Error disconnecting: {str(e)}")

    def send_email(self, to_email: str, subject: str, body: str,
                  html_body: str = "", cc: List[str] = None) -> Tuple[bool, str]:
        """Send email via Gmail."""
        try:
            if not self.connection:
                if not self.connect():
                    return False, "Failed to connect"

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email
            msg["To"] = to_email

            if cc:
                msg["Cc"] = ", ".join(cc)

            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            recipients = [to_email]
            if cc:
                recipients.extend(cc)

            self.connection.sendmail(self.email, recipients, msg.as_string())

            logger.info(f"Email sent via Gmail: {to_email}")
            return True, "Sent successfully"

        except smtplib.SMTPAuthenticationError:
            logger.error(f"Gmail authentication failed for {self.email}")
            return False, "Authentication failed - invalid credentials"

        except smtplib.SMTPServerDisconnected:
            logger.warning("Gmail connection lost, reconnecting...")
            self.connect()
            return False, "Connection lost, retrying"

        except Exception as e:
            logger.error(f"Failed to send via Gmail: {str(e)}")
            return False, str(e)

    def validate_credentials(self) -> bool:
        """Validate Gmail credentials."""
        success = self.connect()
        self.disconnect()
        return success


class SendGridSender:
    """Send emails via SendGrid API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.from_email = "noreply@sendgrid.example.com"

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            self.SendGridAPIClient = SendGridAPIClient
            self.Mail = Mail
            self.client = SendGridAPIClient(api_key)
        except ImportError:
            logger.error("SendGrid library not installed")
            self.client = None

    def send_email(self, to_email: str, subject: str, body: str,
                  html_body: str = "", from_email: str = None) -> Tuple[bool, str]:
        """Send email via SendGrid."""
        try:
            if not self.client:
                return False, "SendGrid not configured"

            from_addr = from_email or self.from_email

            message = self.Mail(
                from_email=from_addr,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body,
                html_content=html_body or body
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent via SendGrid: {to_email}")
                return True, "Sent successfully"
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False, f"SendGrid error: {response.status_code}"

        except Exception as e:
            logger.error(f"Failed to send via SendGrid: {str(e)}")
            return False, str(e)

    def validate_credentials(self) -> bool:
        """Validate SendGrid API key."""
        try:
            if not self.client:
                return False

            test_message = self.Mail(
                from_email="test@example.com",
                to_emails="test@example.com",
                subject="Test",
                plain_text_content="Test"
            )

            response = self.client.send(test_message)
            return response.status_code in [200, 201, 202, 400]

        except Exception as e:
            logger.error(f"SendGrid validation failed: {str(e)}")
            return False


class HybridEmailSender:
    """Send emails using Gmail with SendGrid fallback."""

    def __init__(self, gmail_config: Dict = None, sendgrid_key: str = None):
        self.gmail_sender = None
        self.sendgrid_sender = None

        if gmail_config:
            self.gmail_sender = GmailSender(gmail_config["email"], gmail_config["password"])

        if sendgrid_key:
            self.sendgrid_sender = SendGridSender(sendgrid_key)

        if not self.gmail_sender and not self.sendgrid_sender:
            logger.error("No email service configured!")

    def send_email(self, to_email: str, subject: str, body: str,
                  html_body: str = "") -> Tuple[bool, str, str]:
        """Send email with automatic fallback."""

        if self.gmail_sender:
            success, message = self.gmail_sender.send_email(to_email, subject, body, html_body)
            if success:
                return True, message, "gmail"

            logger.warning("Gmail send failed, attempting SendGrid fallback...")

        if self.sendgrid_sender:
            success, message = self.sendgrid_sender.send_email(to_email, subject, body, html_body)
            if success:
                return True, message, "sendgrid"
            else:
                return False, message, "sendgrid"

        return False, "No email service available", "none"

    def disconnect(self):
        """Disconnect all services."""
        if self.gmail_sender:
            self.gmail_sender.disconnect()

