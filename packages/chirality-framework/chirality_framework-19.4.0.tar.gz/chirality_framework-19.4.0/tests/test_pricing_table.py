"""
Test pricing table integrity and consistency.

Validates that the centralized pricing module works correctly
and contains expected models with positive rates.
"""

import pytest
from chirality.domain.pricing import (
    MODEL_PRICING,
    get_model_pricing,
    get_model_price,
    calculate_cost,
)


def test_pricing_table_presence():
    """Test that pricing table contains expected models."""
    expected_models = [
        "gpt-5",
        "gpt-5-mini",
        "gpt-5-nano",
        "gpt-5-chat-latest",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ]

    for model in expected_models:
        assert model in MODEL_PRICING, f"Missing model: {model}"


def test_pricing_rates_positive():
    """Test that all pricing rates are positive."""
    for model, pricing in MODEL_PRICING.items():
        for token_type, rate in pricing.items():
            assert rate > 0, f"Non-positive rate: {model}.{token_type} = {rate}"


def test_pricing_structure_consistency():
    """Test that all models have required pricing fields."""
    for model, pricing in MODEL_PRICING.items():
        # All models must have input and output
        assert "input" in pricing, f"Missing input price for {model}"
        assert "output" in pricing, f"Missing output price for {model}"

        # GPT-5 and newer models should have cached_input
        if model.startswith(("gpt-5", "gpt-4.1", "gpt-4o")):
            assert "cached_input" in pricing, f"Missing cached_input price for {model}"


def test_get_model_pricing():
    """Test that get_model_pricing returns a copy."""
    pricing1 = get_model_pricing()
    pricing2 = get_model_pricing()

    # Should be equal but not the same object
    assert pricing1 == pricing2
    assert pricing1 is not pricing2

    # Modifying copy shouldn't affect original
    pricing1["test-model"] = {"input": 1.0, "output": 2.0}
    assert "test-model" not in MODEL_PRICING
    assert "test-model" not in get_model_pricing()


def test_get_model_price():
    """Test get_model_price function."""
    # Valid model and token type
    price = get_model_price("gpt-5-nano", "input")
    assert price == 0.05 / 1_000_000

    # Valid model with cached_input
    cached_price = get_model_price("gpt-5-nano", "cached_input")
    assert cached_price == 0.005 / 1_000_000

    # Should be less than regular input
    assert cached_price < price


def test_get_model_price_fallback():
    """Test cached_input fallback to input price."""
    # Legacy model without cached_input should fall back
    price = get_model_price("gpt-4", "cached_input")
    input_price = get_model_price("gpt-4", "input")
    assert price == input_price


def test_get_model_price_errors():
    """Test get_model_price error handling."""
    # Unknown model
    with pytest.raises(KeyError, match="Unknown model"):
        get_model_price("nonexistent-model", "input")

    # Unknown token type (no fallback available)
    with pytest.raises(KeyError, match="Unknown token type"):
        get_model_price("gpt-5-nano", "invalid_type")


def test_calculate_cost():
    """Test cost calculation function."""
    # Simple calculation
    cost = calculate_cost(
        model="gpt-5-nano", prompt_tokens=1000, completion_tokens=500, cached_tokens=0
    )

    expected = (1000 * 0.05 / 1_000_000) + (500 * 0.40 / 1_000_000)
    assert abs(cost - expected) < 1e-10

    # With cached tokens
    cost_with_cache = calculate_cost(
        model="gpt-5-nano",
        prompt_tokens=1000,  # 500 regular + 500 cached
        completion_tokens=500,
        cached_tokens=500,
    )

    expected_with_cache = (
        500 * 0.05 / 1_000_000  # regular input
        + 500 * 0.005 / 1_000_000  # cached input
        + 500 * 0.40 / 1_000_000  # output
    )
    assert abs(cost_with_cache - expected_with_cache) < 1e-10

    # Cached should be cheaper than non-cached
    assert cost_with_cache < cost


def test_calculate_cost_unknown_model():
    """Test cost calculation with unknown model returns 0."""
    cost = calculate_cost("unknown-model", 1000, 500, 0)
    assert cost == 0.0


def test_gpt5_nano_is_cheapest():
    """Test that gpt-5-nano is the cheapest model."""
    nano_input = get_model_price("gpt-5-nano", "input")
    nano_output = get_model_price("gpt-5-nano", "output")

    for model in ["gpt-5", "gpt-5-mini", "gpt-4.1", "gpt-4o", "gpt-4"]:
        model_input = get_model_price(model, "input")
        model_output = get_model_price(model, "output")

        assert nano_input <= model_input, f"gpt-5-nano input should be <= {model}"
        assert nano_output <= model_output, f"gpt-5-nano output should be <= {model}"


def test_pricing_order_makes_sense():
    """Test that pricing follows expected patterns."""
    # GPT-5 series should be ordered: nano < mini < full
    gpt5_input = get_model_price("gpt-5", "input")
    gpt5_mini_input = get_model_price("gpt-5-mini", "input")
    gpt5_nano_input = get_model_price("gpt-5-nano", "input")

    assert gpt5_nano_input < gpt5_mini_input < gpt5_input

    # Cached tokens should always be cheaper than regular
    for model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
        regular_price = get_model_price(model, "input")
        cached_price = get_model_price(model, "cached_input")
        assert cached_price < regular_price
