"""
Test resume robustness against file corruption and crashes.

Validates that ResumableRunner can handle corrupted files, partial writes,
and provides atomic file operations.
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

from chirality.infrastructure.caching import ResumableRunner


@pytest.fixture
def temp_artifacts():
    """Create temporary artifacts directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_atomic_cell_write(temp_artifacts):
    """Test that cell writes are atomic (no partial files after crash)."""
    runner = ResumableRunner(temp_artifacts)

    # Save a cell result
    result_data = {"value": "test result", "metadata": {"tokens": 100}}

    runner.save_cell_result("M", (0, 1, 2), result_data)

    # Verify file exists and is complete
    cell_path = runner.compute_cell_path("M", (0, 1, 2))
    assert cell_path.exists()

    # Load and verify integrity
    with open(cell_path) as f:
        loaded_data = json.load(f)

    assert loaded_data["tensor_name"] == "M"
    assert loaded_data["indices"] == [0, 1, 2]
    assert loaded_data["result"] == result_data
    assert "timestamp" in loaded_data


def test_corrupted_cell_file_handling(temp_artifacts):
    """Test that corrupted cell files are handled gracefully."""
    runner = ResumableRunner(temp_artifacts)

    # Create a corrupted cell file
    cell_path = runner.compute_cell_path("M", (0, 0, 0))
    cell_path.parent.mkdir(parents=True, exist_ok=True)

    # Write invalid JSON
    cell_path.write_text("{ invalid json content")

    # Try to load - should return None and clean up
    result = runner.load_cell_result("M", (0, 0, 0))
    assert result is None

    # File should be removed
    assert not cell_path.exists()


def test_partial_file_cleanup_in_completed_cells(temp_artifacts):
    """Test that get_completed_cells skips and cleans corrupted files."""
    runner = ResumableRunner(temp_artifacts)
    tensor_dir = runner.cell_traces_dir / "M"
    tensor_dir.mkdir(parents=True)

    # Create valid cell file
    valid_cell = tensor_dir / "0_1_2.json"
    valid_data = {
        "tensor_name": "M",
        "indices": [0, 1, 2],
        "timestamp": time.time(),
        "result": {"value": "valid"},
    }
    valid_cell.write_text(json.dumps(valid_data))

    # Create corrupted cell file
    corrupted_cell = tensor_dir / "0_1_3.json"
    corrupted_cell.write_text("{ corrupted")

    # Create temporary file (should be ignored)
    temp_file = tensor_dir / ".0_1_4.json_123.tmp"
    temp_file.write_text("temporary content")

    # Get completed cells
    completed = runner.get_completed_cells("M")

    # Only valid cell should be returned
    assert completed == {"0_1_2"}

    # Corrupted file should be removed
    assert not corrupted_cell.exists()

    # Temp file should still exist (not removed)
    assert temp_file.exists()

    # Valid file should still exist
    assert valid_cell.exists()


def test_atomic_manifest_write(temp_artifacts):
    """Test that manifest writes are atomic."""
    runner = ResumableRunner(temp_artifacts)

    # Save initial manifest
    manifest = {"run_id": "test-run", "cells_completed": 5, "phase2_complete": False}

    runner.save_manifest(manifest)

    # Verify file exists and is complete
    assert runner.manifest_path.exists()

    # Load and verify integrity
    loaded_manifest = runner.load_manifest()
    assert loaded_manifest["run_id"] == "test-run"
    assert loaded_manifest["cells_completed"] == 5
    assert loaded_manifest["phase2_complete"] is False


def test_canonical_cell_path_consistency(temp_artifacts):
    """Test that canonical path function is consistent."""
    runner = ResumableRunner(temp_artifacts)

    # Same indices should produce same path
    path1 = runner.compute_cell_path("M", (0, 1, 2))
    path2 = runner.compute_cell_path("M", (0, 1, 2))
    assert path1 == path2

    # Different indices should produce different paths
    path3 = runner.compute_cell_path("M", (0, 1, 3))
    assert path1 != path3

    # Different tensors should produce different paths
    path4 = runner.compute_cell_path("W", (0, 1, 2))
    assert path1 != path4


def test_resume_after_corruption(temp_artifacts):
    """Test full resume workflow with corruption recovery."""
    runner = ResumableRunner(temp_artifacts)

    # Save several cells
    for i in range(5):
        result_data = {"value": f"result_{i}"}
        runner.save_cell_result("M", (0, 0, i), result_data)

    # Corrupt one cell file
    corrupt_path = runner.compute_cell_path("M", (0, 0, 2))
    corrupt_path.write_text("{ invalid")

    # Get completed cells - should skip corrupted one
    completed = runner.get_completed_cells("M")
    expected = {"0_0_0", "0_0_1", "0_0_3", "0_0_4"}  # Missing 0_0_2
    assert completed == expected

    # Corrupted file should be cleaned up
    assert not corrupt_path.exists()

    # Can re-save the corrupted cell
    runner.save_cell_result("M", (0, 0, 2), {"value": "recovered"})

    # Now should be complete
    completed_after = runner.get_completed_cells("M")
    expected_after = {"0_0_0", "0_0_1", "0_0_2", "0_0_3", "0_0_4"}
    assert completed_after == expected_after


def test_concurrent_safety_simulation(temp_artifacts):
    """Test that atomic operations prevent race conditions."""
    runner = ResumableRunner(temp_artifacts)

    # Save same cell multiple times rapidly (simulates concurrent access)
    for i in range(10):
        result_data = {"value": f"version_{i}", "iteration": i}
        runner.save_cell_result("M", (0, 0, 0), result_data)

    # Should have the latest version
    final_result = runner.load_cell_result("M", (0, 0, 0))
    assert final_result["iteration"] == 9
    assert final_result["value"] == "version_9"

    # Only one file should exist (no partial writes)
    tensor_dir = runner.cell_traces_dir / "M"
    cell_files = list(tensor_dir.glob("0_0_0.*"))
    assert len(cell_files) == 1
    assert cell_files[0].name == "0_0_0.json"
