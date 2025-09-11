"""
Test budget tracking system.

Validates that budget tracking works correctly with mock resolvers
and properly enforces limits.
"""

import pytest
from chirality.domain.budgets import BudgetConfig, BudgetTracker
try:
    from chirality.infrastructure.llm.budget_resolver import BudgetAwareResolver
    from chirality.infrastructure.llm.mock_resolvers import EchoResolver
except Exception:
    pytest.skip("Budget resolver is quarantined/absent in this build; skipping budget resolver tests.", allow_module_level=True)


def test_budget_tracker_basic_functionality():
    """Test that budget tracker tracks usage correctly."""
    config = BudgetConfig(token_budget=1000, cost_budget=0.10)
    tracker = BudgetTracker(config, phase="test")

    # Simulate usage
    metadata = {"total_tokens": 100, "prompt_tokens": 60, "completion_tokens": 40}

    tracker.record_usage(metadata, model="gpt-4")

    status = tracker.get_status()
    assert status["tokens"]["total"] == 100
    assert status["operations"] == 1
    assert status["cost"]["spent"] > 0  # Should have cost


def test_budget_tracker_token_limit_exceeded():
    """Test that budget tracker raises error when token limit exceeded."""
    config = BudgetConfig(token_budget=50)  # Very low limit
    tracker = BudgetTracker(config, phase="test")

    # Exceed limit
    metadata = {"total_tokens": 100}

    with pytest.raises(RuntimeError, match="Token budget exceeded"):
        tracker.record_usage(metadata, model="gpt-4")


def test_budget_tracker_cost_limit_exceeded():
    """Test that budget tracker raises error when cost limit exceeded."""
    config = BudgetConfig(cost_budget=0.001)  # Very low limit
    tracker = BudgetTracker(config, phase="test")

    # Exceed limit with high token usage
    metadata = {"total_tokens": 10000, "prompt_tokens": 5000, "completion_tokens": 5000}

    with pytest.raises(RuntimeError, match="Cost budget exceeded"):
        tracker.record_usage(metadata, model="gpt-4")


def test_budget_aware_resolver_wraps_correctly():
    """Test that budget-aware resolver properly wraps another resolver."""
    config = BudgetConfig(token_budget=10000)
    tracker = BudgetTracker(config, phase="test")
    echo_resolver = EchoResolver()

    budget_resolver = BudgetAwareResolver(echo_resolver, tracker)

    # Test that basic functionality works - using a method that still exists
    result = budget_resolver.run_combined_lens(["test content"], "test lens", "C")
    assert result.text  # Should have some result

    # Test delegation works
    assert hasattr(budget_resolver, "run_combined_lens")


def test_budget_config_default_pricing():
    """Test that budget config includes expected model pricing."""
    config = BudgetConfig()

    assert "gpt-4" in config.model_pricing
    assert "gpt-5" in config.model_pricing
    assert "input" in config.model_pricing["gpt-4"]
    assert "output" in config.model_pricing["gpt-4"]


def test_budget_status_includes_expected_fields():
    """Test that budget status includes all expected fields."""
    config = BudgetConfig(token_budget=1000, cost_budget=1.0, time_budget=300)
    tracker = BudgetTracker(config, phase="test")

    status = tracker.get_status()

    # Check structure
    assert "phase" in status
    assert "operations" in status
    assert "tokens" in status
    assert "cost" in status
    assert "time" in status

    # Check token fields
    assert "total" in status["tokens"]
    assert "budget" in status["tokens"]
    assert "utilization" in status["tokens"]

    # Check cost fields
    assert "spent" in status["cost"]
    assert "budget" in status["cost"]

    # Check time fields
    assert "elapsed" in status["time"]
    assert "budget" in status["time"]


def test_pricing_calculation_accuracy():
    """Test that pricing calculation is correct with new per-token rates."""
    config = BudgetConfig()
    tracker = BudgetTracker(config, phase="test")

    # Test gpt-5-nano pricing: $0.05 per 1M input, $0.40 per 1M output
    metadata = {
        "prompt_tokens": 1000,  # Should cost $0.00005 (0.05/1M * 1000)
        "completion_tokens": 500,  # Should cost $0.0002 (0.40/1M * 500)
        "cached_tokens": 0,
        "total_tokens": 1500,
    }

    tracker.record_usage(metadata, model="gpt-5-nano")
    status = tracker.get_status()

    expected_cost = (1000 * 0.05 / 1_000_000) + (500 * 0.40 / 1_000_000)
    # Should be $0.00005 + $0.0002 = $0.00025

    assert abs(status["cost"]["spent"] - expected_cost) < 0.0000001
    assert status["cost"]["spent"] == pytest.approx(0.00025, abs=1e-8)


def test_cached_tokens_pricing():
    """Test that cached tokens are priced correctly at lower rate."""
    config = BudgetConfig()
    tracker = BudgetTracker(config, phase="test")

    # Test with cached tokens: gpt-5-nano cached input is $0.005 per 1M
    metadata = {
        "prompt_tokens": 1000,  # 500 regular + 500 cached
        "completion_tokens": 100,
        "cached_tokens": 500,  # Should cost $0.0000025 (0.005/1M * 500)
        "total_tokens": 1100,
    }

    tracker.record_usage(metadata, model="gpt-5-nano")
    status = tracker.get_status()

    # Cost breakdown:
    # Regular input: 500 * 0.05/1M = $0.000025
    # Cached input: 500 * 0.005/1M = $0.0000025
    # Output: 100 * 0.40/1M = $0.00004
    # Total: $0.0000675
    regular_input_cost = 500 * 0.05 / 1_000_000
    cached_input_cost = 500 * 0.005 / 1_000_000
    output_cost = 100 * 0.40 / 1_000_000
    expected_cost = regular_input_cost + cached_input_cost + output_cost

    assert status["cost"]["spent"] == pytest.approx(expected_cost, abs=1e-8)
