import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = "leads/leads_manager.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS email_sent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient_email TEXT NOT NULL UNIQUE,
                    campaign_id TEXT,
                    agent_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    subject TEXT,
                    open_count INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    bounce_reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_account TEXT UNIQUE NOT NULL,
                    service TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    last_used DATETIME,
                    emails_sent_today INTEGER DEFAULT 0,
                    emails_sent_total INTEGER DEFAULT 0,
                    bounce_rate REAL DEFAULT 0.0,
                    ban_reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS api_credits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    credits_used REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    remaining_balance REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_leads INTEGER DEFAULT 0,
                    sent_count INTEGER DEFAULT 0,
                    open_count INTEGER DEFAULT 0,
                    bounce_count INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'draft'
                );

                CREATE TABLE IF NOT EXISTS leads_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    linkedin_url TEXT,
                    quality_score REAL,
                    predicted_response_rate REAL,
                    processing_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_email_sent_recipient ON email_sent(recipient_email);
                CREATE INDEX IF NOT EXISTS idx_email_sent_campaign ON email_sent(campaign_id);
                CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
                CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
                CREATE INDEX IF NOT EXISTS idx_leads_quality_score ON leads_quality(quality_score);
            """)
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
        finally:
            conn.close()

    def email_already_sent(self, email: str) -> bool:
        """Check if email has been sent before."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM email_sent WHERE recipient_email = ?", (email,))
            result = cursor.fetchone()
            return result is not None
        finally:
            conn.close()

    def log_email_sent(self, recipient_email: str, campaign_id: str, agent_used: str,
                      subject: str = "", status: str = "sent") -> bool:
        """Log a sent email to prevent duplicates."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO email_sent (recipient_email, campaign_id, agent_used, subject, status)
                VALUES (?, ?, ?, ?, ?)
            """, (recipient_email, campaign_id, agent_used, subject, status))
            conn.commit()
            logger.debug(f"Logged email sent to {recipient_email}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Email already logged: {recipient_email}")
            return False
        except Exception as e:
            logger.error(f"Failed to log email: {str(e)}")
            return False
        finally:
            conn.close()

    def get_agent(self, email: str) -> Optional[Dict[str, Any]]:
        """Get agent by email."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, email_account, service, status, emails_sent_today, bounce_rate
                FROM agents WHERE email_account = ?
            """, (email,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email_account": row[1],
                    "service": row[2],
                    "status": row[3],
                    "emails_sent_today": row[4],
                    "bounce_rate": row[5]
                }
            return None
        finally:
            conn.close()

    def add_agent(self, email: str, service: str) -> bool:
        """Add new email agent."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO agents (email_account, service, status)
                VALUES (?, ?, 'active')
            """, (email, service))
            conn.commit()
            logger.info(f"Added agent: {email} ({service})")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Agent already exists: {email}")
            return False
        finally:
            conn.close()

    def update_agent_status(self, email: str, status: str, ban_reason: str = "") -> bool:
        """Update agent status (active, banned, cooldown)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE agents SET status = ?, ban_reason = ?, last_used = ?
                WHERE email_account = ?
            """, (status, ban_reason, datetime.now(), email))
            conn.commit()
            logger.info(f"Updated agent {email} status to {status}")
            return True
        finally:
            conn.close()

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get all active agents."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, email_account, service, emails_sent_today, bounce_rate
                FROM agents WHERE status = 'active'
                ORDER BY emails_sent_today ASC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "email_account": row[1],
                    "service": row[2],
                    "emails_sent_today": row[3],
                    "bounce_rate": row[4]
                }
                for row in rows
            ]
        finally:
            conn.close()

    def increment_agent_emails(self, email: str, count: int = 1) -> bool:
        """Increment email count for agent."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE agents
                SET emails_sent_today = emails_sent_today + ?,
                    emails_sent_total = emails_sent_total + ?
                WHERE email_account = ?
            """, (count, count, email))
            conn.commit()
            return True
        finally:
            conn.close()

    def deduct_credits(self, operation_type: str, credits: float, description: str = "",
                      current_balance: float = 0) -> bool:
        """Deduct credits from balance."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO api_credits (operation_type, credits_used, description, remaining_balance)
                VALUES (?, ?, ?, ?)
            """, (operation_type, credits, description, current_balance))
            conn.commit()
            logger.debug(f"Deducted {credits} credits for {operation_type}")
            return True
        finally:
            conn.close()

    def save_lead_quality(self, email: str, linkedin_url: str, quality_score: float,
                         response_rate: float) -> bool:
        """Save lead quality score."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO leads_quality
                (email, linkedin_url, quality_score, predicted_response_rate)
                VALUES (?, ?, ?, ?)
            """, (email, linkedin_url, quality_score, response_rate))
            conn.commit()
            return True
        finally:
            conn.close()

    def get_campaign_stats(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT name, created_at, total_leads, sent_count, open_count, bounce_count
                FROM campaigns WHERE id = ?
            """, (campaign_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "name": row[0],
                    "created_at": row[1],
                    "total_leads": row[2],
                    "sent_count": row[3],
                    "open_count": row[4],
                    "bounce_count": row[5]
                }
            return None
        finally:
            conn.close()

    def create_campaign(self, campaign_id: str, name: str, total_leads: int) -> bool:
        """Create new campaign."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO campaigns (id, name, total_leads, status)
                VALUES (?, ?, ?, 'active')
            """, (campaign_id, name, total_leads))
            conn.commit()
            logger.info(f"Created campaign: {name} (ID: {campaign_id})")
            return True
        finally:
            conn.close()
