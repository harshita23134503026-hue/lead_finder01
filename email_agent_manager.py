import logging
from typing import List, Dict, Any, Optional, Tuple
from database_manager import DatabaseManager
from rate_limiter import RateLimiter, HumanBehaviorSimulator
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailAgentManager:
    """Manage pool of email agents with rotation, health checks, and failover."""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.rate_limiter = RateLimiter(max_per_hour=50, max_per_day=400)
        self.current_agent_index = 0
        self.agents_cache = []
        self.last_rotation_time = {}
        self.agent_cooldown = 600

    def add_agent(self, email: str, service: str = "gmail") -> bool:
        """Add a new email agent to the pool."""
        success = self.db_manager.add_agent(email, service)
        if success:
            logger.info(f"Added {service} agent: {email}")
            self._refresh_agents_cache()
        return success

    def _refresh_agents_cache(self):
        """Refresh the list of active agents from database."""
        self.agents_cache = self.db_manager.get_active_agents()
        logger.debug(f"Refreshed agents cache: {len(self.agents_cache)} active agents")

    def get_next_agent(self) -> Optional[Dict[str, Any]]:
        """Get next healthy agent in rotation."""
        if not self.agents_cache:
            self._refresh_agents_cache()

        if not self.agents_cache:
            logger.error("No active agents available")
            return None

        max_attempts = len(self.agents_cache)
        attempts = 0

        while attempts < max_attempts:
            agent = self.agents_cache[self.current_agent_index % len(self.agents_cache)]
            self.current_agent_index += 1

            if self._is_agent_healthy(agent):
                logger.debug(f"Selected agent: {agent['email_account']}")
                return agent
            else:
                logger.warning(f"Skipping unhealthy agent: {agent['email_account']}")
                attempts += 1

        logger.error("No healthy agents available in rotation")
        return None

    def _is_agent_healthy(self, agent: Dict[str, Any]) -> bool:
        """Check if agent is healthy for sending."""
        if agent["bounce_rate"] > 0.05:
            logger.warning(f"Agent {agent['email_account']} has high bounce rate: {agent['bounce_rate']:.2%}")
            self._mark_agent_status(agent['email_account'], "banned", "High bounce rate")
            return False

        status = self.rate_limiter.get_status(agent['email_account'])
        if not status["can_send"]:
            logger.warning(f"Agent {agent['email_account']} has exceeded rate limits")
            return False

        last_used = agent.get("last_used")
        if last_used:
            time_since_last = (datetime.now() - datetime.fromisoformat(last_used)).total_seconds()
            if time_since_last < 1:
                logger.debug(f"Agent {agent['email_account']} just used, skipping")
                return False

        return True

    def _mark_agent_status(self, email: str, status: str, reason: str = "") -> bool:
        """Mark agent as banned, cooldown, or active."""
        success = self.db_manager.update_agent_status(email, status, reason)
        self._refresh_agents_cache()
        return success

    def record_send(self, agent_email: str, success: bool = True, bounce: bool = False) -> bool:
        """Record email send for an agent."""
        try:
            self.db_manager.increment_agent_emails(agent_email, 1)

            if bounce:
                agent = self.db_manager.get_agent(agent_email)
                if agent:
                    current_bounces = agent.get("emails_sent_today", 1)
                    new_bounce_rate = 1 / max(1, agent.get("emails_sent_today", 1))

                    if new_bounce_rate > 0.05:
                        self._mark_agent_status(agent_email, "banned", "High bounce rate")
                        logger.warning(f"Agent banned due to high bounce rate: {agent_email}")

            logger.debug(f"Recorded send for agent: {agent_email}")
            return True

        except Exception as e:
            logger.error(f"Error recording send: {str(e)}")
            return False

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get stats for all agents."""
        self._refresh_agents_cache()
        active = len([a for a in self.agents_cache if a.get("status") == "active"])
        total = len(self.agents_cache)

        stats = {
            "total_agents": total,
            "active_agents": active,
            "agents": []
        }

        for agent in self.agents_cache:
            rate_status = self.rate_limiter.get_status(agent['email_account'])
            stats["agents"].append({
                "email": agent['email_account'],
                "service": agent['service'],
                "status": agent['status'],
                "emails_today": agent['emails_sent_today'],
                "bounce_rate": f"{agent['bounce_rate']:.2%}",
                "can_send": rate_status["can_send"],
                "wait_time": f"{rate_status['wait_time_seconds']:.1f}s"
            })

        return stats

    def get_available_agent_count(self) -> int:
        """Get count of currently available agents."""
        self._refresh_agents_cache()
        return len([a for a in self.agents_cache if self._is_agent_healthy(a)])

    def rotate_on_failure(self, failed_agent_email: str) -> Optional[Dict[str, Any]]:
        """Get backup agent if primary fails."""
        logger.warning(f"Rotating away from failed agent: {failed_agent_email}")
        self._mark_agent_status(failed_agent_email, "cooldown", "Temporary failure")

        next_agent = self.get_next_agent()
        if next_agent:
            logger.info(f"Failover to backup agent: {next_agent['email_account']}")
            return next_agent
        else:
            logger.error("No backup agent available")
            return None

    def display_agent_status(self):
        """Display status of all agents."""
        stats = self.get_agent_stats()
        logger.info("=" * 80)
        logger.info("EMAIL AGENT STATUS")
        logger.info("=" * 80)
        logger.info(f"Total Agents: {stats['total_agents']} | Active: {stats['active_agents']}")
        logger.info("-" * 80)

        for agent in stats["agents"]:
            status_icon = "✓" if agent["can_send"] else "✗"
            logger.info(
                f"{status_icon} {agent['email']:40} | {agent['service']:8} | "
                f"Today: {agent['emails_today']:3} | Bounce: {agent['bounce_rate']:6} | "
                f"Wait: {agent['wait_time']:8}"
            )

        logger.info("=" * 80)

    def warmup_agents(self):
        """Warmup agents with small initial sends to establish reputation."""
        logger.info("Starting agent warmup sequence...")
        for agent in self.agents_cache:
            if agent['emails_sent_total'] == 0:
                logger.info(f"Agent {agent['email_account']} is new - should warmup gradually")
