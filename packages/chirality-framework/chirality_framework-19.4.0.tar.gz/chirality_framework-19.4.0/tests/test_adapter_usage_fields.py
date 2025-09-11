"""
Test OpenAI adapter usage field normalization.

Validates that the adapter correctly normalizes usage fields from different
OpenAI response structures into the format expected by BudgetTracker.
"""

import pytest
from unittest.mock import Mock

from chirality.infrastructure.llm.openai_adapter import LLMClient


@pytest.fixture
def mock_client():
    """Create mock LLM client for testing normalization."""
    return LLMClient.__new__(LLMClient)  # Skip __init__


def test_normalize_usage_fields_complete(mock_client):
    """Test normalization with complete usage data."""
    # Mock response with all fields
    response = Mock()
    usage = Mock()
    usage.input_tokens = 1000
    usage.output_tokens = 500
    usage.total_tokens = 1500

    input_details = Mock()
    input_details.cached_tokens = 200
    usage.input_token_details = input_details

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    assert result == {
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "cached_tokens": 200,
        "total_tokens": 1500,
    }


def test_normalize_usage_fields_fallback_names(mock_client):
    """Test normalization with fallback field names."""
    # Mock response using legacy field names
    response = Mock()
    usage = Mock()
    usage.prompt_tokens = 800  # Legacy name
    usage.completion_tokens = 300  # Legacy name
    usage.total_tokens = 1100

    # No input_tokens/output_tokens to force fallback
    usage.input_tokens = 0
    usage.output_tokens = 0

    # No cached tokens
    usage.input_token_details = None

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    assert result == {
        "prompt_tokens": 800,
        "completion_tokens": 300,
        "cached_tokens": 0,
        "total_tokens": 1100,
    }


def test_normalize_usage_fields_no_usage(mock_client):
    """Test normalization when response.usage is None."""
    response = Mock()
    response.usage = None

    result = mock_client._normalize_usage_fields(response)

    assert result == {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cached_tokens": 0,
        "total_tokens": 0,
    }


def test_normalize_usage_fields_missing_total(mock_client):
    """Test total_tokens calculation when not provided."""
    response = Mock()
    usage = Mock()
    usage.input_tokens = 600
    usage.output_tokens = 400
    usage.total_tokens = 0  # Missing, should calculate
    usage.input_token_details = None

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    assert result == {
        "prompt_tokens": 600,
        "completion_tokens": 400,
        "cached_tokens": 0,
        "total_tokens": 1000,  # Calculated: 600 + 400
    }


def test_normalize_usage_fields_negative_values(mock_client):
    """Test that negative values are clamped to zero."""
    response = Mock()
    usage = Mock()
    usage.input_tokens = -100  # Invalid negative
    usage.output_tokens = 200
    usage.total_tokens = -50  # Invalid negative
    usage.input_token_details = None

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    assert result == {
        "prompt_tokens": 0,  # Clamped
        "completion_tokens": 200,
        "cached_tokens": 0,
        "total_tokens": 0,  # Clamped
    }


def test_normalize_usage_fields_float_values(mock_client):
    """Test that float values are converted to integers."""
    response = Mock()
    usage = Mock()
    usage.input_tokens = 100.7  # Float value
    usage.output_tokens = 50.2
    usage.total_tokens = 150.9
    usage.input_token_details = None

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    assert result == {
        "prompt_tokens": 100,  # Converted to int
        "completion_tokens": 50,
        "cached_tokens": 0,
        "total_tokens": 150,
    }


def test_normalize_usage_fields_cached_tokens_extraction(mock_client):
    """Test cached token extraction from input_token_details."""
    response = Mock()
    usage = Mock()
    usage.input_tokens = 1000
    usage.output_tokens = 200
    usage.total_tokens = 1200

    # Mock nested input_token_details
    input_details = Mock()
    input_details.cached_tokens = 150
    usage.input_token_details = input_details

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    assert result["cached_tokens"] == 150


def test_normalize_usage_fields_robustness(mock_client):
    """Test robustness against various attribute errors."""
    # Mock response with missing attributes
    response = Mock()

    # Usage object exists but missing most attributes
    usage = Mock()
    del usage.input_tokens  # Force AttributeError
    del usage.output_tokens
    del usage.total_tokens
    del usage.prompt_tokens
    del usage.completion_tokens
    usage.input_token_details = None

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    # Should gracefully handle missing attributes
    assert result == {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cached_tokens": 0,
        "total_tokens": 0,
    }


def test_normalize_usage_fields_budget_tracker_compatibility(mock_client):
    """Test that normalized fields match BudgetTracker expectations."""
    response = Mock()
    usage = Mock()
    usage.input_tokens = 500
    usage.output_tokens = 300
    usage.total_tokens = 800

    input_details = Mock()
    input_details.cached_tokens = 100
    usage.input_token_details = input_details

    response.usage = usage

    result = mock_client._normalize_usage_fields(response)

    # Verify all expected fields exist
    expected_fields = {"prompt_tokens", "completion_tokens", "cached_tokens", "total_tokens"}
    assert set(result.keys()) == expected_fields

    # Verify all values are integers >= 0
    for field, value in result.items():
        assert isinstance(value, int), f"{field} should be int, got {type(value)}"
        assert value >= 0, f"{field} should be >= 0, got {value}"
