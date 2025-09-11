#!/usr/bin/env python3
"""
Test D2-1: Stage-3 refactor validation.

Tests the canonical BEGIN/END lens block format:
- role="user" (not system)
- BEGIN/END markers present
- Exact JSON equality with source
- turn_type:"data" in trace
"""

import json
import tempfile
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
    return True  # Proceed with mocking

def mock_responses_api_call(messages, temperature=1.0, json_only=True):
    """Mock OpenAI Responses API for testing."""
    return {"content": json.dumps({"name": "C", "elements": [["test"]]})}

def test_lens_block_format():
    """Test D2-1: Canonical lens block format validation."""
    
    print("🔄 Testing D2-1: Canonical lens block format...")
    
    load_api_key()
    
    with patch('chirality.application.phase1.dialogue_run.call_responses_api', side_effect=mock_responses_api_call):
        orchestrator = DialogueOrchestrator(
            model="gpt-5-nano",
            temperature=1.0,
            lens_mode="auto"
        )
        
        # Run dialogue to get lens injection
        result = orchestrator.run_dialogue()
        history = orchestrator.dialogue_history
        
        # Find the lens injection turn
        lens_turn = None
        lens_turn_index = -1
        
        for i, turn in enumerate(history):
            content = turn.get("content", "")
            if "<<<BEGIN LENS MATRIX>>>" in content:
                lens_turn = turn
                lens_turn_index = i
                break
        
        assert lens_turn is not None, "Lens injection turn not found"
        
        # Test 1: role="user" (not system)
        assert lens_turn["role"] == "user", f"Expected role=user, got {lens_turn['role']}"
        print("✅ Lens injection uses role=user")
        
        # Test 2: BEGIN/END markers present
        content = lens_turn["content"]
        assert "<<<BEGIN LENS MATRIX>>>" in content, "Missing BEGIN marker"
        assert "<<<END LENS MATRIX>>>" in content, "Missing END marker"
        print("✅ BEGIN/END markers present")
        
        # Test 3: Parse the lens block content
        begin_marker = "<<<BEGIN LENS MATRIX>>>"
        end_marker = "<<<END LENS MATRIX>>>"
        
        begin_idx = content.find(begin_marker) + len(begin_marker)
        end_idx = content.find(end_marker)
        block_content = content[begin_idx:end_idx].strip()
        
        # Parse the YAML-like structure
        lines = block_content.split('\n')
        parsed_block = {}
        current_section = None
        
        for line in lines:
            if ':' in line:
                if line.startswith(' ') or line.startswith('\t'):
                    # Indented line - belongs to meta section
                    if current_section == "meta":
                        clean_line = line.strip()
                        if ':' in clean_line:
                            sub_key, sub_value = clean_line.split(':', 1)
                            sub_key = sub_key.strip()
                            sub_value = sub_value.strip()
                            parsed_block['meta'][sub_key] = sub_value
                else:
                    # Top-level line
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in ["rows", "cols", "lenses_json"]:
                        # Parse JSON values
                        try:
                            parsed_block[key] = json.loads(value)
                        except json.JSONDecodeError:
                            parsed_block[key] = value
                    elif key == "meta":
                        parsed_block[key] = {}
                        current_section = "meta"
                    else:
                        parsed_block[key] = value
                        current_section = None
        
        # Test 4: Required fields present
        required_fields = ["matrix", "station", "rows", "cols", "source", "meta", "lenses_json"]
        for field in required_fields:
            assert field in parsed_block, f"Missing required field: {field}"
        
        # Test 5: Meta fields present
        required_meta = ["system_sha", "normative_sha", "asset_sha"]
        for meta_field in required_meta:
            assert meta_field in parsed_block["meta"], f"Missing meta field: {meta_field}"
        
        print("✅ All required fields present")
        
        # Test 6: Values match expected types
        assert parsed_block["matrix"] == "C", f"Expected matrix=C, got {parsed_block['matrix']}"
        assert parsed_block["station"] == "Problem Statement", f"Expected station='Problem Statement', got {parsed_block['station']}"
        assert isinstance(parsed_block["rows"], list), "rows should be a list"
        assert isinstance(parsed_block["cols"], list), "cols should be a list"
        assert isinstance(parsed_block["lenses_json"], list), "lenses_json should be a list"
        assert parsed_block["source"] in ["catalog", "override", "auto"], f"Invalid source: {parsed_block['source']}"
        
        print("✅ Field types and values validated")
        
        # Test 7: Exact JSON equality with source lenses
        matrix_c = result["matrices"]["C"]
        source_lenses = matrix_c["lenses"]["lenses"]
        block_lenses = parsed_block["lenses_json"]
        
        assert source_lenses == block_lenses, "Lens block JSON should exactly match source lenses"
        print("✅ Exact JSON equality with source")
        
        # Test 8: Trace entry has turn_type:"data"
        trace = result["trace"]
        lens_trace = None
        
        for entry in trace:
            if entry.get("type") == "lens_injection":
                lens_trace = entry
                break
        
        assert lens_trace is not None, "Lens injection trace entry not found"
        assert lens_trace.get("turn_type") == "data", f"Expected turn_type=data, got {lens_trace.get('turn_type')}"
        print("✅ Trace entry marked as turn_type=data")
        
        # Test 9: Provenance metadata in trace
        assert "meta" in lens_trace, "Trace should have meta field"
        trace_meta = lens_trace["meta"]
        assert "system_sha" in trace_meta, "Trace meta should have system_sha"
        assert "normative_sha" in trace_meta, "Trace meta should have normative_sha"
        assert "asset_sha" in trace_meta, "Trace meta should have asset_sha"
        print("✅ Provenance metadata in trace")
        
        print(f"\n🎉 D2-1 CANONICAL LENS BLOCK VALIDATION PASSED!")
        print(f"   Lens turn at position: {lens_turn_index}")
        print(f"   Source: {parsed_block['source']}")
        print(f"   Matrix dimensions: {len(parsed_block['rows'])}×{len(parsed_block['cols'])}")
        print(f"   System SHA: {parsed_block['meta']['system_sha']}")
        
        return True

def test_lens_block_parsing():
    """Test lens block can be parsed unambiguously."""
    
    print("\n🔄 Testing lens block parsing...")
    
    # Test with example block
    test_block = """<<<BEGIN LENS MATRIX>>>
matrix: C
station: Problem Statement
rows: ["normative", "operative", "iterative"]
cols: ["guiding", "applying", "judging", "reflecting"]
source: catalog
meta:
  system_sha: abc123
  normative_sha: def456
  asset_sha: ghi789
lenses_json: [["lens1", "lens2"], ["lens3", "lens4"]]
<<<END LENS MATRIX>>>"""
    
    # Parse it
    begin_marker = "<<<BEGIN LENS MATRIX>>>"
    end_marker = "<<<END LENS MATRIX>>>"
    
    begin_idx = test_block.find(begin_marker) + len(begin_marker)
    end_idx = test_block.find(end_marker)
    block_content = test_block[begin_idx:end_idx].strip()
    
    # Should be parseable (use same logic as main test)
    lines = block_content.split('\n')
    parsed = {}
    current_section = None
    
    for line in lines:
        if ':' in line:
            if line.startswith(' ') or line.startswith('\t'):
                # Indented line - belongs to meta section
                if current_section == "meta":
                    clean_line = line.strip()
                    if ':' in clean_line:
                        sub_key, sub_value = clean_line.split(':', 1)
                        sub_key = sub_key.strip()
                        sub_value = sub_value.strip()
                        parsed['meta'][sub_key] = sub_value
            else:
                # Top-level line
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key in ["rows", "cols", "lenses_json"]:
                    parsed[key] = json.loads(value)
                elif key == "meta":
                    parsed[key] = {}
                    current_section = "meta"
                else:
                    parsed[key] = value
                    current_section = None
    
    # Validate parsed content
    assert parsed["matrix"] == "C"
    assert parsed["rows"] == ["normative", "operative", "iterative"]
    assert parsed["lenses_json"] == [["lens1", "lens2"], ["lens3", "lens4"]]
    assert parsed["meta"]["system_sha"] == "abc123"
    
    print("✅ Lens block parsing works correctly")
    return True

if __name__ == "__main__":
    success = test_lens_block_format()
    if success:
        success = test_lens_block_parsing()
    
    if success:
        print("\n✅ ALL D2-1 LENS BLOCK TESTS PASSED!")
    else:
        print("\n❌ D2-1 TESTS FAILED")
        exit(1)