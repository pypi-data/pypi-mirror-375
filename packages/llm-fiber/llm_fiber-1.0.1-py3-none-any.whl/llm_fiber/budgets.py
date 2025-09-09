"""Cost controls and budgets system for llm-fiber."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from .types import ChatMessage, FiberError, Usage


class BudgetType(Enum):
    """Types of budget constraints."""

    TOKEN_COUNT = "token_count"  # Total tokens consumed
    COST_USD = "cost_usd"  # Total cost in USD
    REQUEST_COUNT = "request_count"  # Number of requests
    TIME_WINDOW = "time_window"  # Time-based limits


class BudgetPeriod(Enum):
    """Budget reset periods."""

    NONE = "none"  # Never reset
    HOURLY = "hourly"  # Reset every hour
    DAILY = "daily"  # Reset every day
    WEEKLY = "weekly"  # Reset every week
    MONTHLY = "monthly"  # Reset every month


class BudgetError(FiberError):
    """Budget-related errors."""

    def __init__(
        self,
        message: str,
        budget_type: Optional[BudgetType] = None,
        current_usage: Optional[float] = None,
        limit: Optional[float] = None,
    ):
        super().__init__(message)
        self.budget_type = budget_type
        self.current_usage = current_usage
        self.limit = limit


class BudgetExceededError(BudgetError):
    """Error raised when budget is exceeded."""

    pass


class BudgetWarningError(BudgetError):
    """Error raised when approaching budget limit."""

    pass


@dataclass
class BudgetUsage:
    """Current usage statistics for a budget."""

    tokens_used: int = 0
    cost_usd_used: float = 0.0
    requests_made: int = 0
    time_period_start: float = field(default_factory=time.time)
    last_reset: float = field(default_factory=time.time)

    def reset(self) -> None:
        """Reset usage statistics."""
        self.tokens_used = 0
        self.cost_usd_used = 0.0
        self.requests_made = 0
        self.time_period_start = time.time()
        self.last_reset = time.time()


@dataclass
class Budget:
    """Budget constraint definition."""

    name: str
    budget_type: BudgetType
    limit: float
    period: BudgetPeriod = BudgetPeriod.NONE
    warning_threshold: float = 0.8  # Warn at 80% of limit
    hard_limit: bool = True  # Whether to enforce hard limits

    # Current usage tracking
    usage: BudgetUsage = field(default_factory=BudgetUsage)

    def __post_init__(self):
        """Validate budget configuration."""
        if self.limit < 0:
            raise ValueError("Budget limit must be non-negative")
        if not 0 < self.warning_threshold <= 1:
            raise ValueError("Warning threshold must be between 0 and 1")

    def get_current_usage(self) -> float:
        """Get current usage value based on budget type."""
        if self.budget_type == BudgetType.TOKEN_COUNT:
            return float(self.usage.tokens_used)
        elif self.budget_type == BudgetType.COST_USD:
            return self.usage.cost_usd_used
        elif self.budget_type == BudgetType.REQUEST_COUNT:
            return float(self.usage.requests_made)
        elif self.budget_type == BudgetType.TIME_WINDOW:
            return time.time() - self.usage.time_period_start
        else:
            raise ValueError(f"Unknown budget type: {self.budget_type}")

    @property
    def consumed(self) -> float:
        """Get current consumed amount."""
        return self.get_current_usage()

    @consumed.setter
    def consumed(self, value: float) -> None:
        """Set current consumed amount."""
        if value < 0:
            raise ValueError("Consumed amount cannot be negative")

        if self.budget_type == BudgetType.TOKEN_COUNT:
            self.usage.tokens_used = int(value)
        elif self.budget_type == BudgetType.COST_USD:
            self.usage.cost_usd_used = value
        elif self.budget_type == BudgetType.REQUEST_COUNT:
            self.usage.requests_made = int(value)
        else:
            raise ValueError(f"Cannot set consumed for budget type: {self.budget_type}")

    @property
    def remaining(self) -> float:
        """Get remaining budget."""
        return self.get_remaining()

    @property
    def utilization_rate(self) -> float:
        """Get budget utilization rate."""
        return self.get_utilization()

    @property
    def is_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        return self.get_current_usage() > self.limit

    @property
    def is_warning(self) -> bool:
        """Check if we should warn about approaching limit."""
        return self.should_warn()

    @property
    def last_reset(self) -> datetime:
        """Get timestamp of last reset."""
        return datetime.fromtimestamp(self.usage.last_reset)

    @last_reset.setter
    def last_reset(self, value) -> None:
        """Set timestamp of last reset."""
        if hasattr(value, "timestamp"):
            # Handle datetime objects
            self.usage.last_reset = value.timestamp()
        else:
            # Handle raw timestamp values
            self.usage.last_reset = float(value)

    def get_remaining(self) -> float:
        """Get remaining budget."""
        return self.limit - self.get_current_usage()

    def get_utilization(self) -> float:
        """Get budget utilization as a percentage."""
        return self.get_current_usage() / self.limit

    def should_warn(self) -> bool:
        """Check if we should warn about approaching limit."""
        return self.get_utilization() >= self.warning_threshold

    def needs_reset(self) -> bool:
        """Check if budget needs to be reset based on period."""
        if self.period == BudgetPeriod.NONE:
            return False

        current_time = time.time()
        time_since_reset = current_time - self.usage.last_reset

        if self.period == BudgetPeriod.HOURLY:
            return time_since_reset >= 3600
        elif self.period == BudgetPeriod.DAILY:
            return time_since_reset >= 86400
        elif self.period == BudgetPeriod.WEEKLY:
            return time_since_reset >= 604800
        elif self.period == BudgetPeriod.MONTHLY:
            return time_since_reset >= 2592000  # Approximate

        return False

    def can_consume(self, amount: float) -> bool:
        """Check if the given amount can be consumed without exceeding limit."""
        if not self.hard_limit:
            return True  # Soft limits allow consumption

        current = self.get_current_usage()
        return (current + amount) <= self.limit

    def consume(self, amount: float) -> None:
        """Consume the given amount from the budget.

        Args:
            amount: Amount to consume

        Raises:
            BudgetExceededError: If hard limit would be exceeded
            BudgetWarningError: If soft limit warning threshold is reached
        """
        # Allow negative consumption for refund scenarios

        current = self.get_current_usage()
        new_total = current + amount

        # Check hard limits
        if self.hard_limit and new_total > self.limit:
            raise BudgetExceededError(
                f"Budget '{self.name}' would be exceeded: "
                f"requested {amount}, current {current}, limit {self.limit}",
                budget_type=self.budget_type,
                current_usage=current,
                limit=self.limit,
            )

        # Update usage
        if self.budget_type == BudgetType.TOKEN_COUNT:
            self.usage.tokens_used += int(amount)
        elif self.budget_type == BudgetType.COST_USD:
            self.usage.cost_usd_used += amount
        elif self.budget_type == BudgetType.REQUEST_COUNT:
            self.usage.requests_made += int(amount)
        else:
            raise ValueError(f"Cannot consume for budget type: {self.budget_type}")

        # Check for warnings on soft limits
        if not self.hard_limit and self.should_warn():
            import warnings

            warnings.warn(
                f"Budget '{self.name}' approaching limit: "
                f"{self.get_current_usage():.2f} / {self.limit} "
                f"({self.get_utilization() * 100:.1f}%)",
                UserWarning,
            )

    def reset(self) -> None:
        """Reset the budget usage."""
        self.usage.reset()

    def __str__(self) -> str:
        """String representation of the budget."""
        utilization_pct = self.get_utilization() * 100
        return (
            f"Budget '{self.name}': {self.consumed:.1f}/{self.limit:.1f} "
            f"({utilization_pct:.1f}%) [{self.budget_type.value}]"
        )

    def reset_if_needed(self) -> bool:
        """Reset budget if period has elapsed."""
        if self.needs_reset():
            self.usage.reset()
            return True
        return False


class BudgetEstimator:
    """Estimates cost and token usage for budget checking."""

    def __init__(self, model_registry=None):
        self.model_registry = model_registry

    def estimate_tokens(
        self, model: str, messages: List[ChatMessage], max_tokens: Optional[int] = None
    ) -> Dict[str, int]:
        """Estimate token usage for a request."""
        # Rough estimation - in production, use provider-specific tokenizers
        prompt_text = " ".join(msg.content for msg in messages if msg.content)
        prompt_tokens = max(1, len(prompt_text) // 4)  # ~4 chars per token

        # Estimate completion tokens
        completion_tokens = max_tokens or min(4096, prompt_tokens)  # Conservative estimate

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

    def estimate_cost(self, model: str, token_estimate: Dict[str, int]) -> Optional[float]:
        """Estimate cost for a request."""
        if not self.model_registry:
            return None

        return self.model_registry.estimate_cost(
            model=model,
            prompt_tokens=token_estimate["prompt_tokens"],
            completion_tokens=token_estimate["completion_tokens"],
        )

    def estimate_request_cost(
        self, model: str, messages: List[ChatMessage], max_tokens: Optional[int] = None
    ) -> Dict[str, Union[int, float, None]]:
        """Estimate full cost for a request."""
        token_estimate = self.estimate_tokens(model, messages, max_tokens)
        cost_estimate = self.estimate_cost(model, token_estimate)

        return {
            "tokens": token_estimate["total_tokens"],
            "cost_usd": cost_estimate,
            "prompt_tokens": token_estimate["prompt_tokens"],
            "completion_tokens": token_estimate["completion_tokens"],
        }


class BudgetManager:
    """Manages multiple budgets and enforces limits."""

    def __init__(self, budgets: Optional[List[Budget]] = None, model_registry=None):
        self.budgets: Dict[str, Budget] = {}
        self.estimator = BudgetEstimator(model_registry)

        if budgets:
            for budget in budgets:
                self.add_budget(budget)

    def add_budget(self, budget: Budget) -> None:
        """Add a budget constraint."""
        if budget.name in self.budgets:
            raise ValueError(f"Budget with name '{budget.name}' already exists")
        self.budgets[budget.name] = budget

    def remove_budget(self, name: str) -> None:
        """Remove a budget constraint."""
        self.budgets.pop(name, None)

    def get_budget(self, name: str) -> Optional[Budget]:
        """Get a budget by name."""
        return self.budgets.get(name)

    def list_budgets(self) -> List[str]:
        """List all budget names."""
        return list(self.budgets.keys())

    def get_all_budgets(self):
        """Get all budgets."""
        return self.budgets.values()

    def check_preflight(self, usage: Usage) -> None:
        """Check if usage would exceed any budgets before execution.

        Args:
            usage: Usage to check against budgets

        Raises:
            BudgetExceededError: If usage would exceed hard limits
        """
        import warnings

        # Reset budgets that need it
        for budget in self.budgets.values():
            budget.reset_if_needed()

        exceeded = []
        warnings_list = []

        for budget in self.budgets.values():
            # Determine what to consume based on budget type
            if budget.budget_type == BudgetType.TOKEN_COUNT:
                amount = usage.total
            elif budget.budget_type == BudgetType.COST_USD:
                if usage.cost_estimate is None:
                    continue  # Skip if we can't estimate cost
                amount = usage.cost_estimate
            elif budget.budget_type == BudgetType.REQUEST_COUNT:
                amount = 1
            else:
                continue

            # Check if would exceed hard limit
            if budget.hard_limit and not budget.can_consume(amount):
                exceeded.append(budget)
            # Check if would trigger warning (but allow soft limits)
            elif not budget.hard_limit and budget.consumed + amount >= (
                budget.limit * budget.warning_threshold
            ):
                warnings_list.append(budget)

        # Raise errors if needed
        if exceeded:
            budget = exceeded[0]  # Report first exceeded budget
            raise BudgetExceededError(
                f"Request would exceed {budget.budget_type.value} budget '{budget.name}': "
                f"current {budget.consumed} + {amount} would exceed limit {budget.limit}",
                budget_type=budget.budget_type,
                current_usage=budget.consumed,
                limit=budget.limit,
            )

        # Issue warnings for soft limits
        for budget in warnings_list:
            warnings.warn(
                f"Request approaching {budget.budget_type.value} budget '{budget.name}': "
                f"{budget.utilization_rate:.1%} of {budget.limit} used",
                UserWarning,
            )

    def track_usage(self, usage: Usage) -> None:
        """Track actual usage against budgets.

        Args:
            usage: Usage statistics to record
        """
        for budget in self.budgets.values():
            if budget.budget_type == BudgetType.TOKEN_COUNT:
                budget.consume(usage.total)
            elif budget.budget_type == BudgetType.COST_USD:
                if usage.cost_estimate is not None:
                    budget.consume(usage.cost_estimate)
            elif budget.budget_type == BudgetType.REQUEST_COUNT:
                budget.consume(1)

    def reset_budget(self, name: str) -> bool:
        """Reset a specific budget.

        Args:
            name: Budget name to reset

        Returns:
            True if budget was found and reset, False otherwise
        """
        budget = self.budgets.get(name)
        if budget:
            budget.reset()
            return True
        return False

    def get_warnings(self) -> List[Dict[str, Union[str, float, bool]]]:
        """Get budgets that are in warning state."""
        warnings = []
        for budget in self.budgets.values():
            if budget.is_warning:
                warnings.append(
                    {
                        "budget_name": budget.name,
                        "budget_type": budget.budget_type.value,
                        "limit": budget.limit,
                        "consumed": budget.consumed,
                        "utilization_rate": budget.utilization_rate,
                        "warning_threshold": budget.warning_threshold,
                        "hard_limit": budget.hard_limit,
                    }
                )
        return warnings

    def get_exceeded_budgets(self) -> List[Budget]:
        """Get budgets that are exceeded."""
        return [budget for budget in self.budgets.values() if budget.is_exceeded]

    def reset_expired_budgets(self) -> int:
        """Reset budgets that have expired periods.

        Returns:
            Number of budgets that were reset
        """
        reset_count = 0
        for budget in self.budgets.values():
            if budget.reset_if_needed():
                reset_count += 1
        return reset_count

    def reset_all_budgets(self) -> None:
        """Reset all budget usage."""
        for budget in self.budgets.values():
            budget.usage.reset()

    def check_budgets_preflight(
        self, model: str, messages: List[ChatMessage], max_tokens: Optional[int] = None
    ) -> None:
        """Check if request would exceed any budgets before making it.

        Args:
            model: Model name
            messages: Chat messages
            max_tokens: Maximum tokens to generate

        Raises:
            BudgetExceededError: If request would exceed hard limits
            BudgetWarningError: If request would trigger warnings
        """
        # Reset budgets that need it
        for budget in self.budgets.values():
            budget.reset_if_needed()

        # Get cost estimates
        estimates = self.estimator.estimate_request_cost(model, messages, max_tokens)

        warnings = []
        exceeded = []

        for budget in self.budgets.values():
            # Check current state
            current_usage = budget.consumed

            # Estimate usage after this request
            if budget.budget_type == BudgetType.TOKEN_COUNT:
                estimated_after = current_usage + estimates["tokens"]
            elif budget.budget_type == BudgetType.COST_USD:
                if estimates["cost_usd"] is None:
                    continue  # Skip if we can't estimate cost
                estimated_after = current_usage + estimates["cost_usd"]
            elif budget.budget_type == BudgetType.REQUEST_COUNT:
                estimated_after = current_usage + 1
            elif budget.budget_type == BudgetType.TIME_WINDOW:
                # Time budgets are checked differently
                if budget.is_exceeded():
                    exceeded.append(budget)
                continue
            else:
                continue

            # Check if would exceed hard limit
            if budget.hard_limit and estimated_after >= budget.limit:
                exceeded.append(budget)
            # Check if would trigger warning
            elif estimated_after >= (budget.limit * budget.warning_threshold):
                warnings.append(budget)

        # Raise errors if needed
        if exceeded:
            budget = exceeded[0]  # Report first exceeded budget
            raise BudgetExceededError(
                f"Request would exceed {budget.budget_type.value} budget '{budget.name}': "
                f"estimated {budget.consumed} + request cost would exceed {budget.limit}",
                budget_type=budget.budget_type,
                current_usage=budget.consumed,
                limit=budget.limit,
            )

        if warnings:
            budget = warnings[0]  # Report first warning
            raise BudgetWarningError(
                f"Request approaching {budget.budget_type.value} budget '{budget.name}': "
                f"{budget.utilization_rate:.1%} of {budget.limit} used",
                budget_type=budget.budget_type,
                current_usage=budget.consumed,
                limit=budget.limit,
            )

    def record_usage(self, usage: Usage, model: str) -> None:
        """Record actual usage after a request completes.

        Args:
            usage: Usage statistics from the request
            model: Model that was used
        """
        for budget in self.budgets.values():
            if budget.budget_type == BudgetType.TOKEN_COUNT:
                budget.usage.tokens_used += usage.total
            elif budget.budget_type == BudgetType.COST_USD:
                if usage.cost_estimate:
                    budget.usage.cost_usd_used += usage.cost_estimate
            elif budget.budget_type == BudgetType.REQUEST_COUNT:
                budget.usage.requests_made += 1

    def get_budget_status(self) -> Dict[str, Dict[str, Union[str, float, bool]]]:
        """Get status of all budgets."""
        status = {}

        for name, budget in self.budgets.items():
            budget.reset_if_needed()

            status[name] = {
                "type": budget.budget_type.value,
                "limit": budget.limit,
                "consumed": budget.consumed,
                "remaining": budget.remaining,
                "utilization_rate": budget.utilization_rate,
                "is_exceeded": budget.is_exceeded,
                "should_warn": budget.is_warning,
                "period": budget.period.value,
                "hard_limit": budget.hard_limit,
            }

        return status

    def get_budget_summary(self) -> Dict[str, Union[int, float, List[str]]]:
        """Get high-level budget summary."""
        total_budgets = len(self.budgets)
        exceeded_budgets = [name for name, budget in self.budgets.items() if budget.is_exceeded]
        warning_budgets = [name for name, budget in self.budgets.items() if budget.is_warning]

        return {
            "total_budgets": total_budgets,
            "exceeded_count": len(exceeded_budgets),
            "warning_count": len(warning_budgets),
            "exceeded_budgets": exceeded_budgets,
            "warning_budgets": warning_budgets,
            "overall_status": "exceeded"
            if exceeded_budgets
            else "warning"
            if warning_budgets
            else "healthy",
        }


# Convenience functions for creating common budgets
def create_cost_budget(
    name: str,
    limit_usd: float,
    period: BudgetPeriod = BudgetPeriod.DAILY,
    hard_limit: bool = True,
    warning_threshold: float = 0.8,
) -> Budget:
    """Create a cost-based budget."""
    return Budget(
        name=name,
        budget_type=BudgetType.COST_USD,
        limit=limit_usd,
        period=period,
        hard_limit=hard_limit,
        warning_threshold=warning_threshold,
    )


def create_token_budget(
    name: str,
    limit_tokens: int,
    period: BudgetPeriod = BudgetPeriod.DAILY,
    hard_limit: bool = True,
    warning_threshold: float = 0.8,
) -> Budget:
    """Create a token-based budget."""
    return Budget(
        name=name,
        budget_type=BudgetType.TOKEN_COUNT,
        limit=float(limit_tokens),
        period=period,
        hard_limit=hard_limit,
        warning_threshold=warning_threshold,
    )


def create_request_budget(
    name: str,
    limit_requests: int,
    period: BudgetPeriod = BudgetPeriod.HOURLY,
    hard_limit: bool = True,
    warning_threshold: float = 0.8,
) -> Budget:
    """Create a request count budget."""
    return Budget(
        name=name,
        budget_type=BudgetType.REQUEST_COUNT,
        limit=float(limit_requests),
        period=period,
        hard_limit=hard_limit,
        warning_threshold=warning_threshold,
    )


__all__ = [
    "BudgetType",
    "BudgetPeriod",
    "BudgetError",
    "BudgetExceededError",
    "BudgetWarningError",
    "BudgetUsage",
    "Budget",
    "BudgetEstimator",
    "BudgetManager",
    "create_cost_budget",
    "create_token_budget",
    "create_request_budget",
]
