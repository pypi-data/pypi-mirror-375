"""
Test lens derivation and catalog building.

Validates that lens triples are derived correctly from Phase 1 matrices
and that the lens catalog is built with deterministic lens_ids.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# These imports may need adjustment based on actual implementation
from chirality.infrastructure.lenses.derive import LensDeriver, derive_all_lenses

try:
    from chirality.infrastructure.lenses.build import build_catalog
except ImportError:
    build_catalog = None


@pytest.fixture
def mock_phase1_matrices():
    """Mock Phase 1 matrices for lens derivation testing."""
    return {
        "E": {
            "name": "E",
            "station": "Evaluation",
            "rows": ["normative", "operative", "iterative"],
            "cols": ["guiding", "applying", "judging"],
            "elements": [
                ["eval_norm_guide", "eval_norm_apply", "eval_norm_judge"],
                ["eval_op_guide", "eval_op_apply", "eval_op_judge"],
                ["eval_iter_guide", "eval_iter_apply", "eval_iter_judge"],
            ],
            "step": "lensed",
        },
        "X": {
            "name": "X",
            "station": "Verification",
            "rows": ["data", "information", "knowledge", "wisdom"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "elements": [
                ["x_data_nec", "x_data_suff", "x_data_comp", "x_data_cons"],
                ["x_info_nec", "x_info_suff", "x_info_comp", "x_info_cons"],
                ["x_know_nec", "x_know_suff", "x_know_comp", "x_know_cons"],
                ["x_wisd_nec", "x_wisd_suff", "x_wisd_comp", "x_wisd_cons"],
            ],
            "step": "lensed",
        },
        "P": {
            "name": "P",
            "station": "Validation",
            "rows": ["reflecting"],
            "cols": ["necessity (vs contingency)", "sufficiency", "completeness", "consistency"],
            "elements": [["p_refl_nec", "p_refl_suff", "p_refl_comp", "p_refl_cons"]],
            "step": "constructed",
        },
        "H": {
            "name": "H",
            "station": "Validation",
            "rows": ["consistency_reflecting"],
            "cols": ["value"],
            "elements": [["h_cons_refl"]],
            "step": "constructed",
        },
    }


def test_derive_triples_basic_structure(mock_phase1_matrices, temp_artifacts_dir):
    """Test that derive_all_lenses produces expected output structure."""
    # Mock file I/O for phase1 data
    phase1_file = temp_artifacts_dir / "phase1_output.json"
    with open(phase1_file, "w") as f:
        json.dump({"matrices": mock_phase1_matrices}, f)

    spec_file = temp_artifacts_dir / "tensor_spec.json"
    with open(spec_file, "w") as f:
        json.dump({"tensors": [{"matrix_operand": "E"}]}, f)

    output_file = temp_artifacts_dir / "lenses_triples.json"

    # Use actual implementation
    lens_count = derive_all_lenses(
        phase1_output_path=phase1_file,
        tensor_spec_path=spec_file,
        kernel_hash="test_hash",
        model="gpt-4",
        output_path=output_file,
    )

    # Verify output exists
    assert output_file.exists()
    assert lens_count > 0

    with open(output_file) as f:
        data = json.load(f)

    # Should have expected structure
    assert "lens_count" in data
    assert "lenses" in data
    assert isinstance(data["lenses"], list)

    # Each lens should have the expected structure
    if data["lenses"]:
        lens = data["lenses"][0]
        assert "row" in lens
        assert "col" in lens
        assert "station" in lens
        assert "lens_id" in lens


def test_lens_id_deterministic():
    """Test that lens IDs are generated deterministically."""
    # Test data
    row = "normative"
    col = "guiding"
    station = "Evaluation"

    # Generate lens ID twice - should be identical
    deriver1 = LensDeriver("test_hash", "gpt-4")
    deriver2 = LensDeriver("test_hash", "gpt-4")

    id1 = deriver1._compute_lens_id(row, col, station)
    id2 = deriver2._compute_lens_id(row, col, station)

    assert id1 == id2
    assert isinstance(id1, str)
    assert len(id1) > 0


@pytest.mark.skip("Lens catalog builder not yet implemented")
def test_build_catalog_temperature_locked(temp_artifacts_dir):
    """Test that lens catalog building uses locked temperature=0.2."""
    pytest.skip("build_catalog not yet implemented")


@pytest.mark.skip("Lens catalog builder not yet implemented")
def test_catalog_jsonl_format(temp_artifacts_dir):
    """Test that catalog output follows expected JSONL format."""
    pytest.skip("build_catalog not yet implemented")
