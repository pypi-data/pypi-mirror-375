#!/usr/bin/env python3
"""
Runtime verification smoke test for Responses API usage.

Per colleague_1's requirement: monkeypatch OpenAI client and assert 
client.responses.create() is called at least once, and that no chat endpoint is touched.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from chirality.application.phase1.dialogue_run import DialogueOrchestrator


def test_responses_api_runtime_verification():
    """Test that DialogueOrchestrator uses only Responses API."""
    
    print("🔄 Testing runtime Responses API compliance...")
    
    # Mock response object with Responses API structure
    mock_response = Mock()
    mock_response.output_text = '{"test": "response"}'
    mock_response.usage = Mock()
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    mock_response.usage.total_tokens = 150
    mock_response.usage.input_token_details = Mock()
    mock_response.usage.input_token_details.cached_tokens = 0
    mock_response.model = "gpt-4o-mini"
    
    # Track API calls
    responses_create_calls = []
    chat_completions_calls = []
    
    def mock_responses_create(*args, **kwargs):
        responses_create_calls.append((args, kwargs))
        return mock_response
    
    def mock_chat_completions_create(*args, **kwargs):
        chat_completions_calls.append((args, kwargs))
        # This should never be called!
        raise AssertionError("FORBIDDEN: chat.completions.create was called!")
    
    # Mock the OpenAI client
    with patch('chirality.infrastructure.llm.openai_adapter.OpenAI') as MockOpenAI:
        mock_client = Mock()
        mock_client.responses = Mock()
        mock_client.responses.create = mock_responses_create
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = mock_chat_completions_create
        
        MockOpenAI.return_value = mock_client
        
        # Run a small orchestration
        orchestrator = DialogueOrchestrator(
            model="echo",  # Use echo resolver to avoid real API calls
            temperature=0.2,
            budget_config=None,
            lens_mode="auto"  # Use auto mode to avoid lens catalog requirement
        )
        
        try:
            # Create test output directory
            test_output = Path("test_smoke_output")
            test_output.mkdir(exist_ok=True)
            
            # This should trigger multiple LLM calls using Responses API
            result = orchestrator.run_dialogue(test_output)
            
            print(f"✅ Orchestration completed without calling Chat Completions API")
            print(f"📊 Responses API calls made: {len(responses_create_calls)}")
            print(f"🚫 Chat Completions API calls: {len(chat_completions_calls)}")
            
            # Verify Responses API was used
            assert len(responses_create_calls) > 0, "Expected at least one call to client.responses.create()"
            
            # Verify Chat Completions API was never used  
            assert len(chat_completions_calls) == 0, f"FORBIDDEN: {len(chat_completions_calls)} calls to chat.completions.create found!"
            
            # Verify call structure
            for i, (args, kwargs) in enumerate(responses_create_calls):
                print(f"  Call {i+1}: {list(kwargs.keys())}")
                
                # Should use Responses API parameters
                assert "instructions" in kwargs or "input" in kwargs, f"Call {i+1}: Missing instructions/input parameters"
                
                # Should NOT use Chat Completions parameters
                assert "messages" not in kwargs, f"Call {i+1}: FORBIDDEN messages parameter found"
            
            print("✅ All API calls use proper Responses API format")
            
            # Cleanup
            import shutil
            if test_output.exists():
                shutil.rmtree(test_output)
                
        except Exception as e:
            print(f"❌ Smoke test failed: {e}")
            raise


def test_adapter_responses_api_direct():
    """Test that the adapter itself uses Responses API correctly."""
    
    print("🔄 Testing adapter direct Responses API usage...")
    
    from chirality.infrastructure.llm.openai_adapter import LLMClient
    
    # Mock response
    mock_response = Mock()
    mock_response.output_text = '{"test": "direct response"}'
    mock_response.usage = Mock()
    mock_response.usage.input_tokens = 50
    mock_response.usage.output_tokens = 25
    mock_response.usage.total_tokens = 75
    mock_response.usage.input_token_details = Mock()
    mock_response.usage.input_token_details.cached_tokens = 0
    mock_response.model = "gpt-4o-mini"
    
    responses_calls = []
    chat_calls = []
    
    def mock_responses_create(*args, **kwargs):
        responses_calls.append((args, kwargs))
        return mock_response
        
    def mock_chat_create(*args, **kwargs):
        chat_calls.append((args, kwargs))
        raise AssertionError("FORBIDDEN: chat.completions.create called in adapter!")
    
    with patch('chirality.infrastructure.llm.openai_adapter.OpenAI') as MockOpenAI:
        mock_client = Mock()
        mock_client.responses = Mock()
        mock_client.responses.create = mock_responses_create
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()  
        mock_client.chat.completions.create = mock_chat_create
        
        MockOpenAI.return_value = mock_client
        
        # Test the adapter directly
        llm_client = LLMClient()
        
        # Test old messages format (should be converted internally)
        messages = [
            {"role": "system", "content": "Test system prompt"},
            {"role": "user", "content": "Test user message"}
        ]
        
        # Use default configuration (no parameter overrides per D2-4)
        response_dict, metadata = llm_client.call_responses(
            messages=messages,
            json_only=True
        )
        
        print(f"✅ Adapter call completed using Responses API")
        print(f"📊 Responses calls: {len(responses_calls)}")
        print(f"🚫 Chat calls: {len(chat_calls)}")
        
        # Verify only Responses API was used
        assert len(responses_calls) == 1, "Expected exactly one Responses API call"
        assert len(chat_calls) == 0, "FORBIDDEN: Chat Completions API was called"
        
        # Verify call parameters
        args, kwargs = responses_calls[0]
        print(f"📋 API call parameters: {list(kwargs.keys())}")
        
        assert "instructions" in kwargs, "Missing instructions parameter"
        assert "input" in kwargs, "Missing input parameter" 
        
        # max_output_tokens only included if max_tokens was provided in config
        if "max_output_tokens" in kwargs:
            print("✅ Uses max_output_tokens parameter")
        else:
            print("ℹ️  No max_output_tokens (using API default)")
            
        assert "messages" not in kwargs, "FORBIDDEN: messages parameter found"
        
        print("✅ Adapter uses proper Responses API parameters")


if __name__ == "__main__":
    print("🚀 Running Responses API runtime verification smoke tests...")
    
    try:
        test_adapter_responses_api_direct()
        print()
        test_responses_api_runtime_verification()
        
        print("\n🎉 ALL SMOKE TESTS PASSED!")
        print("✅ No Chat Completions API usage detected")
        print("✅ Only Responses API used throughout framework")
        print("✅ Runtime verification confirms colleague_1's requirements met")
        
    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)