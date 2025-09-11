#!/usr/bin/env python3
"""
Test D2-3: Adapter contract validation.

Tests that _execute_stage calls the adapter with:
- instructions == bytes(system.md) (verify SHA)
- input containing entire transcript + current asset text
- text.format configured to JSON (object or schema)
"""

import json
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from chirality.application.phase1.dialogue_run import DialogueOrchestrator

def load_api_key():
    """Load API key from .env file silently."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    import os
                    os.environ["OPENAI_API_KEY"] = key
                    return True
    return True

def test_adapter_contract_instructions():
    """Test D2-3: Adapter receives correct instructions (system.md)."""
    
    print("🔄 Testing D2-3: Adapter contract - instructions parameter...")
    
    load_api_key()
    
    # Capture the actual call arguments
    captured_calls = []
    
    def mock_call_responses(**kwargs):
        captured_calls.append(kwargs)
        return {
            "id": "test_id",
            "output_text": json.dumps({"name": "C", "elements": [["test"]]}),
            "usage": None,
            "raw": {}
        }
    
    with patch('chirality.application.phase1.dialogue_run.call_responses', side_effect=mock_call_responses):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        # Run just the mechanical stage
        try:
            result, trace = orchestrator._execute_stage("phase1_c_mechanical", "C", "mechanical")
            
            # Should have captured at least one call
            assert len(captured_calls) > 0, "No adapter calls captured"
            
            call_args = captured_calls[0]
            
            # Test 1: instructions parameter present
            assert "instructions" in call_args, "Missing instructions parameter"
            instructions = call_args["instructions"]
            
            # Test 2: instructions should be system.md content
            expected_system = orchestrator.registry.get_text("system")
            assert instructions == expected_system, "Instructions should be exact system.md content"
            
            # Test 3: Verify SHA of instructions
            expected_sha = hashlib.sha256(expected_system.encode()).hexdigest()
            actual_sha = hashlib.sha256(instructions.encode()).hexdigest()
            assert actual_sha == expected_sha, f"Instructions SHA mismatch: {actual_sha[:16]} != {expected_sha[:16]}"
            
            print(f"✅ Instructions parameter correct (SHA: {actual_sha[:16]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Adapter contract test failed: {e}")
            return False

def test_adapter_contract_input():
    """Test D2-3: Adapter receives correct input (transcript + asset text)."""
    
    print("🔄 Testing D2-3: Adapter contract - input parameter...")
    
    load_api_key()
    
    # Capture the actual call arguments
    captured_calls = []
    
    def mock_call_responses(**kwargs):
        captured_calls.append(kwargs)
        return {
            "id": "test_id", 
            "output_text": json.dumps({"name": "C", "elements": [["test"]]}),
            "usage": None,
            "raw": {}
        }
    
    with patch('chirality.application.phase1.dialogue_run.call_responses', side_effect=mock_call_responses):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        # Add some history to the dialogue
        orchestrator.dialogue_history = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "First user message"},
            {"role": "assistant", "content": "First assistant response"}
        ]
        
        try:
            result, trace = orchestrator._execute_stage("phase1_c_mechanical", "C", "mechanical")
            
            # Should have captured the call
            assert len(captured_calls) > 0, "No adapter calls captured"
            
            call_args = captured_calls[0]
            
            # Test 1: input parameter present
            assert "input" in call_args, "Missing input parameter"
            input_content = call_args["input"]
            
            # Test 2: input should contain transcript
            assert "[USER] First user message" in input_content, "Input missing transcript content"
            assert "[ASSISTANT] First assistant response" in input_content, "Input missing assistant response"
            
            # Test 3: input should contain current asset text
            assert "mechanical construction" in input_content.lower(), "Input missing current stage asset text"
            
            # Test 4: input should NOT contain system message (that's in instructions)
            assert "System message" not in input_content, "Input should not contain system message"
            
            print("✅ Input parameter contains complete transcript + asset text")
            
            return True
            
        except Exception as e:
            print(f"❌ Input contract test failed: {e}")
            return False

def test_adapter_contract_text_config():
    """Test D2-3: Adapter receives correct text.format configuration."""
    
    print("🔄 Testing D2-3: Adapter contract - response_format parameter...")
    
    load_api_key()
    
    # Capture the actual call arguments
    captured_calls = []
    
    def mock_call_responses(**kwargs):
        captured_calls.append(kwargs)
        return {
            "id": "test_id",
            "output_text": json.dumps({"name": "C", "elements": [["test"]]}),
            "usage": None,
            "raw": {}
        }
    
    with patch('chirality.application.phase1.dialogue_run.call_responses', side_effect=mock_call_responses):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        try:
            result, trace = orchestrator._execute_stage("phase1_c_mechanical", "C", "mechanical")
            
            # Should have captured the call
            assert len(captured_calls) > 0, "No adapter calls captured"
            
            call_args = captured_calls[0]
            
            # Test 1: text parameter present
            assert "text" in call_args, "Missing text parameter"
            text_cfg = call_args["text"]
            
            # Test 2: text.format should enforce JSON (object or strict schema)
            assert text_cfg is not None, "text should not be None"
            assert isinstance(text_cfg, dict), "text should be dict"
            assert text_cfg.get("format") in {"json_object", "json_schema"}, "text.format should enforce JSON"
            
            print("✅ Response format parameter correct (JSON enforcement)")
            
            return True
            
        except Exception as e:
            print(f"❌ Response format contract test failed: {e}")
            return False

def test_adapter_contract_no_messages():
    """Test D2-3: Adapter does NOT receive messages parameter."""
    
    print("🔄 Testing D2-3: Adapter contract - no messages parameter...")
    
    load_api_key()
    
    # Capture the actual call arguments
    captured_calls = []
    
    def mock_call_responses(**kwargs):
        captured_calls.append(kwargs)
        return {
            "id": "test_id",
            "output_text": json.dumps({"name": "C", "elements": [["test"]]}),
            "usage": None,
            "raw": {}
        }
    
    with patch('chirality.application.phase1.dialogue_run.call_responses', side_effect=mock_call_responses):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        try:
            result, trace = orchestrator._execute_stage("phase1_c_mechanical", "C", "mechanical")
            
            # Should have captured the call
            assert len(captured_calls) > 0, "No adapter calls captured"
            
            call_args = captured_calls[0]
            
            # Test: should NOT have messages parameter
            assert "messages" not in call_args, "Adapter should not receive messages parameter"
            
            # Test: should have the new parameters
            required_params = ["instructions", "input", "text"]
            for param in required_params:
                assert param in call_args, f"Missing required parameter: {param}"
            
            print("✅ Adapter uses instructions+input, not messages")
            
            return True
            
        except Exception as e:
            print(f"❌ No-messages contract test failed: {e}")
            return False

def test_adapter_contract_api_call_marker():
    """Test D2-3: Trace entries mark api_call='responses'."""
    
    print("🔄 Testing D2-3: Trace entries mark new API usage...")
    
    load_api_key()
    
    def mock_call_responses(**kwargs):
        return {
            "id": "test_response_id",
            "output_text": json.dumps({"name": "C", "elements": [["test"]]}),
            "usage": {"total_tokens": 100},
            "raw": {}
        }
    
    with patch('chirality.application.phase1.dialogue_run.call_responses', side_effect=mock_call_responses):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        try:
            result, trace = orchestrator._execute_stage("phase1_c_mechanical", "C", "mechanical")
            
            # Test: trace should mark new API usage
            assert "api_call" in trace, "Trace missing api_call field"
            assert trace["api_call"] == "responses", f"Expected api_call='responses', got {trace['api_call']}"
            
            # Test: trace should include response ID
            assert "response_id" in trace, "Trace missing response_id field"
            assert trace["response_id"] == "test_response_id", "Trace should include response ID"
            
            print("✅ Trace correctly marks new API usage")
            
            return True
            
        except Exception as e:
            print(f"❌ API call marker test failed: {e}")
            return False

if __name__ == "__main__":
    success = True
    
    # Run all adapter contract tests
    success &= test_adapter_contract_instructions()
    success &= test_adapter_contract_input()
    success &= test_adapter_contract_text_config()
    success &= test_adapter_contract_no_messages()
    success &= test_adapter_contract_api_call_marker()
    
    if success:
        print("\n✅ ALL D2-3 ADAPTER CONTRACT TESTS PASSED!")
        print("   ✅ Instructions parameter: system.md content with correct SHA")
        print("   ✅ Input parameter: transcript + current asset text")
        print("   ✅ Response format parameter: JSON enforcement")
        print("   ✅ No messages parameter: uses instructions+input instead")
        print("   ✅ Trace markers: api_call='responses' and response_id")
    else:
        print("\n❌ D2-3 ADAPTER CONTRACT TESTS FAILED")
        exit(1)
