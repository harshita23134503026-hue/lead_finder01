import logging
import time
from typing import Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter to prevent banning."""

    def __init__(self, max_per_hour: int = 60, max_per_day: int = 500):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.agent_buckets = defaultdict(lambda: {"tokens": 0, "last_update": time.time()})
        self.agent_daily = defaultdict(lambda: {"count": 0, "date": datetime.now().date()})

    def add_tokens(self, agent_id: str, rate: int = 60):
        """Add tokens to bucket (60 tokens per hour = 1 per minute)."""
        now = time.time()
        bucket = self.agent_buckets[agent_id]
        time_passed = now - bucket["last_update"]
        tokens_to_add = (time_passed / 3600) * rate
        bucket["tokens"] = min(self.max_per_hour, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now

    def allow_request(self, agent_id: str) -> bool:
        """Check if request is allowed without exceeding rate limit."""
        self.add_tokens(agent_id)

        bucket = self.agent_buckets[agent_id]
        daily = self.agent_daily[agent_id]

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
        else:
            logger.warning(f"Rate limit exceeded for agent {agent_id}")
            return False

        today = datetime.now().date()
        if daily["date"] != today:
            daily["date"] = today
            daily["count"] = 0

        if daily["count"] < self.max_per_day:
            daily["count"] += 1
            return True
        else:
            logger.warning(f"Daily limit exceeded for agent {agent_id}")
            return False

    def get_wait_time(self, agent_id: str) -> float:
        """Get how long to wait before next request (in seconds)."""
        self.add_tokens(agent_id)
        bucket = self.agent_buckets[agent_id]

        if bucket["tokens"] >= 1:
            return 0

        tokens_needed = 1 - bucket["tokens"]
        time_needed = (tokens_needed / self.max_per_hour) * 3600
        return time_needed

    def get_status(self, agent_id: str) -> Dict[str, Any]:
        """Get rate limit status for agent."""
        self.add_tokens(agent_id)
        bucket = self.agent_buckets[agent_id]
        daily = self.agent_daily[agent_id]

        return {
            "agent_id": agent_id,
            "tokens_available": int(bucket["tokens"]),
            "daily_sent": daily["count"],
            "daily_limit": self.max_per_day,
            "can_send": bucket["tokens"] >= 1 and daily["count"] < self.max_per_day,
            "wait_time_seconds": self.get_wait_time(agent_id)
        }


class HumanBehaviorSimulator:
    """Simulate human-like email sending behavior."""

    @staticmethod
    def get_random_delay(min_sec: int = 5, max_sec: int = 15) -> float:
        """Get random delay between sends (human-like)."""
        import random
        return random.uniform(min_sec, max_sec)

    @staticmethod
    def get_optimal_send_time(location: str = "") -> datetime:
        """Get optimal time to send email (based on timezone)."""
        now = datetime.now()

        business_hours = {
            "USA": (9, 17),
            "UK": (9, 17),
            "Europe": (9, 17),
            "Asia": (10, 18)
        }

        hours = business_hours.get(location, (9, 17))

        current_hour = now.hour

        if hours[0] <= current_hour < hours[1]:
            return now

        if current_hour < hours[0]:
            return now.replace(hour=hours[0], minute=0, second=0)
        else:
            next_day = now + timedelta(days=1)
            return next_day.replace(hour=hours[0], minute=0, second=0)

    @staticmethod
    def get_random_user_agent() -> str:
        """Get random user agent for email headers."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
        ]
        import random
        return random.choice(user_agents)

    @staticmethod
    def should_send_now(last_send_time: datetime = None, min_interval_sec: int = 5) -> bool:
        """Check if enough time has passed since last send."""
        if not last_send_time:
            return True

        elapsed = (datetime.now() - last_send_time).total_seconds()
        return elapsed >= min_interval_sec

    @staticmethod
    def get_random_day_time() -> datetime:
        """Get random day/time to send (avoid patterns)."""
        import random
        now = datetime.now()

        random_day_offset = random.randint(0, 2)
        random_hour = random.randint(9, 17)
        random_minute = random.randint(0, 59)

        send_time = now + timedelta(days=random_day_offset)
        send_time = send_time.replace(hour=random_hour, minute=random_minute, second=0)

        return send_time
