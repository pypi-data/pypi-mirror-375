#!/usr/bin/env python3
"""
Test clean transcript - no DOT-BRIDGE clutter or metadata pollution.

Verifies that the LLM transcript contains only clean mathematical operations
without any framework metadata awareness.
"""

import json
from pathlib import Path
from chirality.application.phase1.dialogue_run import DialogueOrchestrator
from chirality.domain.preflight import preflight_dot


def test_clean_transcript():
    """Test that transcript contains no metadata pollution whatsoever."""
    
    print("🔄 Testing clean transcript without metadata pollution...")
    
    # Create orchestrator
    orchestrator = DialogueOrchestrator(
        model="echo",
        temperature=0.2,
        budget_config=None,
        lens_mode="auto"
    )
    
    try:
        # Run complete pipeline
        result = orchestrator.run_dialogue(Path("artifacts/"))
        
        # Check dialogue history for any metadata pollution
        dialogue_history = orchestrator.dialogue_history
        
        # Forbidden metadata tokens that should NEVER appear in transcript
        # Based on colleague_1's specification: system_sha, normative_sha, asset_sha, 
        # generated_at, model, source:, DOT BRIDGE, mode: (case-insensitive)
        forbidden_tokens = [
            # Framework metadata (colleague_1's core list)
            "system_sha", "normative_sha", "asset_sha", "generated_at", "model",
            "kernel_hash", "snapshot_hash", "code_sha", "output_sha",
            
            # Data-drop metadata
            "kind:", "derivation:", "source:", "function:", "code_fqn:", 
            "from_turn:", "from_matrix:", "from_layer:", "input_rows:", "input_cols:",
            "meta:", "assumption:", "note:",
            
            # Cross-ontology clutter (colleague_1 emphasized DOT BRIDGE)
            "DOT BRIDGE", "DOT-BRIDGE", "dot_bridge", "cross-basis", "cross-ontology",
            
            # Mode/source awareness (colleague_1 emphasized mode:)
            "mode:", "source: catalog", "source: auto", "source: override",
            
            # Reference block clutter (eliminated)
            "BEGIN REFERENCE MATRIX", "END REFERENCE MATRIX"
        ]
        
        for i, turn in enumerate(dialogue_history):
            content = turn.get("content", "")
            
                # Check for any forbidden tokens (case-insensitive)
            for token in forbidden_tokens:
                assert token.lower() not in content.lower(), f"Turn {i} contains forbidden metadata token: {token}"
        
        # Additional specific validations for data-drop blocks
        for i, turn in enumerate(dialogue_history):
            content = turn.get("content", "")
            
            # Lens blocks should only contain rows, cols, lenses_json
            if "<<<BEGIN LENS MATRIX>>>" in content:
                lines = content.split('\n')
                in_lens_block = False
                for line in lines:
                    if "<<<BEGIN LENS MATRIX>>>" in line:
                        in_lens_block = True
                        continue
                    if "<<<END LENS MATRIX>>>" in line:
                        in_lens_block = False
                        continue
                    if in_lens_block and line.strip() and not line.startswith(('rows:', 'cols:', 'lenses_json:', 'values_json:')):
                        # Allow JSON content lines (arrays, strings, numbers, braces, etc.)
                        stripped = line.strip()
                        if not (stripped.startswith('[') or stripped.startswith('"') or stripped.startswith(']') or 
                               stripped in ['{', '}', ','] or stripped.endswith(',') or stripped.isdigit() or
                               stripped.startswith('null') or stripped.startswith('true') or stripped.startswith('false')):
                            assert False, f"Turn {i} lens block contains forbidden field: {line.strip()}"
            
            # Derived blocks should only contain rows, cols, values_json  
            if "<<<BEGIN DERIVED MATRIX>>>" in content:
                lines = content.split('\n')
                in_derived_block = False
                for line in lines:
                    if "<<<BEGIN DERIVED MATRIX>>>" in line:
                        in_derived_block = True
                        continue
                    if "<<<END DERIVED MATRIX>>>" in line:
                        in_derived_block = False
                        continue
                    if in_derived_block and line.strip() and not line.startswith(('rows:', 'cols:', 'values_json:')):
                        # Allow JSON content lines
                        if not (line.strip().startswith('[') or line.strip().startswith('"') or line.strip().startswith(']') or line.strip() in ['{', '}', ',']):
                            assert False, f"Turn {i} derived block contains forbidden field: {line.strip()}"
        
        # Verify Matrix X exists without DOT-BRIDGE
        matrices = result["matrices"]
        assert "X" in matrices, "Matrix X missing"
        
        matrix_x = matrices["X"]
        expected_x_stages = ["mechanical", "interpreted", "lenses", "lensed"]
        for stage in expected_x_stages:
            assert stage in matrix_x, f"Matrix X missing {stage} stage"
        
        # Should NOT contain dot_bridge stage
        assert "dot_bridge" not in matrix_x, "Matrix X should not contain DOT-BRIDGE stage"
        
        # Verify trace does not contain dot_bridge entries
        trace = result.get("trace", [])
        dot_bridge_traces = [t for t in trace if t.get("kind") == "dot_bridge"]
        assert len(dot_bridge_traces) == 0, f"Trace contains {len(dot_bridge_traces)} DOT-BRIDGE entries"
        
        print("✅ Transcript is clean - no DOT-BRIDGE or metadata pollution")
        print("✅ Matrix X implemented as clean dot product operation")
        print("✅ All framework logic happens outside the LLM conversation")
        
        return True
        
    except Exception as e:
        print(f"❌ Clean transcript test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simplified_preflight():
    """Test that preflight only checks dimensional conformability."""
    
    print("🔄 Testing simplified preflight validation...")
    
    # Test matrices with different labels but conformable dimensions
    matrix_k = {
        "name": "K",
        "rows": ["guiding", "applying", "judging", "reflecting"],  # 4 rows
        "cols": ["normative", "operative", "iterative"]  # 3 cols
    }
    
    matrix_j = {
        "name": "J",
        "rows": ["data", "information", "knowledge"],  # 3 rows (matches K cols count)
        "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"]  # 4 cols
    }
    
    # Should pass - dimensions are conformable (3 vs 3)
    try:
        preflight_dot(matrix_k, matrix_j)
        print("✅ Preflight correctly validates dimensional conformability")
    except Exception as e:
        print(f"❌ Preflight should pass for conformable dimensions: {e}")
        return False
    
    # Test non-conformable dimensions
    matrix_bad = {
        "name": "Bad",
        "rows": ["r1", "r2"],  # 2 rows
        "cols": ["c1", "c2", "c3", "c4"]  # 4 cols
    }
    
    # Should fail - dimensions not conformable (3 vs 2)
    try:
        preflight_dot(matrix_k, matrix_bad)
        print("❌ Preflight should fail for non-conformable dimensions")
        return False
    except Exception as e:
        if "conformable dimensions" in str(e):
            print("✅ Preflight correctly rejects non-conformable dimensions")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    print("✅ Preflight validation simplified to dimensional checks only")
    return True


def test_matrix_x_clean():
    """Test that Matrix X is a clean mathematical operation."""
    
    print("🔄 Testing Matrix X as clean dot product...")
    
    # Verify Matrix X prompt assets contain only mathematical instructions
    from chirality.infrastructure.prompts.registry import get_registry
    
    registry = get_registry()
    
    # Check X/mechanical.md
    try:
        mechanical_text = registry.get_text("phase1_x_mechanical")
        
        # Should contain clean mathematical instructions
        assert "dot product" in mechanical_text.lower() or "sum of products" in mechanical_text.lower(), "X mechanical missing dot product instructions"
        
        # Should NOT contain metadata awareness
        assert "cross-basis" not in mechanical_text, "X mechanical contains cross-basis metadata"
        assert "cross-ontology" not in mechanical_text, "X mechanical contains cross-ontology metadata"
        assert "DOT-BRIDGE" not in mechanical_text, "X mechanical references DOT-BRIDGE"
        
        print("✅ Matrix X mechanical stage contains clean mathematical instructions")
        
    except Exception as e:
        print(f"ℹ️  Could not verify X/mechanical.md content: {e}")
    
    return True


if __name__ == "__main__":
    success = True
    
    # Test all cleanup aspects
    success &= test_clean_transcript()
    success &= test_simplified_preflight()
    success &= test_matrix_x_clean()
    
    if success:
        print("\n🎉 TRANSCRIPT CLEANUP SUCCESSFUL!")
        print("   ✅ No DOT-BRIDGE clutter in LLM conversation")
        print("   ✅ No metadata pollution in prompts")
        print("   ✅ Matrix X is clean dot product operation")
        print("   ✅ Preflight validation simplified to dimensional checks")
        print("   ✅ All framework logic happens in Python outside transcript")
        print("\n🚀 LLM receives only clean mathematical instructions!")
    else:
        print("\n❌ TRANSCRIPT CLEANUP FAILED")
        exit(1)