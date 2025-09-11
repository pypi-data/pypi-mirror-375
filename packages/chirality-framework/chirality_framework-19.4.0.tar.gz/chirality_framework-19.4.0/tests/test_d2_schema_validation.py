#!/usr/bin/env python3
"""
Test D2-5: Schema validation implementation.

Tests stage response validation and lens payload validation
according to colleague_1's D2-5 specification.
"""

import json
from chirality.infrastructure.validation.schemas import (
    StageResponseValidator,
    LensPayloadValidator,
    validate_stage_response,
    validate_lens_payload,
    SchemaValidationError
)


def test_stage_response_validation():
    """Test D2-5: Stage response validation against JSON tail schemas."""
    
    print("🔄 Testing D2-5: Stage response validation...")
    
    # Test valid Matrix C mechanical response
    valid_c_mechanical = {
        "artifact": "matrix",
        "name": "C",
        "station": "Problem Statement",
        "rows": ["normative", "operative", "iterative"],
        "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
        "step": "mechanical",
        "op": "dot",
        "elements": [
            ["elem1", "elem2", "elem3", "elem4"],
            ["elem5", "elem6", "elem7", "elem8"],
            ["elem9", "elem10", "elem11", "elem12"]
        ]
    }
    
    errors = validate_stage_response(valid_c_mechanical, "C", "mechanical")
    if errors:
        print(f"❌ Valid C/mechanical response failed validation: {errors}")
        return False
    else:
        print("✅ Valid C/mechanical response passed validation")
    
    # Test invalid response - missing required field
    invalid_missing_field = {
        "artifact": "matrix",
        "name": "C",
        # Missing "station" field
        "rows": ["normative", "operative", "iterative"],
        "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
        "step": "mechanical",
        "op": "dot",
        "elements": [["elem1", "elem2", "elem3", "elem4"]]
    }
    
    errors = validate_stage_response(invalid_missing_field, "C", "mechanical")
    if not errors:
        print("❌ Invalid response (missing field) should have failed validation")
        return False
    elif "Missing required field: station" in errors:
        print("✅ Missing field correctly detected")
    else:
        print(f"❌ Wrong error detected for missing field: {errors}")
        return False
    
    # Test invalid response - wrong dimensions
    invalid_dimensions = {
        "artifact": "matrix",
        "name": "C",
        "station": "Problem Statement",
        "rows": ["normative", "operative", "iterative"],
        "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
        "step": "mechanical",
        "op": "dot",
        "elements": [
            ["elem1", "elem2"],  # Too few columns
            ["elem3", "elem4", "elem5", "elem6"],
            ["elem7", "elem8", "elem9", "elem10"]
        ]
    }
    
    errors = validate_stage_response(invalid_dimensions, "C", "mechanical")
    if not errors:
        print("❌ Invalid dimensions should have failed validation")
        return False
    elif any("expected 4 columns" in error for error in errors):
        print("✅ Invalid dimensions correctly detected")
    else:
        print(f"❌ Wrong error detected for dimensions: {errors}")
        return False
    
    return True


def test_lens_payload_validation():
    """Test D2-5: Lens payload validation for canonical BEGIN/END blocks."""
    
    print("🔄 Testing D2-5: Lens payload validation...")
    
    # Test valid lens block
    valid_lens_block = """<<<BEGIN LENS MATRIX>>>
matrix: C
station: Problem Statement
rows: ["normative", "operative", "iterative"]
cols: ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"]
source: catalog
meta:
  system_sha: abc123
  normative_sha: def456
  asset_sha: ghi789
lenses_json: [["lens1", "lens2", "lens3", "lens4"], ["lens5", "lens6", "lens7", "lens8"], ["lens9", "lens10", "lens11", "lens12"]]
<<<END LENS MATRIX>>>"""
    
    errors = validate_lens_payload(valid_lens_block)
    if errors:
        print(f"❌ Valid lens block failed validation: {errors}")
        return False
    else:
        print("✅ Valid lens block passed validation")
    
    # Test invalid lens block - missing BEGIN marker
    invalid_no_begin = """matrix: C
station: Problem Statement
rows: ["normative", "operative", "iterative"]
cols: ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"]
source: catalog
lenses_json: [["lens1", "lens2", "lens3", "lens4"]]
<<<END LENS MATRIX>>>"""
    
    errors = validate_lens_payload(invalid_no_begin)
    if not errors:
        print("❌ Missing BEGIN marker should have failed validation")
        return False
    elif any("must start with" in error for error in errors):
        print("✅ Missing BEGIN marker correctly detected")
    else:
        print(f"❌ Wrong error detected for missing BEGIN: {errors}")
        return False
    
    # Test invalid lens block - dimension mismatch
    invalid_dimensions = """<<<BEGIN LENS MATRIX>>>
matrix: C
station: Problem Statement
rows: ["normative", "operative", "iterative"]
cols: ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"]
source: catalog
meta:
  system_sha: abc123
  normative_sha: def456
  asset_sha: ghi789
lenses_json: [["lens1", "lens2"], ["lens3", "lens4"]]
<<<END LENS MATRIX>>>"""
    
    errors = validate_lens_payload(invalid_dimensions)
    if not errors:
        print("❌ Dimension mismatch should have failed validation")
        return False
    elif any("rows mismatch" in error or "cols mismatch" in error for error in errors):
        print("✅ Dimension mismatch correctly detected")
    else:
        print(f"❌ Wrong error detected for dimensions: {errors}")
        return False
    
    return True


def test_validator_integration():
    """Test D2-5: Validator class integration."""
    
    print("🔄 Testing D2-5: Validator class integration...")
    
    # Test StageResponseValidator
    stage_validator = StageResponseValidator()
    
    # Check that schema patterns were built
    if not stage_validator.schema_patterns:
        print("❌ StageResponseValidator has no schema patterns")
        return False
    
    # Check that we have patterns for key matrix/step combinations
    expected_patterns = [("C", "mechanical"), ("C", "interpreted"), ("C", "lensed")]
    for pattern in expected_patterns:
        if pattern not in stage_validator.schema_patterns:
            print(f"❌ Missing schema pattern for {pattern}")
            return False
    
    print(f"✅ StageResponseValidator loaded {len(stage_validator.schema_patterns)} schema patterns")
    
    # Test LensPayloadValidator
    lens_validator = LensPayloadValidator()
    
    # Test with minimal valid block
    minimal_block = """<<<BEGIN LENS MATRIX>>>
matrix: A
station: Problem Statement
rows: ["r1", "r2"]
cols: ["c1", "c2"]
source: auto
lenses_json: [["l1", "l2"], ["l3", "l4"]]
<<<END LENS MATRIX>>>"""
    
    errors = lens_validator.validate_lens_block(minimal_block)
    if errors:
        print(f"❌ Minimal valid block failed: {errors}")
        return False
    
    print("✅ LensPayloadValidator working correctly")
    
    return True


def test_edge_cases():
    """Test D2-5: Edge cases and error conditions."""
    
    print("🔄 Testing D2-5: Edge cases...")
    
    # Test unknown matrix/step combination
    unknown_response = {"artifact": "matrix", "name": "UNKNOWN"}
    errors = validate_stage_response(unknown_response, "UNKNOWN", "unknown")
    if not errors:
        print("❌ Unknown matrix/step should produce error")
        return False
    elif any("No schema pattern defined" in error for error in errors):
        print("✅ Unknown matrix/step correctly handled")
    else:
        print(f"❌ Wrong error for unknown matrix: {errors}")
        return False
    
    # Test malformed lens block
    malformed_lens = "This is not a lens block at all"
    errors = validate_lens_payload(malformed_lens)
    if not errors:
        print("❌ Malformed lens block should fail validation")
        return False
    else:
        print("✅ Malformed lens block correctly rejected")
    
    # Test empty responses
    empty_response = {}
    errors = validate_stage_response(empty_response, "C", "mechanical")
    if not errors:
        print("❌ Empty response should fail validation")
        return False
    elif len(errors) >= 5:  # Should have many missing field errors
        print("✅ Empty response correctly rejected with multiple errors")
    else:
        print(f"❌ Empty response should have more errors: {errors}")
        return False
    
    return True


def test_matrix_specific_validation():
    """Test D2-5: Matrix-specific validation rules."""
    
    print("🔄 Testing D2-5: Matrix-specific validation...")
    
    # Test Matrix F (hadamard operation)
    valid_f_response = {
        "artifact": "matrix",
        "name": "F",
        "station": "Requirements",
        "rows": ["data", "information", "knowledge"],
        "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
        "step": "mechanical",
        "op": "hadamard",
        "elements": [
            ["elem1", "elem2", "elem3", "elem4"],
            ["elem5", "elem6", "elem7", "elem8"],
            ["elem9", "elem10", "elem11", "elem12"]
        ]
    }
    
    errors = validate_stage_response(valid_f_response, "F", "mechanical")
    if errors:
        print(f"❌ Valid F/mechanical response failed: {errors}")
        return False
    else:
        print("✅ Matrix F validation working")
    
    # Test Matrix E (different dimensions)
    valid_e_response = {
        "artifact": "matrix",
        "name": "E",
        "station": "Evaluation",
        "rows": ["guiding", "applying", "judging"],
        "cols": ["data", "information", "knowledge"],
        "step": "mechanical",
        "op": "dot",
        "elements": [
            ["elem1", "elem2", "elem3"],
            ["elem4", "elem5", "elem6"],
            ["elem7", "elem8", "elem9"]
        ]
    }
    
    errors = validate_stage_response(valid_e_response, "E", "mechanical")
    if errors:
        print(f"❌ Valid E/mechanical response failed: {errors}")
        return False
    else:
        print("✅ Matrix E validation working")
    
    return True


if __name__ == "__main__":
    success = True
    
    # Run all D2-5 schema validation tests
    success &= test_stage_response_validation()
    success &= test_lens_payload_validation()
    success &= test_validator_integration()
    success &= test_edge_cases()
    success &= test_matrix_specific_validation()
    
    if success:
        print("\n✅ ALL D2-5 SCHEMA VALIDATION TESTS PASSED!")
        print("   ✅ Stage response validation: JSON tail schema enforcement")
        print("   ✅ Lens payload validation: Canonical BEGIN/END block format")
        print("   ✅ Validator integration: Schema pattern loading and validation")
        print("   ✅ Edge cases: Unknown matrices, malformed blocks, empty responses")
        print("   ✅ Matrix-specific: Different matrices and operations validated")
    else:
        print("\n❌ D2-5 SCHEMA VALIDATION TESTS FAILED")
        exit(1)