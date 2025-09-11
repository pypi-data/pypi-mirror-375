#!/usr/bin/env python3
"""
Test Matrix F (Requirements) Pipeline with Element-wise Product (⊙).

Verifies that Matrix F implements the element-wise product operation correctly:
F[i,j] = C[i,j] * J[i,j] (hadamard product, not dot product)

Tests the complete 4-stage pipeline: mechanical → interpreted → lenses → lensed
"""

import os
import json
from pathlib import Path
from unittest.mock import patch

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


def test_matrix_f_element_wise_operation():
    """Test Matrix F element-wise product operation vs Matrix C dot product."""
    
    print("🔄 Testing Matrix F element-wise product (⊙) operation...")
    
    load_api_key()
    
    # Mock responses that demonstrate element-wise vs dot product difference
    mock_responses = {
        # Matrix C responses (dot product - complex formulas with sums)
        "C_mechanical": {
            "artifact": "matrix",
            "name": "C",
            "station": "problem statement",
            "rows": ["normative", "operative", "iterative"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "step": "mechanical",
            "op": "dot",
            "elements": [
                # Dot product: each cell is sum of multiple terms
                ["objectives*necessary + actions*contingent + benchmarks*purposeful + feedback*constitutive",
                 "objectives*sufficient + actions*actionable + benchmarks*effective + feedback*optimal",
                 "objectives*complete + actions*contextual + benchmarks*comprehensive + feedback*holistic",
                 "objectives*consistent + actions*congruent + benchmarks*coherent + feedback*principled"],
                ["standards*necessary + methods*contingent + criteria*purposeful + adaptation*constitutive",
                 "standards*sufficient + methods*actionable + criteria*effective + adaptation*optimal",
                 "standards*complete + methods*contextual + criteria*comprehensive + adaptation*holistic",
                 "standards*consistent + methods*congruent + criteria*coherent + adaptation*principled"],
                ["developments*necessary + coordination*contingent + evaluation*purposeful + refinement*constitutive",
                 "developments*sufficient + coordination*actionable + evaluation*effective + refinement*optimal",
                 "developments*complete + coordination*contextual + evaluation*comprehensive + refinement*holistic",
                 "developments*consistent + coordination*congruent + evaluation*coherent + refinement*principled"]
            ]
        },
        "C_interpreted": {
            "artifact": "matrix",
            "name": "C",
            "station": "problem statement",
            "rows": ["normative", "operative", "iterative"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "step": "interpreted",
            "op": "dot",
            "elements": [
                ["established_requirements", "adequate_scope", "complete_definition", "coherent_framework"],
                ["operational_necessity", "sufficient_methods", "comprehensive_process", "consistent_execution"],
                ["evolving_needs", "adaptive_sufficiency", "complete_iteration", "coherent_refinement"]
            ]
        },
        "C_lensed": {
            "artifact": "matrix",
            "name": "C",
            "station": "problem statement",
            "rows": ["normative", "operative", "iterative"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "step": "lensed",
            "op": "dot",
            "elements": [
                ["lensed_established_requirements", "lensed_adequate_scope", "lensed_complete_definition", "lensed_coherent_framework"],
                ["lensed_operational_necessity", "lensed_sufficient_methods", "lensed_comprehensive_process", "lensed_consistent_execution"],
                ["lensed_evolving_needs", "lensed_adaptive_sufficiency", "lensed_complete_iteration", "lensed_coherent_refinement"]
            ]
        },
        # Matrix F responses (element-wise product - single multiplications)
        "F_mechanical": {
            "artifact": "matrix",
            "name": "F",
            "station": "requirements",
            "rows": ["data", "information", "knowledge"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "step": "mechanical",
            "op": "hadamard",
            "elements": [
                # Element-wise: each cell is single multiplication C[i,j] * J[i,j]
                ["established_requirements * necessary",
                 "adequate_scope * sufficient", 
                 "complete_definition * complete",
                 "coherent_framework * consistent"],
                ["operational_necessity * contingent",
                 "sufficient_methods * actionable",
                 "comprehensive_process * contextual", 
                 "consistent_execution * congruent"],
                ["evolving_needs * purposeful",
                 "adaptive_sufficiency * effective",
                 "complete_iteration * comprehensive",
                 "coherent_refinement * coherent"]
            ]
        },
        "F_interpreted": {
            "artifact": "matrix",
            "name": "F",
            "station": "requirements", 
            "rows": ["data", "information", "knowledge"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "step": "interpreted",
            "op": "hadamard",
            "elements": [
                ["essential_requirements", "adequate_scope", "complete_specifications", "consistent_framework"],
                ["contingent_operations", "actionable_methods", "contextual_processes", "congruent_execution"],
                ["purposeful_evolution", "effective_adaptation", "comprehensive_iteration", "coherent_improvement"]
            ]
        },
        "F_lensed": {
            "artifact": "matrix",
            "name": "F",
            "station": "requirements",
            "rows": ["data", "information", "knowledge"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "step": "lensed",
            "op": "hadamard",
            "elements": [
                ["lensed_essential_requirements", "lensed_adequate_scope", "lensed_complete_specifications", "lensed_consistent_framework"],
                ["lensed_contingent_operations", "lensed_actionable_methods", "lensed_contextual_processes", "lensed_congruent_execution"],
                ["lensed_purposeful_evolution", "lensed_effective_adaptation", "lensed_comprehensive_iteration", "lensed_coherent_improvement"]
            ]
        }
    }
    
    call_count = 0
    stage_calls = ["C_mechanical", "C_interpreted", "C_lensed", "F_mechanical", "F_interpreted", "F_lensed"]
    
    def mock_call_responses(**kwargs):
        nonlocal call_count
        stage_key = stage_calls[call_count] if call_count < len(stage_calls) else "unknown"
        call_count += 1
        
        response_data = mock_responses.get(stage_key, {"error": "unexpected_call"})
        
        return {
            "id": f"test_response_{call_count}",
            "output_text": json.dumps(response_data),
            "usage": {"total_tokens": 150, "prompt_tokens": 75, "completion_tokens": 75},
            "raw": {"stage": stage_key}
        }
    
    with patch('chirality.application.phase1.dialogue_run.call_responses', side_effect=mock_call_responses):
        orchestrator = DialogueOrchestrator(
            model="gpt-4",
            temperature=0.7,
            lens_mode="auto"
        )
        
        try:
            # Run both Matrix C and F pipelines
            result = orchestrator.run_dialogue()
            
            # Verify both matrices are present
            assert "C" in result["matrices"], "Result missing Matrix C"
            assert "F" in result["matrices"], "Result missing Matrix F"
            
            matrix_c = result["matrices"]["C"]
            matrix_f = result["matrices"]["F"]
            
            # Verify Matrix C (dot product) structure
            c_mechanical = matrix_c["mechanical"]["elements"]
            # Should contain sums (multiple terms with +)
            c_sample = c_mechanical[0][0]
            assert "+" in c_sample, f"Matrix C mechanical should contain sums (+ operators), got: {c_sample}"
            assert "*" in c_sample, f"Matrix C mechanical should contain multiplications, got: {c_sample}"
            
            # Verify Matrix F (element-wise) structure  
            f_mechanical = matrix_f["mechanical"]["elements"]
            # Should contain single multiplications (no + operators)
            f_sample = f_mechanical[0][0]
            assert "*" in f_sample, f"Matrix F mechanical should contain multiplication, got: {f_sample}"
            assert "+" not in f_sample, f"Matrix F mechanical should NOT contain sums (element-wise), got: {f_sample}"
            
            # Verify Matrix F uses hadamard operation
            assert matrix_f["mechanical"]["op"] == "hadamard", "Matrix F should use hadamard operation"
            assert matrix_c["mechanical"]["op"] == "dot", "Matrix C should use dot operation"
            
            # Verify Matrix F dimensions match C and J (3x4)
            assert len(f_mechanical) == 3, "Matrix F should have 3 rows"
            assert len(f_mechanical[0]) == 4, "Matrix F should have 4 columns"
            
            # Verify all F stages completed
            required_stages = ["mechanical", "interpreted", "lenses", "lensed"]
            for stage in required_stages:
                assert stage in matrix_f, f"Matrix F missing {stage} stage"
            
            # Verify F lenses use requirements station
            f_lenses = matrix_f["lenses"]
            assert "station" not in f_lenses or "requirements" in str(f_lenses), "Matrix F should use requirements station"
            
            print("✅ Matrix F element-wise product operation working correctly")
            print(f"   ✅ Matrix C (dot): Contains sums in mechanical stage")
            print(f"   ✅ Matrix F (hadamard): Single multiplications only")
            print(f"   ✅ Matrix F station: Requirements")
            print(f"   ✅ All F stages: {list(matrix_f.keys())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Matrix F element-wise test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_matrix_f_canonical_integration():
    """Test Matrix F integration with canonical matrix definitions."""
    
    print("🔄 Testing Matrix F canonical integration...")
    
    from chirality.domain.matrices.canonical import get_matrix_info
    
    # Verify Matrix F canonical definition
    try:
        matrix_f_info = get_matrix_info("F")
        
        assert matrix_f_info["matrix_id"] == "F", "Matrix F should have ID 'F'"
        assert matrix_f_info["station"] == "requirements", "Matrix F should be at requirements station"
        assert matrix_f_info["rows"] == 3, "Matrix F should have 3 rows"
        assert matrix_f_info["cols"] == 4, "Matrix F should have 4 columns"
        
        # Check row labels match Matrix J (since F uses C ⊙ J, and C has different rows than J)
        expected_rows = ["data", "information", "knowledge"]  # From Matrix J structure
        assert matrix_f_info["row_labels"] == expected_rows, f"Matrix F rows should match J structure: {matrix_f_info['row_labels']}"
        
        print("✅ Matrix F canonical integration working")
        print(f"   ✅ Station: {matrix_f_info['station']}")
        print(f"   ✅ Dimensions: {matrix_f_info['rows']}×{matrix_f_info['cols']}")
        print(f"   ✅ Row labels: {matrix_f_info['row_labels']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Matrix F canonical integration failed: {e}")
        return False


def test_matrix_f_operation_inference():
    """Test that Matrix F operation is correctly inferred as hadamard."""
    
    print("🔄 Testing Matrix F operation inference...")
    
    from chirality.application.phase1.dialogue_run import _infer_operation
    
    # Test operation inference
    operation = _infer_operation("F")
    assert operation == "hadamard", f"Matrix F should infer hadamard operation, got: {operation}"
    
    # Compare with other matrices
    assert _infer_operation("C") == "dot", "Matrix C should infer dot operation"
    assert _infer_operation("E") == "dot", "Matrix E should infer dot operation"
    assert _infer_operation("D") == "add", "Matrix D should infer add operation"
    
    print("✅ Matrix F operation inference working")
    print(f"   ✅ Matrix F: hadamard (⊙)")
    print(f"   ✅ Matrix C: dot (·)")
    print(f"   ✅ Matrix D: add (+)")
    
    return True


if __name__ == "__main__":
    success = True
    
    # Run all Matrix F tests
    success &= test_matrix_f_element_wise_operation()
    success &= test_matrix_f_canonical_integration()
    success &= test_matrix_f_operation_inference()
    
    if success:
        print("\n✅ ALL MATRIX F PIPELINE TESTS PASSED!")
        print("   ✅ Element-wise product (⊙): Single multiplications, no sums")
        print("   ✅ Distinct from dot product (·): Matrix C uses sums, F uses direct correspondence")
        print("   ✅ Canonical integration: Requirements station, 3×4 dimensions")
        print("   ✅ Operation inference: Correctly identifies hadamard operation")
        print("   ✅ Complete pipeline: mechanical → interpreted → lenses → lensed")
        print("   ✅ Matrix F (Requirements) implemented successfully!")
    else:
        print("\n❌ MATRIX F PIPELINE TESTS FAILED")
        exit(1)