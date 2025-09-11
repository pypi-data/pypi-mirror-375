#!/usr/bin/env python3
"""
Test P0-3: Strict Structured Outputs with JSON Schema.

Per colleague_1's specification: "Wherever a stage has a schema, pass 
response_format={"type":"json_schema", "json_schema": <tail>} and validate 
the model's output against that schema in-code."
"""

import json
from chirality.infrastructure.validation.json_schema_converter import (
    convert_contract_to_json_schema,
    get_strict_response_format,
    validate_stage_response_strict
)


def test_json_schema_conversion():
    """Test conversion of JSON tail contracts to JSON Schema format."""
    
    print("🔄 Testing JSON schema conversion...")
    
    # Test C/mechanical conversion
    schema = convert_contract_to_json_schema("C", "mechanical")
    
    # Verify schema structure
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema
    assert schema["additionalProperties"] == False
    
    # Verify required fields are present
    required_fields = {"artifact", "name", "station", "step", "op", "elements"}
    assert set(schema["required"]) >= required_fields
    
    # Verify name is constrained to matrix
    assert schema["properties"]["name"]["enum"] == ["C"]
    
    # Verify step is constrained
    assert schema["properties"]["step"]["enum"] == ["mechanical"]
    
    print("  ✅ Schema conversion works correctly")


def test_response_format_generation():
    """Test generation of OpenAI response_format parameter."""
    
    print("🔄 Testing response format generation...")
    
    # Test C/mechanical response format
    response_format = get_strict_response_format("C", "mechanical")
    
    # Verify OpenAI format structure
    assert response_format["type"] == "json_schema"
    assert "json_schema" in response_format
    
    json_schema = response_format["json_schema"]
    assert "name" in json_schema
    assert "description" in json_schema
    assert "schema" in json_schema
    assert json_schema.get("strict") == True
    
    # Verify schema content
    schema = json_schema["schema"]
    assert schema["type"] == "object"
    assert "properties" in schema
    assert schema.get("additionalProperties") == False
    
    print("  ✅ Response format generation works correctly")


def test_schema_validation():
    """Test validation of responses against strict schemas."""
    
    print("🔄 Testing schema validation...")
    
    # Valid response for C/mechanical
    valid_response = {
        "artifact": "matrix",
        "name": "C",
        "station": "problem statement",
        "rows": ["normative", "operative", "iterative"],
        "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
        "step": "mechanical",
        "op": "dot",
        "elements": [
            ["a", "b", "c", "d"],
            ["e", "f", "g", "h"],
            ["i", "j", "k", "l"]
        ]
    }
    
    is_valid, errors = validate_stage_response_strict(valid_response, "C", "mechanical")
    assert is_valid, f"Valid response failed validation: {errors}"
    assert len(errors) == 0
    
    print("  ✅ Valid response passes validation")
    
    # Invalid response - missing required field
    invalid_response = {
        "artifact": "matrix",
        "name": "C",
        "station": "problem statement",
        # Missing "step" field
        "op": "dot",
        "elements": [["a", "b"]]
    }
    
    is_valid, errors = validate_stage_response_strict(invalid_response, "C", "mechanical")
    assert not is_valid, "Invalid response should fail validation"
    assert len(errors) > 0
    assert any("step" in error for error in errors)
    
    print("  ✅ Invalid response correctly fails validation")
    
    # Invalid response - wrong matrix name
    wrong_matrix = valid_response.copy()
    wrong_matrix["name"] = "D"  # Wrong matrix
    
    is_valid, errors = validate_stage_response_strict(wrong_matrix, "C", "mechanical")
    assert not is_valid, "Wrong matrix name should fail validation"
    assert any("name" in error for error in errors)
    
    print("  ✅ Wrong matrix name correctly fails validation")


def test_strict_vs_basic_format():
    """Test that strict format is more restrictive than basic json_object."""
    
    print("🔄 Testing strict vs basic format...")
    
    # Get both formats
    strict_format = get_strict_response_format("C", "mechanical")
    basic_format = {"type": "json_object"}
    
    # Strict format should be json_schema, not json_object
    assert strict_format["type"] == "json_schema"
    assert basic_format["type"] == "json_object"
    
    # Strict format should have detailed schema
    assert "json_schema" in strict_format
    assert "schema" in strict_format["json_schema"]
    
    # Basic format should be minimal
    assert len(basic_format) == 1
    
    print("  ✅ Strict format is properly differentiated from basic format")


def test_matrix_specific_schemas():
    """Test that different matrices get different schemas."""
    
    print("🔄 Testing matrix-specific schemas...")
    
    # Get schemas for different matrices
    c_schema = convert_contract_to_json_schema("C", "mechanical")
    f_schema = convert_contract_to_json_schema("F", "mechanical")
    
    # Names should be different
    assert c_schema["properties"]["name"]["enum"] == ["C"]
    assert f_schema["properties"]["name"]["enum"] == ["F"]
    
    # Operations should be different (C uses dot, F uses hadamard)
    assert c_schema["properties"]["op"]["enum"] == ["dot"]
    assert f_schema["properties"]["op"]["enum"] == ["hadamard"]
    
    print("  ✅ Matrix-specific schemas work correctly")


def test_fallback_behavior():
    """Test fallback to basic JSON when no schema is available."""
    
    print("🔄 Testing fallback behavior...")
    
    # Try to get schema for non-existent matrix/step
    response_format = get_strict_response_format("NONEXISTENT", "unknown")
    
    # Should fallback to basic JSON object
    assert response_format == {"type": "json_object"}
    
    print("  ✅ Fallback behavior works correctly")


if __name__ == "__main__":
    print("🚀 Testing P0-3: Strict Structured Outputs with JSON Schema...")
    
    try:
        test_json_schema_conversion()
        test_response_format_generation()
        test_schema_validation()
        test_strict_vs_basic_format()
        test_matrix_specific_schemas()
        test_fallback_behavior()
        
        print("\n✅ ALL P0-3 STRICT STRUCTURED OUTPUTS TESTS PASSED!")
        print("✅ JSON tail contracts convert to proper JSON Schema")
        print("✅ OpenAI response_format uses json_schema with strict mode")
        print("✅ In-code validation enforces schema compliance")
        print("✅ Matrix-specific schemas provide precise constraints")
        print("✅ Graceful fallback for unknown matrix/step combinations")
        print("✅ Ready for production with strict output validation")
        
    except Exception as e:
        print(f"\n❌ P0-3 STRICT STRUCTURED OUTPUTS TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)