"""Unit tests for budgets and cost control functionality."""

import time
from datetime import datetime, timedelta

import pytest

from llm_fiber.budgets import (
    Budget,
    BudgetExceededError,
    BudgetManager,
    BudgetPeriod,
    BudgetType,
    create_cost_budget,
    create_request_budget,
    create_token_budget,
)
from llm_fiber.types import Usage


class TestBudgetType:
    """Test BudgetType enum functionality."""

    def test_budget_type_values(self):
        """Test budget type enum values."""
        assert BudgetType.TOKEN_COUNT.value == "token_count"
        assert BudgetType.COST_USD.value == "cost_usd"
        assert BudgetType.REQUEST_COUNT.value == "request_count"
        assert BudgetType.TIME_WINDOW.value == "time_window"

    def test_budget_type_from_string(self):
        """Test creating budget type from string."""
        assert BudgetType("token_count") == BudgetType.TOKEN_COUNT
        assert BudgetType("cost_usd") == BudgetType.COST_USD
        assert BudgetType("request_count") == BudgetType.REQUEST_COUNT
        assert BudgetType("time_window") == BudgetType.TIME_WINDOW


class TestBudgetPeriod:
    """Test BudgetPeriod enum functionality."""

    def test_budget_period_values(self):
        """Test budget period enum values."""
        assert BudgetPeriod.HOURLY.value == "hourly"
        assert BudgetPeriod.DAILY.value == "daily"
        assert BudgetPeriod.WEEKLY.value == "weekly"
        assert BudgetPeriod.MONTHLY.value == "monthly"

    def test_budget_period_from_string(self):
        """Test creating budget period from string."""
        assert BudgetPeriod("hourly") == BudgetPeriod.HOURLY
        assert BudgetPeriod("daily") == BudgetPeriod.DAILY
        assert BudgetPeriod("weekly") == BudgetPeriod.WEEKLY
        assert BudgetPeriod("monthly") == BudgetPeriod.MONTHLY


class TestBudget:
    """Test Budget functionality."""

    def test_budget_creation_basic(self):
        """Test basic budget creation."""
        budget = Budget(
            name="test_budget",
            budget_type=BudgetType.COST_USD,
            limit=10.0,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        assert budget.name == "test_budget"
        assert budget.budget_type == BudgetType.COST_USD
        assert budget.limit == 10.0
        assert budget.period == BudgetPeriod.DAILY
        assert budget.hard_limit is True
        assert budget.consumed == 0.0
        assert budget.warning_threshold == 0.8  # Default 80%

    def test_budget_creation_with_warning_threshold(self):
        """Test budget creation with custom warning threshold."""
        budget = Budget(
            name="warn_budget",
            budget_type=BudgetType.TOKEN_COUNT,
            limit=1000,
            period=BudgetPeriod.HOURLY,
            hard_limit=False,
            warning_threshold=0.9,
        )

        assert budget.warning_threshold == 0.9
        assert budget.hard_limit is False

    def test_budget_remaining(self):
        """Test budget remaining calculation."""
        budget = Budget(
            name="remaining_test",
            budget_type=BudgetType.COST_USD,
            limit=10.0,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        assert budget.remaining == 10.0

        budget.consumed = 3.5
        assert budget.remaining == 6.5

        budget.consumed = 10.0
        assert budget.remaining == 0.0

        budget.consumed = 12.0
        assert budget.remaining == -2.0

    def test_budget_utilization_rate(self):
        """Test budget utilization rate calculation."""
        budget = Budget(
            name="util_test",
            budget_type=BudgetType.TOKEN_COUNT,
            limit=1000,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        assert budget.utilization_rate == 0.0

        budget.consumed = 250
        assert budget.utilization_rate == 0.25

        budget.consumed = 800
        assert budget.utilization_rate == 0.8

        budget.consumed = 1000
        assert budget.utilization_rate == 1.0

        budget.consumed = 1200
        assert budget.utilization_rate == 1.2

    def test_budget_is_exceeded(self):
        """Test budget exceeded check."""
        budget = Budget(
            name="exceed_test",
            budget_type=BudgetType.COST_USD,
            limit=5.0,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        assert not budget.is_exceeded

        budget.consumed = 3.0
        assert not budget.is_exceeded

        budget.consumed = 5.0
        assert not budget.is_exceeded  # At limit, not exceeded

        budget.consumed = 5.1
        assert budget.is_exceeded

    def test_budget_is_warning(self):
        """Test budget warning check."""
        budget = Budget(
            name="warning_test",
            budget_type=BudgetType.TOKEN_COUNT,
            limit=1000,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
            warning_threshold=0.8,
        )

        assert not budget.is_warning

        budget.consumed = 700
        assert not budget.is_warning

        budget.consumed = 800
        assert budget.is_warning

        budget.consumed = 950
        assert budget.is_warning

    def test_budget_can_consume_success(self):
        """Test budget can_consume check - success cases."""
        budget = Budget(
            name="consume_test",
            budget_type=BudgetType.COST_USD,
            limit=10.0,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        # Can consume within limit
        assert budget.can_consume(5.0)
        assert budget.can_consume(10.0)

        # After partial consumption
        budget.consumed = 6.0
        assert budget.can_consume(4.0)
        assert not budget.can_consume(4.1)

    def test_budget_can_consume_soft_limit(self):
        """Test budget can_consume with soft limit."""
        budget = Budget(
            name="soft_test",
            budget_type=BudgetType.TOKEN_COUNT,
            limit=1000,
            period=BudgetPeriod.DAILY,
            hard_limit=False,  # Soft limit
        )

        # Can consume even beyond limit with soft limit
        assert budget.can_consume(500)
        assert budget.can_consume(1000)
        assert budget.can_consume(1500)  # Beyond limit but soft

    def test_budget_consume_success(self):
        """Test budget consume operation - success."""
        budget = Budget(
            name="consume_op_test",
            budget_type=BudgetType.COST_USD,
            limit=10.0,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        initial_consumed = budget.consumed

        # Consume within limit
        budget.consume(3.5)
        assert budget.consumed == initial_consumed + 3.5

        # Consume more
        budget.consume(2.0)
        assert budget.consumed == initial_consumed + 5.5

    def test_budget_consume_hard_limit_exceeded(self):
        """Test budget consume operation - hard limit exceeded."""
        budget = Budget(
            name="hard_limit_test",
            budget_type=BudgetType.TOKEN_COUNT,
            limit=1000,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        budget.consumed = 900

        # This should succeed
        budget.consume(50)
        assert budget.consumed == 950

        # This should fail
        with pytest.raises(BudgetExceededError) as exc_info:
            budget.consume(100)

        assert budget.name in str(exc_info.value)
        assert budget.consumed == 950  # Should not have changed

    def test_budget_consume_soft_limit_warning(self):
        """Test budget consume operation - soft limit warning."""
        budget = Budget(
            name="soft_limit_test",
            budget_type=BudgetType.COST_USD,
            limit=5.0,
            period=BudgetPeriod.DAILY,
            hard_limit=False,
            warning_threshold=0.8,
        )

        # Consume to warning threshold
        budget.consumed = 3.5  # Below warning

        # This should work without warning
        budget.consume(0.4)  # Total 3.9, still below 4.0 (80%)

        # This should trigger warning but still work
        with pytest.warns(UserWarning) as warning_info:
            budget.consume(1.0)  # Total 4.9, above warning threshold

        assert len(warning_info) > 0
        assert budget.consumed == 4.9

        # Can still consume beyond limit with soft limit
        budget.consume(1.0)  # Total 5.9, beyond limit
        assert budget.consumed == 5.9

    def test_budget_reset(self):
        """Test budget reset functionality."""
        budget = Budget(
            name="reset_test",
            budget_type=BudgetType.REQUEST_COUNT,
            limit=100,
            period=BudgetPeriod.HOURLY,
            hard_limit=True,
        )

        # Consume some budget
        budget.consumed = 45
        budget.last_reset = datetime.now() - timedelta(hours=1)

        original_reset_time = budget.last_reset

        # Reset budget
        budget.reset()

        assert budget.consumed == 0
        assert budget.last_reset > original_reset_time

    def test_budget_needs_reset(self):
        """Test budget needs_reset check."""
        budget = Budget(
            name="reset_check_test",
            budget_type=BudgetType.COST_USD,
            limit=10.0,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        # Fresh budget shouldn't need reset
        assert not budget.needs_reset()

        # Set last reset to yesterday
        budget.last_reset = datetime.now() - timedelta(days=1, hours=1)
        assert budget.needs_reset()

        # Different periods
        budget.period = BudgetPeriod.HOURLY
        budget.last_reset = datetime.now() - timedelta(hours=1, minutes=1)
        assert budget.needs_reset()

        budget.period = BudgetPeriod.WEEKLY
        budget.last_reset = datetime.now() - timedelta(days=7, hours=1)
        assert budget.needs_reset()

        budget.period = BudgetPeriod.MONTHLY
        budget.last_reset = datetime.now() - timedelta(days=31)
        assert budget.needs_reset()

    def test_budget_str_representation(self):
        """Test budget string representation."""
        budget = Budget(
            name="str_test",
            budget_type=BudgetType.COST_USD,
            limit=10.0,
            period=BudgetPeriod.DAILY,
            hard_limit=True,
        )

        budget.consumed = 3.5

        str_repr = str(budget)
        assert "str_test" in str_repr
        assert "3.5" in str_repr
        assert "10.0" in str_repr
        assert "35.0%" in str_repr  # Utilization


class TestBudgetHelpers:
    """Test budget creation helper functions."""

    def test_create_cost_budget_basic(self):
        """Test creating cost budget with helper."""
        budget = create_cost_budget(
            name="api_costs", limit_usd=25.0, period=BudgetPeriod.DAILY, hard_limit=True
        )

        assert budget.name == "api_costs"
        assert budget.budget_type == BudgetType.COST_USD
        assert budget.limit == 25.0
        assert budget.period == BudgetPeriod.DAILY
        assert budget.hard_limit is True

    def test_create_cost_budget_with_warning(self):
        """Test creating cost budget with warning threshold."""
        budget = create_cost_budget(
            name="api_costs_warn",
            limit_usd=50.0,
            period=BudgetPeriod.WEEKLY,
            hard_limit=False,
            warning_threshold=0.9,
        )

        assert budget.budget_type == BudgetType.COST_USD
        assert budget.limit == 50.0
        assert budget.warning_threshold == 0.9
        assert budget.hard_limit is False

    def test_create_token_budget_basic(self):
        """Test creating token budget with helper."""
        budget = create_token_budget(
            name="token_limit", limit_tokens=10000, period=BudgetPeriod.HOURLY, hard_limit=True
        )

        assert budget.name == "token_limit"
        assert budget.budget_type == BudgetType.TOKEN_COUNT
        assert budget.limit == 10000
        assert budget.period == BudgetPeriod.HOURLY
        assert budget.hard_limit is True

    def test_create_request_budget_basic(self):
        """Test creating request budget with helper."""
        budget = create_request_budget(
            name="request_limit", limit_requests=1000, period=BudgetPeriod.DAILY, hard_limit=False
        )

        assert budget.name == "request_limit"
        assert budget.budget_type == BudgetType.REQUEST_COUNT
        assert budget.limit == 1000
        assert budget.period == BudgetPeriod.DAILY
        assert budget.hard_limit is False


class TestBudgetManager:
    """Test BudgetManager functionality."""

    @pytest.fixture
    def sample_budgets(self):
        """Create sample budgets for testing."""
        return [
            create_cost_budget("daily_cost", 10.0, BudgetPeriod.DAILY, hard_limit=True),
            create_token_budget("hourly_tokens", 5000, BudgetPeriod.HOURLY, hard_limit=True),
            create_request_budget("daily_requests", 100, BudgetPeriod.DAILY, hard_limit=False),
        ]

    @pytest.fixture
    def budget_manager(self, sample_budgets):
        """Create budget manager with sample budgets."""
        return BudgetManager(sample_budgets)

    def test_budget_manager_creation_empty(self):
        """Test creating empty budget manager."""
        manager = BudgetManager()
        assert len(manager.budgets) == 0
        assert list(manager.get_all_budgets()) == []

    def test_budget_manager_creation_with_budgets(self, budget_manager, sample_budgets):
        """Test creating budget manager with budgets."""
        assert len(budget_manager.budgets) == 3

        all_budgets = list(budget_manager.get_all_budgets())
        assert len(all_budgets) == 3

        budget_names = [b.name for b in all_budgets]
        assert "daily_cost" in budget_names
        assert "hourly_tokens" in budget_names
        assert "daily_requests" in budget_names

    def test_budget_manager_add_budget(self, budget_manager):
        """Test adding budget to manager."""
        new_budget = create_cost_budget("weekly_cost", 100.0, BudgetPeriod.WEEKLY, hard_limit=True)

        budget_manager.add_budget(new_budget)

        assert len(budget_manager.budgets) == 4
        assert budget_manager.get_budget("weekly_cost") == new_budget

    def test_budget_manager_add_duplicate_name(self, budget_manager):
        """Test adding budget with duplicate name."""
        duplicate_budget = create_cost_budget(
            "daily_cost", 20.0, BudgetPeriod.DAILY, hard_limit=True
        )

        with pytest.raises(ValueError) as exc_info:
            budget_manager.add_budget(duplicate_budget)

        assert "already exists" in str(exc_info.value)

    def test_budget_manager_get_budget(self, budget_manager):
        """Test getting budget by name."""
        cost_budget = budget_manager.get_budget("daily_cost")
        assert cost_budget is not None
        assert cost_budget.name == "daily_cost"
        assert cost_budget.budget_type == BudgetType.COST_USD

        # Non-existent budget
        missing_budget = budget_manager.get_budget("nonexistent")
        assert missing_budget is None

    def test_budget_manager_remove_budget(self, budget_manager):
        """Test removing budget from manager."""
        assert budget_manager.get_budget("daily_cost") is not None

        budget_manager.remove_budget("daily_cost")

        assert budget_manager.get_budget("daily_cost") is None
        assert len(budget_manager.budgets) == 2

    def test_budget_manager_remove_nonexistent(self, budget_manager):
        """Test removing non-existent budget."""
        # Should not raise error
        budget_manager.remove_budget("nonexistent_budget")
        assert len(budget_manager.budgets) == 3  # No change

    def test_budget_manager_check_preflight_success(self, budget_manager):
        """Test preflight budget check - success case."""
        usage = Usage(prompt=100, completion=50, total=150, cost_estimate=2.0)

        # Should pass all budget checks
        budget_manager.check_preflight(usage)  # Should not raise

    def test_budget_manager_check_preflight_cost_exceeded(self, budget_manager):
        """Test preflight budget check - cost budget exceeded."""
        # Consume most of the cost budget
        cost_budget = budget_manager.get_budget("daily_cost")
        cost_budget.consumed = 8.0  # 8 out of 10

        usage = Usage(prompt=500, completion=300, total=800, cost_estimate=3.0)

        with pytest.raises(BudgetExceededError) as exc_info:
            budget_manager.check_preflight(usage)

        assert "daily_cost" in str(exc_info.value)

    def test_budget_manager_check_preflight_token_exceeded(self, budget_manager):
        """Test preflight budget check - token budget exceeded."""
        # Consume most of the token budget
        token_budget = budget_manager.get_budget("hourly_tokens")
        token_budget.consumed = 4800  # 4800 out of 5000

        usage = Usage(prompt=300, completion=0, total=300)

        with pytest.raises(BudgetExceededError) as exc_info:
            budget_manager.check_preflight(usage)

        assert "hourly_tokens" in str(exc_info.value)

    def test_budget_manager_check_preflight_soft_limit_warning(self, budget_manager):
        """Test preflight budget check - soft limit warning."""
        # Set up request budget near warning threshold
        request_budget = budget_manager.get_budget("daily_requests")
        request_budget.consumed = 85  # 85 out of 100, above 80% warning

        usage = Usage(prompt=50, completion=25, total=75)

        # Should warn but not fail (soft limit)
        with pytest.warns(UserWarning):
            budget_manager.check_preflight(usage)

    def test_budget_manager_track_usage_success(self, budget_manager):
        """Test tracking usage against budgets."""
        initial_cost = budget_manager.get_budget("daily_cost").consumed
        initial_tokens = budget_manager.get_budget("hourly_tokens").consumed
        initial_requests = budget_manager.get_budget("daily_requests").consumed

        usage = Usage(prompt=100, completion=50, total=150, cost_estimate=1.5)

        budget_manager.track_usage(usage)

        # Check that budgets were updated
        assert budget_manager.get_budget("daily_cost").consumed == initial_cost + 1.5
        assert budget_manager.get_budget("hourly_tokens").consumed == initial_tokens + 150
        assert budget_manager.get_budget("daily_requests").consumed == initial_requests + 1

    def test_budget_manager_track_usage_no_cost_estimate(self, budget_manager):
        """Test tracking usage without cost estimate."""
        initial_cost = budget_manager.get_budget("daily_cost").consumed
        initial_tokens = budget_manager.get_budget("hourly_tokens").consumed

        usage = Usage(prompt=200, completion=100, total=300)  # No cost_estimate

        budget_manager.track_usage(usage)

        # Cost budget should not change, tokens should
        assert budget_manager.get_budget("daily_cost").consumed == initial_cost
        assert budget_manager.get_budget("hourly_tokens").consumed == initial_tokens + 300

    def test_budget_manager_reset_budget(self, budget_manager):
        """Test resetting individual budget."""
        cost_budget = budget_manager.get_budget("daily_cost")
        cost_budget.consumed = 5.0

        budget_manager.reset_budget("daily_cost")

        assert cost_budget.consumed == 0.0

    def test_budget_manager_reset_nonexistent_budget(self, budget_manager):
        """Test resetting non-existent budget."""
        # Should not raise error
        budget_manager.reset_budget("nonexistent")

    def test_budget_manager_reset_all_budgets(self, budget_manager):
        """Test resetting all budgets."""
        # Consume some budget
        for budget in budget_manager.get_all_budgets():
            if budget.budget_type == BudgetType.COST_USD:
                budget.consumed = 3.0
            elif budget.budget_type == BudgetType.TOKEN_COUNT:
                budget.consumed = 1000
            elif budget.budget_type == BudgetType.REQUEST_COUNT:
                budget.consumed = 25

        budget_manager.reset_all_budgets()

        # All should be reset
        for budget in budget_manager.get_all_budgets():
            assert budget.consumed == 0.0

    def test_budget_manager_auto_reset_needed_budgets(self, budget_manager):
        """Test automatic reset of budgets that need it."""
        # Set last reset times to trigger reset
        for budget in budget_manager.get_all_budgets():
            budget.consumed = 50  # Some consumption
            if budget.period == BudgetPeriod.DAILY:
                budget.last_reset = datetime.now() - timedelta(days=1, hours=1)
            elif budget.period == BudgetPeriod.HOURLY:
                budget.last_reset = datetime.now() - timedelta(hours=1, minutes=1)

        reset_count = budget_manager.reset_expired_budgets()

        # Should have reset budgets that needed it
        assert reset_count > 0

        # Budgets should be reset
        for budget in budget_manager.get_all_budgets():
            if budget.needs_reset():
                assert budget.consumed == 0.0

    def test_budget_manager_get_budget_status(self, budget_manager):
        """Test getting budget status summary."""
        # Set some consumption
        cost_budget = budget_manager.get_budget("daily_cost")
        cost_budget.consumed = 6.0

        token_budget = budget_manager.get_budget("hourly_tokens")
        token_budget.consumed = 2500

        status = budget_manager.get_budget_status()

        assert len(status) == 3
        assert status["daily_cost"]["consumed"] == 6.0
        assert status["daily_cost"]["limit"] == 10.0
        assert status["daily_cost"]["utilization_rate"] == 0.6

        assert status["hourly_tokens"]["consumed"] == 2500
        assert status["hourly_tokens"]["utilization_rate"] == 0.5

    def test_budget_manager_get_warnings(self, budget_manager):
        """Test getting budget warnings."""
        # Set budgets to warning levels
        cost_budget = budget_manager.get_budget("daily_cost")
        cost_budget.consumed = 8.5  # 85% of 10.0

        token_budget = budget_manager.get_budget("hourly_tokens")
        token_budget.consumed = 4200  # 84% of 5000

        warnings = budget_manager.get_warnings()

        assert len(warnings) == 2
        warning_names = [w["budget_name"] for w in warnings]
        assert "daily_cost" in warning_names
        assert "hourly_tokens" in warning_names

    def test_budget_manager_get_exceeded_budgets(self, budget_manager):
        """Test getting exceeded budgets."""
        # Exceed some budgets
        cost_budget = budget_manager.get_budget("daily_cost")
        cost_budget.consumed = 12.0  # Exceeds 10.0

        exceeded = budget_manager.get_exceeded_budgets()

        assert len(exceeded) == 1
        assert exceeded[0].name == "daily_cost"


class TestBudgetIntegration:
    """Test budget integration scenarios."""

    def test_budget_lifecycle_scenario(self):
        """Test complete budget lifecycle scenario."""
        # Create budget manager with realistic budgets
        budgets = [
            create_cost_budget(
                "daily_api_cost", 50.0, BudgetPeriod.DAILY, hard_limit=True, warning_threshold=0.8
            ),
            create_token_budget(
                "hourly_tokens",
                100000,
                BudgetPeriod.HOURLY,
                hard_limit=False,
                warning_threshold=0.9,
            ),
            create_request_budget("daily_requests", 500, BudgetPeriod.DAILY, hard_limit=True),
        ]

        manager = BudgetManager(budgets)

        # Simulate API usage throughout the day
        usage_scenarios = [
            Usage(prompt=1000, completion=500, total=1500, cost_estimate=5.0),  # Large request
            Usage(prompt=200, completion=100, total=300, cost_estimate=1.0),  # Medium request
            Usage(prompt=50, completion=25, total=75, cost_estimate=0.2),  # Small request
        ]

        # Process multiple requests
        for i in range(10):  # 10 rounds of requests
            for usage in usage_scenarios:
                # Check if we can proceed
                try:
                    manager.check_preflight(usage)
                    manager.track_usage(usage)
                except BudgetExceededError as e:
                    # Handle budget exceeded
                    print(f"Budget exceeded at iteration {i}: {e}")
                    break

        # Check final status
        status = manager.get_budget_status()
        warnings = manager.get_warnings()
        exceeded = manager.get_exceeded_budgets()

        # Verify realistic budget consumption
        assert status["daily_api_cost"]["consumed"] > 0
        assert status["hourly_tokens"]["consumed"] > 0
        assert status["daily_requests"]["consumed"] > 0

        # Some budgets might be in warning state
        print(f"Active warnings: {len(warnings)}")
        print(f"Exceeded budgets: {len(exceeded)}")

    def test_budget_reset_timing_accuracy(self):
        """Test budget reset timing accuracy."""
        # Create hourly budget
        budget = create_token_budget("timing_test", 1000, BudgetPeriod.HOURLY, hard_limit=True)
        manager = BudgetManager([budget])

        # Set precise timing
        now = datetime.now()
        budget.last_reset = now - timedelta(hours=1, seconds=1)  # Just over an hour ago
        budget.consumed = 500

        # Should need reset
        assert budget.needs_reset()

        # Reset and verify timing
        reset_count = manager.reset_expired_budgets()
        assert reset_count == 1
        assert budget.consumed == 0
        assert budget.last_reset > now

    def test_budget_multiple_types_coordination(self):
        """Test coordination between multiple budget types."""
        budgets = [
            create_cost_budget("cost_limit", 10.0, BudgetPeriod.DAILY, hard_limit=True),
            create_token_budget("token_limit", 10000, BudgetPeriod.DAILY, hard_limit=True),
            create_request_budget("request_limit", 50, BudgetPeriod.DAILY, hard_limit=True),
        ]

        manager = BudgetManager(budgets)

        # Large usage that might hit multiple limits
        large_usage = Usage(prompt=8000, completion=4000, total=12000, cost_estimate=15.0)

        # Should fail on cost limit first
        with pytest.raises(BudgetExceededError) as exc_info:
            manager.check_preflight(large_usage)

        assert "cost_limit" in str(exc_info.value)

        # Smaller usage within cost but hitting token limit
        token_heavy_usage = Usage(prompt=9000, completion=2000, total=11000, cost_estimate=3.0)

        with pytest.raises(BudgetExceededError) as exc_info:
            manager.check_preflight(token_heavy_usage)

        assert "token_limit" in str(exc_info.value)

        # Usage within limits should work
        reasonable_usage = Usage(prompt=100, completion=50, total=150, cost_estimate=0.5)
        manager.check_preflight(reasonable_usage)  # Should not raise
        manager.track_usage(reasonable_usage)

        # Verify consumption
        status = manager.get_budget_status()
        assert status["cost_limit"]["consumed"] == 0.5
        assert status["token_limit"]["consumed"] == 150
        assert status["request_limit"]["consumed"] == 1

    def test_budget_soft_vs_hard_limit_behavior(self):
        """Test behavior difference between soft and hard limits."""
        budgets = [
            create_cost_budget("hard_limit", 5.0, BudgetPeriod.DAILY, hard_limit=True),
            create_cost_budget("soft_limit", 5.0, BudgetPeriod.DAILY, hard_limit=False),
        ]

        manager = BudgetManager(budgets)

        # Consume close to limit
        usage = Usage(prompt=1000, completion=500, total=1500, cost_estimate=4.5)
        manager.track_usage(usage)

        # Try to exceed both limits
        exceeding_usage = Usage(prompt=500, completion=250, total=750, cost_estimate=1.0)

        # Hard limit should fail
        with pytest.raises(BudgetExceededError):
            manager.check_preflight(exceeding_usage)

        # Remove hard limit budget and try again
        manager.remove_budget("hard_limit")

        # Soft limit should warn but allow
        with pytest.warns(UserWarning):
            manager.check_preflight(exceeding_usage)
            manager.track_usage(exceeding_usage)

        # Verify soft limit budget exceeded but still functional
        soft_budget = manager.get_budget("soft_limit")
        assert soft_budget.consumed == 5.5  # 4.5 + 1.0
        assert soft_budget.is_exceeded

    def test_budget_warning_threshold_customization(self):
        """Test custom warning thresholds work correctly."""
        budgets = [
            create_cost_budget(
                "early_warning", 10.0, BudgetPeriod.DAILY, hard_limit=False, warning_threshold=0.5
            ),  # 50% warning
            create_cost_budget(
                "late_warning", 10.0, BudgetPeriod.DAILY, hard_limit=False, warning_threshold=0.95
            ),  # 95% warning
        ]

        manager = BudgetManager(budgets)

        # Usage that triggers early warning but not late warning
        usage = Usage(prompt=1000, completion=500, total=1500, cost_estimate=6.0)

        # Should warn for early_warning (60% > 50%) but not late_warning (60% < 95%)
        with pytest.warns(UserWarning) as warning_info:
            manager.check_preflight(usage)

        # Should have exactly one warning
        assert len(warning_info) == 1
        assert "early_warning" in str(warning_info[0].message)

        # Track usage
        manager.track_usage(usage)

        # Now both should warn with additional usage
        additional_usage = Usage(prompt=500, completion=250, total=750, cost_estimate=4.0)

        with pytest.warns(UserWarning) as warning_info:
            manager.check_preflight(additional_usage)

        # Should have two warnings now (total would be 100% > both thresholds)
        assert len(warning_info) == 2

    def test_budget_edge_cases(self):
        """Test budget edge cases and boundary conditions."""
        # Zero limit budget
        zero_budget = create_cost_budget("zero_limit", 0.0, BudgetPeriod.DAILY, hard_limit=True)
        manager = BudgetManager([zero_budget])

        # Any usage should exceed zero budget
        usage = Usage(prompt=1, completion=1, total=2, cost_estimate=0.001)

        with pytest.raises(BudgetExceededError):
            manager.check_preflight(usage)

        # Negative consumption (refund scenario)
        budget = create_cost_budget("refund_test", 10.0, BudgetPeriod.DAILY, hard_limit=True)
        budget.consumed = 5.0

        # Negative consumption (like a refund)
        budget.consume(-2.0)
        assert budget.consumed == 3.0
        assert budget.utilization_rate == 0.3

        # Very large limit
        large_budget = create_token_budget(
            "large_limit", 1_000_000_000, BudgetPeriod.MONTHLY, hard_limit=True
        )
        assert large_budget.remaining == 1_000_000_000
        assert large_budget.utilization_rate == 0.0

    def test_budget_concurrent_access_safety(self):
        """Test budget thread safety and concurrent access."""
        import threading

        budget = create_cost_budget("concurrent_test", 100.0, BudgetPeriod.DAILY, hard_limit=False)
        manager = BudgetManager([budget])

        # Track consumption from multiple threads
        consumption_results = []
        errors = []

        def consume_budget(thread_id, amount, count):
            try:
                for i in range(count):
                    usage = Usage(prompt=100, completion=50, total=150, cost_estimate=amount)
                    try:
                        manager.check_preflight(usage)
                        manager.track_usage(usage)
                        consumption_results.append((thread_id, i, amount))
                    except BudgetExceededError as e:
                        errors.append((thread_id, i, str(e)))
                    time.sleep(0.001)  # Small delay to encourage interleaving
            except Exception as e:
                errors.append((thread_id, "general", str(e)))

        # Start multiple threads consuming budget
        threads = []
        for i in range(5):
            thread = threading.Thread(target=consume_budget, args=(i, 2.0, 20))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify final state is consistent
        final_consumed = budget.consumed
        expected_consumed = len(consumption_results) * 2.0

        assert (
            abs(final_consumed - expected_consumed) < 0.001
        )  # Account for floating point precision
        assert budget.consumed >= 0  # Should never go negative

        # Print results for debugging if needed
        print(f"Concurrent test results: consumed={final_consumed}, expected={expected_consumed}")
        print(f"Successful consumptions: {len(consumption_results)}, errors: {len(errors)}")

    def test_budget_serialization_compatibility(self):
        """Test that budgets can be serialized/deserialized (for persistence)."""
        import json
        from datetime import datetime

        budget = create_cost_budget(
            "serialize_test", 25.0, BudgetPeriod.WEEKLY, hard_limit=True, warning_threshold=0.75
        )
        budget.consumed = 15.5

        # Create a serializable representation
        budget_data = {
            "name": budget.name,
            "budget_type": budget.budget_type.value,
            "limit": budget.limit,
            "period": budget.period.value,
            "hard_limit": budget.hard_limit,
            "warning_threshold": budget.warning_threshold,
            "consumed": budget.consumed,
            "last_reset": budget.last_reset.isoformat(),
        }

        # Serialize to JSON
        json_data = json.dumps(budget_data)

        # Deserialize
        loaded_data = json.loads(json_data)

        # Recreate budget
        restored_budget = Budget(
            name=loaded_data["name"],
            budget_type=BudgetType(loaded_data["budget_type"]),
            limit=loaded_data["limit"],
            period=BudgetPeriod(loaded_data["period"]),
            hard_limit=loaded_data["hard_limit"],
            warning_threshold=loaded_data["warning_threshold"],
        )
        restored_budget.consumed = loaded_data["consumed"]
        restored_budget.last_reset = datetime.fromisoformat(loaded_data["last_reset"])

        # Verify restoration
        assert restored_budget.name == budget.name
        assert restored_budget.budget_type == budget.budget_type
        assert restored_budget.limit == budget.limit
        assert restored_budget.period == budget.period
        assert restored_budget.hard_limit == budget.hard_limit
        assert restored_budget.warning_threshold == budget.warning_threshold
        assert restored_budget.consumed == budget.consumed
        assert abs((restored_budget.last_reset - budget.last_reset).total_seconds()) < 1
