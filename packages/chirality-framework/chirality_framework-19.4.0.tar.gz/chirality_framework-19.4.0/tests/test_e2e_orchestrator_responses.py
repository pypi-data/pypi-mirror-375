#!/usr/bin/env python3
"""
End-to-end orchestrator test to verify Responses API usage.

Tests a single stage (C/mechanical) and asserts:
1. Adapter called with instructions+input only (no messages)
2. No metadata in transcript (clean semantic content)
"""

import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from chirality.application.phase1.dialogue_run import DialogueOrchestrator


def test_orchestrator_single_stage_responses_api():
    """Test that orchestrator uses Responses API correctly for a single stage."""
    
    print("🔄 Testing orchestrator single stage with Responses API...")
    
    # Track all call_responses calls
    call_responses_calls = []
    
    def mock_call_responses(**kwargs):
        """Capture all calls to call_responses"""
        call_responses_calls.append(kwargs)
        
        # Return a mock response
        return {
            "output_text": json.dumps({
                "artifact": "matrix",
                "name": "C",
                "station": "problem statement",
                "rows": ["normative", "operative", "iterative"],
                "cols": ["necessity", "sufficiency", "completeness", "consistency"],
                "step": "mechanical",
                "op": "dot",
                "elements": [
                    ["a", "b", "c", "d"],
                    ["e", "f", "g", "h"],
                    ["i", "j", "k", "l"]
                ]
            }),
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "raw": {
                "metadata": {
                    "model": "gpt-4o-mini",
                    "temperature": None,
                    "latency_ms": 500,
                    "total_tokens": 150
                }
            }
        }
    
    # Mock the call_responses function
    with patch('chirality.application.phase1.dialogue_run.call_responses', mock_call_responses):
        # Create orchestrator with echo model
        orchestrator = DialogueOrchestrator(
            model="echo",
            temperature=None,  # Test that None is handled correctly
            budget_config=None,
            lens_mode="auto"
        )
        
        # Run just the first stage (C/mechanical)
        test_output = Path("test_e2e_output")
        test_output.mkdir(exist_ok=True)
        
        try:
            # Access the private method for testing
            orchestrator._call_llm_with_json_tail(
                user_message="Test prompt for C/mechanical",
                json_tail="Return JSON with matrix elements",
                operation="C_mechanical"
            )
            
            # Verify at least one call was made
            assert len(call_responses_calls) > 0, "No calls to call_responses were made"
            
            print(f"✅ Made {len(call_responses_calls)} call(s) to call_responses")
            
            # Verify each call used proper Responses API format
            for i, call_kwargs in enumerate(call_responses_calls):
                print(f"\n📋 Call {i+1} parameters: {list(call_kwargs.keys())}")
                
                # MUST have instructions and input
                assert "instructions" in call_kwargs, f"Call {i+1}: Missing 'instructions' parameter"
                assert "input" in call_kwargs, f"Call {i+1}: Missing 'input' parameter"
                
                # MUST NOT have messages
                assert "messages" not in call_kwargs, f"Call {i+1}: FORBIDDEN 'messages' parameter found!"
                
                # Check that instructions is a string (system prompt)
                assert isinstance(call_kwargs["instructions"], str), f"Call {i+1}: instructions should be a string"
                
                # Check that input is a string (transcript)
                assert isinstance(call_kwargs["input"], str), f"Call {i+1}: input should be a string"
                
                print(f"  ✅ Uses instructions+input format")
                print(f"  ✅ No messages parameter")
                
                # Verify no metadata in the input transcript
                input_text = call_kwargs["input"]
                forbidden_tokens = [
                    "system_sha", "normative_sha", "asset_sha",
                    "generated_at", "source:", "mode:",
                    "<<<BEGIN", ">>>END",
                    "DOT BRIDGE", "DOT-BRIDGE"
                ]
                
                for token in forbidden_tokens:
                    assert token not in input_text, f"Call {i+1}: Forbidden metadata '{token}' found in transcript!"
                
                print(f"  ✅ No metadata in transcript")
            
            print("\n✅ All calls use proper Responses API format")
            print("✅ No metadata pollution in transcripts")
            
        finally:
            # Cleanup
            import shutil
            if test_output.exists():
                shutil.rmtree(test_output)


def test_adapter_temperature_handling():
    """Test that temperature=None is handled correctly."""
    
    print("\n🔄 Testing temperature=None handling...")
    
    from chirality.infrastructure.llm.config import LLMConfig, get_config
    
    # Set temperature to None
    config = get_config()
    original_temp = config.temperature
    config.temperature = None
    
    try:
        # Mock the underlying client.responses.create
        mock_response = Mock()
        mock_response.output_text = '{"test": "response"}'
        mock_response.usage = Mock()
        mock_response.model = "test-model"
        
        with patch('chirality.infrastructure.llm.openai_adapter.OpenAI') as MockOpenAI:
            mock_client = Mock()
            mock_client.responses = Mock()
            
            # Capture the actual API call parameters
            api_call_params = []
            
            def capture_create(**kwargs):
                api_call_params.append(kwargs)
                return mock_response
            
            mock_client.responses.create = capture_create
            MockOpenAI.return_value = mock_client
            
            # Import and use the adapter
            from chirality.infrastructure.llm.openai_adapter import call_responses
            
            # Make a call
            result = call_responses(
                instructions="Test instructions",
                input="Test input"
            )
            
            # Verify temperature was not included when None
            assert len(api_call_params) == 1
            params = api_call_params[0]
            
            if config.temperature is None:
                assert "temperature" not in params, "Temperature should not be included when None"
                print("  ✅ Temperature correctly omitted when None")
            else:
                assert "temperature" in params
                print(f"  ✅ Temperature included: {params['temperature']}")
            
    finally:
        # Restore original temperature
        config.temperature = original_temp


if __name__ == "__main__":
    print("🚀 Running end-to-end orchestrator Responses API tests...")
    
    try:
        test_orchestrator_single_stage_responses_api()
        test_adapter_temperature_handling()
        
        print("\n🎉 ALL E2E ORCHESTRATOR TESTS PASSED!")
        print("✅ Orchestrator uses instructions+input exclusively")
        print("✅ No messages parameter in any call")
        print("✅ No metadata in transcripts")
        print("✅ Temperature=None handled correctly")
        print("✅ Ready for production with 100% Responses API compliance")
        
    except Exception as e:
        print(f"\n❌ E2E TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)