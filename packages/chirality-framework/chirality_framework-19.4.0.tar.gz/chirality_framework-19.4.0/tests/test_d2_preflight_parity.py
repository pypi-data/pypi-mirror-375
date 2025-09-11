#!/usr/bin/env python3
"""
Test D2-2: Preflight parity check validation.

Tests row/col parity between interpreted matrix and lens block:
- Success case: matching dimensions
- Failure case: simulated mismatch raises explicit error
"""

import json
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

def mock_responses_api_call(messages, temperature=1.0, json_only=True):
    """Mock OpenAI Responses API with proper row/col data."""
    last_message = messages[-1]["content"] if messages else ""
    
    # Matrix C dimensions from canonical specification
    # C = A · B, so C has A's rows and B's columns  
    correct_rows = ["normative", "operative", "iterative"]  # From Matrix A
    correct_cols = ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"]  # From Matrix B
    
    if "mechanical construction" in last_message.lower():
        return {"content": json.dumps({
            "name": "C",
            "operation": "dot_product",
            "station": "Problem Statement",
            "rows": correct_rows,
            "cols": correct_cols,
            "elements": [["test * data"]]
        })}
    elif "semantic interpretation" in last_message.lower():
        return {"content": json.dumps({
            "name": "C", 
            "operation": "dot_product",
            "station": "Problem Statement",
            "rows": correct_rows,
            "cols": correct_cols,
            "elements": [["test_data"]]
        })}
    else:
        return {"content": json.dumps({
            "name": "C",
            "elements": [["test"]]
        })}

def test_preflight_parity_success():
    """Test D2-2: Successful parity check."""
    
    print("🔄 Testing D2-2: Preflight parity check success...")
    
    load_api_key()
    
    with patch('chirality.application.phase1.dialogue_run.call_responses_api', side_effect=mock_responses_api_call):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        # Run dialogue - should succeed with matching dimensions
        result = orchestrator.run_dialogue()
        
        # Should complete successfully
        assert "matrices" in result
        assert "C" in result["matrices"]
        
        # Check that lens injection happened
        c_matrix = result["matrices"]["C"]
        assert "lenses" in c_matrix
        
        print("✅ Preflight parity check passed - no dimension mismatch")
        return True

def test_preflight_parity_failure():
    """Test D2-2: Simulated mismatch raises error."""
    
    print("🔄 Testing D2-2: Preflight parity check failure...")
    
    load_api_key()
    
    # Mock lens resolver to return mismatched dimensions
    def mock_mismatched_lens_resolve(station):
        return {
            "station": station,
            "matrix_id": "C",
            "rows": ["WRONG", "DIMENSIONS", "HERE"],  # Different from matrix
            "cols": ["MISMATCHED", "COLUMNS"],        # Different from matrix  
            "lenses": [["lens1", "lens2"], ["lens3", "lens4"], ["lens5", "lens6"]],
            "source": "test"
        }
    
    with patch('chirality.application.phase1.dialogue_run.call_responses_api', side_effect=mock_responses_api_call):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        # Mock the lens resolver to return mismatched dimensions
        with patch.object(orchestrator.lens_resolver, 'resolve_lenses', side_effect=mock_mismatched_lens_resolve):
            try:
                result = orchestrator.run_dialogue()
                assert False, "Should have raised ValueError for dimension mismatch"
                
            except ValueError as e:
                error_msg = str(e)
                assert "parity check failed" in error_msg.lower(), f"Expected parity error, got: {error_msg}"
                assert "matrix c" in error_msg.lower(), "Error should mention Matrix C"
                assert "drifted" in error_msg.lower(), "Error should mention dimension drift"
                
                print("✅ Preflight parity check correctly raises error on mismatch")
                return True
                
            except Exception as e:
                print(f"❌ Unexpected exception type: {type(e).__name__}: {e}")
                return False

def test_preflight_parity_with_fallback_parsing():
    """Test D2-2: Parity check with content string parsing."""
    
    print("🔄 Testing D2-2: Preflight parity with fallback parsing...")
    
    load_api_key()
    
    # Mock API call that returns string content (simulating json_parse_failed)
    def mock_string_content_call(messages, temperature=1.0, json_only=True):
        last_message = messages[-1]["content"] if messages else ""
        
        if "semantic interpretation" in last_message.lower():
            # Return content as string that needs parsing (with correct Matrix C dimensions)
            return {"content": "({'name': 'C', 'rows': ['normative', 'operative', 'iterative'], 'cols': ['necessity (vs contingency)', 'sufficiency', 'completeness', 'consistency'], 'elements': [['test']]}, metadata)"}
        else:
            return mock_responses_api_call(messages, temperature, json_only)
    
    with patch('chirality.application.phase1.dialogue_run.call_responses_api', side_effect=mock_string_content_call):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        # Should handle string parsing for parity check
        result = orchestrator.run_dialogue()
        
        # Should complete successfully
        assert "matrices" in result
        assert "C" in result["matrices"]
        
        print("✅ Preflight parity check works with string content parsing")
        return True

def test_preflight_parity_skip_when_no_data():
    """Test D2-2: Parity check skipped when no interpreted data available."""
    
    print("🔄 Testing D2-2: Preflight parity skip when no data...")
    
    load_api_key()
    
    # Mock API that doesn't provide interpretable row/col data
    def mock_no_data_call(messages, temperature=1.0, json_only=True):
        return {"content": json.dumps({"error": "no_data", "name": "C"})}
    
    with patch('chirality.application.phase1.dialogue_run.call_responses_api', side_effect=mock_no_data_call):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        # Should skip parity check and continue
        result = orchestrator.run_dialogue()
        
        # Should complete (lens injection should work even without parity check)
        assert "matrices" in result
        assert "C" in result["matrices"]
        
        print("✅ Preflight parity check skipped when no interpreted data available")
        return True

if __name__ == "__main__":
    success = True
    
    # Run all parity tests
    success &= test_preflight_parity_success()
    success &= test_preflight_parity_failure() 
    success &= test_preflight_parity_with_fallback_parsing()
    success &= test_preflight_parity_skip_when_no_data()
    
    if success:
        print("\n✅ ALL D2-2 PREFLIGHT PARITY TESTS PASSED!")
        print("   ✅ Success case: matching dimensions")
        print("   ✅ Failure case: mismatch raises explicit error") 
        print("   ✅ Fallback parsing: handles string content")
        print("   ✅ Skip case: no interpreted data available")
    else:
        print("\n❌ D2-2 PREFLIGHT PARITY TESTS FAILED")
        exit(1)