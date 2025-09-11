"""
Test Phase 1 contracts and aggregator output.

Validates that Phase 1 produces the expected phase1_output.json structure
and that it passes Pydantic validation.
"""

import pytest
import json
from pathlib import Path

from chirality.application.phase1.contracts import Phase1Output


def test_phase1_output_schema_validation(sample_phase1_output):
    """Test that sample output validates against Phase1Output schema."""
    # This should not raise any validation errors
    validated = Phase1Output.model_validate(sample_phase1_output)

    # Verify key fields are present
    assert validated.meta.kernel_hash == "abc123def456"
    assert validated.meta.snapshot_hash == "xyz789uvw123"
    assert validated.meta.model == "gpt-4"

    assert "A" in validated.matrices
    assert "B" in validated.matrices

    assert validated.principles.from_ == "Matrix E"
    assert len(validated.principles.items) == 2


def test_phase1_output_required_fields():
    """Test that missing required fields raise validation errors."""
    incomplete_output = {
        "meta": {
            "kernel_hash": "abc123"
            # missing snapshot_hash and model
        },
        "matrices": {},
        "principles": {"from": "Matrix E", "items": []},
    }

    with pytest.raises(ValueError):  # Pydantic validation error
        Phase1Output.model_validate(incomplete_output)


def test_phase1_output_json_serialization(sample_phase1_output):
    """Test that validated output can be serialized back to JSON."""
    validated = Phase1Output.model_validate(sample_phase1_output)

    # Should serialize cleanly
    json_str = validated.model_dump_json(indent=2)

    # Should be valid JSON
    parsed = json.loads(json_str)

    # Key fields should be preserved
    assert parsed["meta"]["kernel_hash"] == "abc123def456"
    assert "A" in parsed["matrices"]
    assert "B" in parsed["matrices"]


def test_matrix_step_field(sample_phase1_output):
    """Test that matrix step field is properly validated."""
    validated = Phase1Output.model_validate(sample_phase1_output)

    # Step should be one of the allowed literals
    assert validated.matrices["A"].step == "base"
    assert validated.matrices["B"].step == "base"

    # Test invalid step
    invalid_output = sample_phase1_output.copy()
    invalid_output["matrices"]["A"]["step"] = "invalid_step"

    with pytest.raises(ValueError):
        Phase1Output.model_validate(invalid_output)


def test_principles_alias_handling(sample_phase1_output):
    """Test that 'from' field alias works correctly."""
    validated = Phase1Output.model_validate(sample_phase1_output)

    # Should access via alias
    assert validated.principles.from_ == "Matrix E"

    # Should serialize with original field name
    json_dict = validated.model_dump(by_alias=True)
    assert json_dict["principles"]["from"] == "Matrix E"


# Integration test for file-based validation
def test_phase1_output_file_validation(temp_artifacts_dir, sample_phase1_output):
    """Test validating a phase1_output.json file from disk."""
    output_file = temp_artifacts_dir / "phase1_output.json"

    # Write sample output to file
    with open(output_file, "w") as f:
        json.dump(sample_phase1_output, f, indent=2)

    # Read and validate from file
    with open(output_file) as f:
        file_data = json.load(f)

    validated = Phase1Output.model_validate(file_data)

    # Should match original data
    assert validated.meta.kernel_hash == sample_phase1_output["meta"]["kernel_hash"]
    assert len(validated.matrices) == len(sample_phase1_output["matrices"])
