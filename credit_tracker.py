import logging
from typing import Dict, Any, Optional, Tuple
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CreditTracker:
    def __init__(self, initial_credits: float = 1000.0, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.balance = initial_credits
        self.credit_costs = {
            "linkedin_search": 1.0,
            "email_send_gmail": 0.5,
            "email_send_sendgrid": 1.0,
            "lead_scoring": 0.1,
            "email_personalization": 0.1,
            "send_time_optimization": 0.05,
            "subject_optimization": 0.05
        }
        logger.info(f"Credit tracker initialized with {initial_credits} credits")

    def deduct_credits(self, operation_type: str, count: int = 1) -> bool:
        """Deduct credits for an operation."""
        cost = self.credit_costs.get(operation_type, 0)
        total_cost = cost * count

        if self.balance < total_cost:
            logger.warning(f"Insufficient credits for {operation_type}. Need {total_cost}, have {self.balance}")
            return False

        self.balance -= total_cost
        self.db_manager.deduct_credits(
            operation_type=operation_type,
            credits=total_cost,
            description=f"{operation_type} x{count}",
            current_balance=self.balance
        )
        logger.info(f"Deducted {total_cost} credits for {operation_type}. Balance: {self.balance}")
        return True

    def add_credits(self, amount: float, reason: str = "") -> None:
        """Add credits to balance (for manual top-ups)."""
        self.balance += amount
        logger.info(f"Added {amount} credits. Reason: {reason}. New balance: {self.balance}")

    def get_balance(self) -> float:
        """Get current credit balance."""
        return self.balance

    def get_estimated_operations(self) -> Dict[str, int]:
        """Estimate how many operations can be done with current balance."""
        estimates = {}
        for operation_type, cost in self.credit_costs.items():
            if cost > 0:
                estimates[operation_type] = int(self.balance / cost)
        return estimates

    def check_sufficient_credits(self, operation_type: str, count: int = 1) -> bool:
        """Check if enough credits for operation."""
        cost = self.credit_costs.get(operation_type, 0)
        total_cost = cost * count
        return self.balance >= total_cost

    def get_credit_status(self) -> Dict[str, Any]:
        """Get detailed credit status."""
        estimates = self.get_estimated_operations()
        return {
            "current_balance": self.balance,
            "operations_possible": estimates,
            "low_balance_alert": self.balance < 50,
            "critical_balance_alert": self.balance < 10
        }

    def display_status(self):
        """Display credit status to user."""
        status = self.get_credit_status()
        logger.info("=" * 60)
        logger.info("CREDIT TRACKER STATUS")
        logger.info("=" * 60)
        logger.info(f"Current Balance: {status['current_balance']:.2f} credits")
        logger.info("\nEstimated operations possible:")
        for op, count in status['operations_possible'].items():
            logger.info(f"  - {op}: ~{count} operations")
        if status['low_balance_alert']:
            logger.warning("⚠️  LOW BALANCE ALERT - Consider adding credits!")
        if status['critical_balance_alert']:
            logger.error("🚨 CRITICAL BALANCE - Add credits immediately!")
        logger.info("=" * 60)

    def bulk_deduct(self, operations: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
        """Deduct credits for multiple operations at once."""
        total_cost = 0
        for op_type, count in operations.items():
            cost = self.credit_costs.get(op_type, 0)
            total_cost += cost * count

        if self.balance < total_cost:
            logger.warning(f"Insufficient credits for bulk operation. Need {total_cost}, have {self.balance}")
            return False, {
                "required": total_cost,
                "available": self.balance,
                "deficit": total_cost - self.balance
            }

        for op_type, count in operations.items():
            self.deduct_credits(op_type, count)

        logger.info(f"Bulk deduction completed. Total: {total_cost} credits. Balance: {self.balance}")
        return True, {"total_cost": total_cost, "new_balance": self.balance}
