#!/usr/bin/env python3
"""
Test adapter self-policing to ensure Chat Completions parameters are rejected.

Per colleague_1's requirement: "Add a tiny unit test that asserts the adapter kwargs never contain messages."
"""

import pytest
from chirality.infrastructure.llm.openai_adapter import call_responses, LLMClient


def test_call_responses_rejects_messages():
    """Test that call_responses raises when messages parameter is provided."""
    
    with pytest.raises(ValueError, match="Forbidden Chat Completions parameter 'messages' detected"):
        call_responses(
            instructions="Test instructions",
            input="Test input",
            messages=[{"role": "user", "content": "test"}]  # FORBIDDEN
        )


def test_call_responses_rejects_chat_completions_params():
    """Test that call_responses rejects all Chat Completions parameters."""
    
    forbidden_params = [
        'messages', 'message', 'role', 'content', 'system', 'user', 'assistant',
        'max_tokens', 'max_completion_tokens', 'function_call', 'functions',
        'chat', 'completions', 'stream'
    ]
    
    for param in forbidden_params:
        with pytest.raises(ValueError, match=f"Forbidden Chat Completions parameter '{param}' detected"):
            call_responses(
                instructions="Test instructions",
                input="Test input",
                **{param: "test_value"}
            )


def test_call_responses_rejects_unexpected_params():
    """Test that call_responses rejects unexpected parameters."""
    
    with pytest.raises(ValueError, match=r"Unexpected parameters: \['unknown_param'\]"):
        call_responses(
            instructions="Test instructions",
            input="Test input",
            unknown_param="test_value"
        )


def test_call_responses_allows_valid_responses_params():
    """Test that call_responses allows valid Responses API parameters."""
    
    # This should NOT raise - these are valid Responses API parameters
    # We'll mock the actual call to avoid making real API requests
    
    from unittest.mock import patch, Mock
    
    mock_response = {
        "id": "test_id",
        "output_text": '{"test": "response"}',
        "usage": None,
        "raw": {"metadata": {}}
    }
    
    with patch('chirality.infrastructure.llm.openai_adapter.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.call_responses_new.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # These should all work without raising
        result = call_responses(
            instructions="Test instructions",
            input="Test input",
            text={"format": "json_object"},
            store=True,
            metadata={"test": "metadata"}
        )
        
        assert result == mock_response
        mock_client.call_responses_new.assert_called_once_with(
            instructions="Test instructions",
            input="Test input",
            text={"format": "json_object"},
            store=True,
            metadata={"test": "metadata"}
        )


def test_llm_client_call_responses_new_self_policing():
    """Test that LLMClient.call_responses_new also rejects forbidden parameters."""
    
    # Test direct client usage (should also be self-policing)
    client = LLMClient.__new__(LLMClient)  # Create without __init__ to avoid needing API key
    
    with pytest.raises(ValueError, match="Forbidden Chat Completions parameter 'messages' detected in LLMClient"):
        client.call_responses_new(
            instructions="Test instructions",
            input="Test input",
            messages=[{"role": "user", "content": "test"}]  # FORBIDDEN
        )
    
    with pytest.raises(ValueError, match="Unexpected parameters: \\['unknown_param'\\]"):
        client.call_responses_new(
            instructions="Test instructions",
            input="Test input",
            unknown_param="test_value"
        )


def test_adapter_kwargs_never_contain_messages():
    """
    Colleague_1 requirement: "Add a tiny unit test that asserts the adapter kwargs never contain messages."
    
    Test that our adapter implementation can never accidentally pass messages to underlying calls.
    """
    
    from unittest.mock import patch, Mock
    
    # Track all kwargs passed to the underlying implementation
    captured_kwargs = []
    
    def capture_kwargs(**kwargs):
        captured_kwargs.append(kwargs)
        # Return a mock response
        return {
            "id": "test_id",
            "output_text": '{"test": "response"}',
            "usage": None,
            "raw": {"metadata": {}}
        }
    
    with patch('chirality.infrastructure.llm.openai_adapter.get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.call_responses_new.side_effect = capture_kwargs
        mock_get_client.return_value = mock_client
        
        # Make a valid call
        call_responses(
            instructions="Test instructions",
            input="Test input",
            text={"format": "json_object"}
        )
        
        # Assert no forbidden parameters were passed through
        assert len(captured_kwargs) == 1
        kwargs = captured_kwargs[0]
        
        # Ensure no messages or Chat Completions parameters
        forbidden = {'messages', 'message', 'role', 'content', 'system', 'user', 'assistant',
                    'max_tokens', 'max_completion_tokens', 'function_call', 'functions',
                    'chat', 'completions', 'stream'}
        
        for param in forbidden:
            assert param not in kwargs, f"Forbidden parameter '{param}' found in adapter kwargs!"
        
        # Ensure only valid Responses API parameters
        expected_params = {'instructions', 'input', 'text', 'store', 'metadata'}
        for param in kwargs:
            assert param in expected_params, f"Unexpected parameter '{param}' in adapter kwargs!"


if __name__ == "__main__":
    print("🔄 Testing adapter self-policing...")
    
    try:
        test_call_responses_rejects_messages()
        test_call_responses_rejects_chat_completions_params()
        test_call_responses_rejects_unexpected_params()
        test_call_responses_allows_valid_responses_params()
        test_llm_client_call_responses_new_self_policing()
        test_adapter_kwargs_never_contain_messages()
        
        print("✅ All adapter self-policing tests passed!")
        print("✅ Adapter rejects Chat Completions parameters")
        print("✅ Adapter kwargs never contain messages")
        print("✅ Only valid Responses API parameters allowed")
        
    except Exception as e:
        print(f"❌ Adapter self-policing test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
