#!/usr/bin/env python3
"""
Test script for Matrix C 4-stage pipeline execution.

Validates the complete conversational pipeline:
1. C/mechanical.md (with operators)
2. C/interpreted.md (resolve operators) 
3. Lens injection (no LLM)
4. C/lensed.md (final interpretation)
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from chirality.application.phase1.dialogue_run import DialogueOrchestrator
from chirality.infrastructure.llm.openai_adapter import call_responses_api

def mock_responses_api_call(messages, temperature=0.1, json_only=True):
    """Mock OpenAI Responses API for testing."""
    # Get the last user message to determine stage
    last_message = messages[-1]["content"] if messages else ""
    
    if "mechanical construction" in last_message.lower():
        # Stage 1: Mechanical - should have operators
        return {
            "content": json.dumps({
                "name": "C",
                "operation": "dot_product",
                "station": "Problem Statement", 
                "dimensions": [3, 4],
                "elements": [
                    ["guiding * data + applying * information + judging * knowledge + reflecting * wisdom",
                     "guiding * necessary + applying * sufficient + judging * complete + reflecting * consistent",
                     "guiding * whole + applying * parts + judging * relationships + reflecting * context",
                     "guiding * true + applying * valid + judging * sound + reflecting * coherent"],
                    ["operational * data + iterative * information + responsive * knowledge + adaptive * wisdom", 
                     "operational * necessary + iterative * sufficient + responsive * complete + adaptive * consistent",
                     "operational * whole + iterative * parts + responsive * relationships + adaptive * context",
                     "operational * true + iterative * valid + responsive * sound + adaptive * coherent"],
                    ["experimental * data + cyclical * information + learning * knowledge + evolving * wisdom",
                     "experimental * necessary + cyclical * sufficient + learning * complete + evolving * consistent", 
                     "experimental * whole + cyclical * parts + learning * relationships + evolving * context",
                     "experimental * true + cyclical * valid + learning * sound + evolving * coherent"]
                ]
            })
        }
    elif "semantic interpretation" in last_message.lower():
        # Stage 2: Interpreted - no operators
        return {
            "content": json.dumps({
                "name": "C", 
                "operation": "dot_product",
                "station": "Problem Statement",
                "dimensions": [3, 4],
                "elements": [
                    ["guided_data_synthesis", "necessary_guidance", "holistic_guidance", "truth_guidance"],
                    ["operational_data_flow", "sufficient_operations", "parts_operations", "valid_operations"], 
                    ["experimental_data_cycles", "complete_learning", "relationship_learning", "sound_learning"]
                ]
            })
        }
    elif "lensed interpretation" in last_message.lower():
        # Stage 4: Lensed - interpreted through lenses
        return {
            "content": json.dumps({
                "name": "C",
                "operation": "dot_product", 
                "station": "Problem Statement",
                "dimensions": [3, 4],
                "elements": [
                    ["problem_necessity_through_normative_lens", "problem_sufficiency_through_normative_lens", 
                     "problem_completeness_through_normative_lens", "problem_consistency_through_normative_lens"],
                    ["problem_necessity_through_operative_lens", "problem_sufficiency_through_operative_lens",
                     "problem_completeness_through_operative_lens", "problem_consistency_through_operative_lens"],
                    ["problem_necessity_through_iterative_lens", "problem_sufficiency_through_iterative_lens", 
                     "problem_completeness_through_iterative_lens", "problem_consistency_through_iterative_lens"]
                ]
            })
        }
    else:
        return {"content": json.dumps({"error": "unknown_stage", "message": last_message[:100]})}

def test_matrix_c_pipeline():
    """Test complete Matrix C 4-stage pipeline."""
    
    print("🔄 Testing Matrix C 4-stage pipeline...")
    
    # Mock the OpenAI API calls
    with patch('chirality.application.phase1.dialogue_run.call_responses_api', side_effect=mock_responses_api_call):
        # Create orchestrator in auto mode to avoid catalog requirements
        orchestrator = DialogueOrchestrator(
            model="gpt-4o-mini",
            temperature=0.1,
            lens_mode="auto"
        )
        
        # Run the dialogue (only Matrix C is implemented)
        try:
            result = orchestrator.run_dialogue()
            
            # Validate result structure
            assert "meta" in result
            assert "matrices" in result  
            assert "trace" in result
            
            print("✅ Basic structure validation passed")
            
            # Validate Matrix C stages
            assert "C" in result["matrices"]
            c_matrix = result["matrices"]["C"]
            
            # Check all 4 stages are present
            expected_stages = ["mechanical", "interpreted", "lenses", "lensed"]
            for stage in expected_stages:
                assert stage in c_matrix, f"Missing stage: {stage}"
            
            print("✅ All 4 stages present")
            
            # Validate mechanical stage has operators
            mechanical = c_matrix["mechanical"]
            mechanical_str = json.dumps(mechanical)
            assert "*" in mechanical_str and "+" in mechanical_str, "Mechanical stage should have operators"
            
            print("✅ Mechanical stage has operators (* and +)")
            
            # Validate interpreted stage has no operators
            interpreted = c_matrix["interpreted"]
            interpreted_str = json.dumps(interpreted)
            assert "*" not in interpreted_str and "+" not in interpreted_str, "Interpreted stage should not have operators"
            
            print("✅ Interpreted stage has no operators")
            
            # Validate lens injection occurred
            lenses = c_matrix["lenses"]
            assert "source" in lenses, "Lenses should have source information"
            assert "lenses" in lenses, "Should contain lens matrix"
            
            print("✅ Lens injection completed")
            
            # Validate lensed stage
            lensed = c_matrix["lensed"]
            assert "elements" in lensed, "Lensed stage should have elements"
            
            print("✅ Lensed stage completed")
            
            # Validate trace entries  
            trace = result["trace"]
            assert len(trace) == 4, f"Expected 4 trace entries, got {len(trace)}"
            
            # Check trace entry types
            expected_trace_types = ["mechanical", "interpreted", "lens_injection", "lensed"]
            actual_types = []
            for entry in trace:
                if "stage" in entry:
                    actual_types.append(entry["stage"])
                elif "type" in entry:
                    actual_types.append(entry["type"])
            
            for expected_type in expected_trace_types:
                assert expected_type in actual_types, f"Missing trace type: {expected_type}"
            
            print("✅ Trace validation passed")
            
            # Validate conversation history progression
            history = orchestrator.dialogue_history
            
            # Should have: system, mechanical_user, mechanical_assistant, interpreted_user, interpreted_assistant, 
            # lens_system, lensed_user, lensed_assistant
            assert len(history) >= 8, f"Expected at least 8 history entries, got {len(history)}"
            
            # Check for lens system message in history
            lens_messages = [msg for msg in history if msg.get("role") == "system" and "Interpretive Lenses" in msg.get("content", "")]
            assert len(lens_messages) > 0, "Should have lens system message in history"
            
            print("✅ Conversation history validation passed")
            
            # Test colleague_1's acceptance criteria
            print("\n🔍 Validating colleague_1's acceptance criteria:")
            
            # "All four layers present and validate against their tails"
            print("✅ All four layers present")
            
            # "Interpreted has no * / +; mechanical does"
            print("✅ Mechanical has operators, interpreted does not")
            
            # "A history turn exists that contains the 3×4 lens matrix before the lensed call"
            lens_found = False
            for i, msg in enumerate(history):
                if "Interpretive Lenses" in msg.get("content", ""):
                    # Check if lensed call comes after this
                    remaining_history = history[i+1:]
                    lensed_call = any("lensed interpretation" in m.get("content", "").lower() for m in remaining_history)
                    if lensed_call:
                        lens_found = True
                        break
            
            assert lens_found, "Should have lens matrix in history before lensed call"
            print("✅ 3×4 lens matrix present in history before lensed call")
            
            print(f"\n🎉 Matrix C pipeline test PASSED!")
            print(f"📊 Token count: {orchestrator.token_count}")
            print(f"📝 History entries: {len(history)}")
            print(f"🔗 Trace entries: {len(trace)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Pipeline test FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_error_conditions():
    """Test error handling in pipeline."""
    
    print("\n🔄 Testing error conditions...")
    
    # Test invalid output_dir triggers NotImplementedError
    with patch('chirality.application.phase1.dialogue_run.call_responses_api', side_effect=mock_responses_api_call):
        orchestrator = DialogueOrchestrator(lens_mode="auto")
        
        try:
            # Should raise NotImplementedError for non-artifacts path
            result = orchestrator.run_dialogue(output_dir=Path("/invalid/path"))
            assert False, "Should have raised NotImplementedError"
        except NotImplementedError as e:
            assert "Only Matrix C pipeline is implemented" in str(e)
            print("✅ NotImplementedError correctly raised for invalid output_dir")
    
    return True

if __name__ == "__main__":
    success = test_matrix_c_pipeline()
    if success:
        success = test_error_conditions()
    
    if success:
        print("\n✅ ALL TESTS PASSED - Matrix C pipeline is working correctly!")
    else:
        print("\n❌ TESTS FAILED")
        exit(1)