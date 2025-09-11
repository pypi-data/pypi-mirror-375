"""
Test Phase 2 reproducibility.

Validates that running Phase 2 twice with the same snapshot_hash and lens catalog
produces byte-identical results.
"""

import pytest
import json
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.mark.skip("Phase 2 tensor engine not yet implemented")
def test_phase2_deterministic_output(temp_artifacts_dir):
    """Test that Phase 2 produces identical output when run twice with same inputs."""
    # Setup mock inputs
    snapshot_file = temp_artifacts_dir / "phase1_snapshot.md"
    lens_catalog = temp_artifacts_dir / "lens_catalog.jsonl"
    tensor_spec = temp_artifacts_dir / "tensor_spec.json"

    # Create mock snapshot
    snapshot_content = """# Phase 1 Snapshot
snapshot_hash: abc123def456

## Matrix E
[Evaluation content...]
"""
    with open(snapshot_file, "w") as f:
        f.write(snapshot_content)

    # Create mock lens catalog
    lens_entries = [
        {
            "lens_id": "lens_001",
            "row": "normative",
            "col": "guiding",
            "station": "Assessment",
            "text": "Mock lens text",
            "kernel_hash": "xyz789",
            "model": "gpt-4",
            "prompt_version": "v1",
        }
    ]

    with open(lens_catalog, "w") as f:
        for entry in lens_entries:
            f.write(json.dumps(entry) + "\n")

    # Create mock tensor spec
    spec = {"tensor": "M", "operation": "cross_product", "dimensions": [9, 3, 3]}

    with open(tensor_spec, "w") as f:
        json.dump(spec, f)

    # Run Phase 2 twice with deterministic mock
    output1_dir = temp_artifacts_dir / "run1"
    output2_dir = temp_artifacts_dir / "run2"

    try:
        # Import the actual Phase 2 runner
        from chirality.application.phase2.tensor_engine import run_phase2

        # Mock the LLM calls to be deterministic
        with patch(
            "chirality.application.phase2.tensor_engine.resolve_tensor_cell"
        ) as mock_resolve:
            # Return deterministic mock results
            mock_resolve.return_value = {
                "value": "deterministic_cell_result",
                "metadata": {"model": "gpt-4", "temperature": 0.2},
            }

            # Run Phase 2 twice
            run_phase2(str(tensor_spec), str(snapshot_file), output_dir=str(output1_dir))
            run_phase2(str(tensor_spec), str(snapshot_file), output_dir=str(output2_dir))

            # Compare outputs
            output1_file = output1_dir / "phase2_output.json"
            output2_file = output2_dir / "phase2_output.json"

            assert output1_file.exists()
            assert output2_file.exists()

            # Read both outputs
            with open(output1_file) as f:
                output1 = json.load(f)
            with open(output2_file) as f:
                output2 = json.load(f)

            # Should be identical
            assert output1 == output2

            # Verify SHA-256 hashes are identical
            hash1 = hashlib.sha256(output1_file.read_bytes()).hexdigest()
            hash2 = hashlib.sha256(output2_file.read_bytes()).hexdigest()

            assert hash1 == hash2

    except ImportError:
        pytest.skip("Phase 2 tensor engine not yet implemented")


@pytest.mark.skip("Phase 2 tensor engine not yet implemented")
def test_phase2_snapshot_hash_dependency(temp_artifacts_dir):
    """Test that different snapshot_hash produces different Phase 2 output."""
    # This test ensures that Phase 2 is actually using the snapshot content

    snapshot1_file = temp_artifacts_dir / "snapshot1.md"
    snapshot2_file = temp_artifacts_dir / "snapshot2.md"
    tensor_spec = temp_artifacts_dir / "tensor_spec.json"

    # Create two different snapshots
    with open(snapshot1_file, "w") as f:
        f.write("# Snapshot 1\nsnapshot_hash: abc123\n## Matrix E\nContent A")

    with open(snapshot2_file, "w") as f:
        f.write("# Snapshot 2\nsnapshot_hash: def456\n## Matrix E\nContent B")

    # Mock tensor spec
    with open(tensor_spec, "w") as f:
        json.dump({"tensor": "M", "operation": "cross_product"}, f)

    try:
        from chirality.application.phase2.tensor_engine import run_phase2

        output1_dir = temp_artifacts_dir / "run1"
        output2_dir = temp_artifacts_dir / "run2"

        with patch(
            "chirality.application.phase2.tensor_engine.resolve_tensor_cell"
        ) as mock_resolve:
            # Mock should return different results based on input content
            def mock_resolver(*args, **kwargs):
                # Simple way to make output depend on input
                input_hash = hashlib.md5(str(args).encode()).hexdigest()[:8]
                return {"value": f"result_for_{input_hash}", "metadata": {"model": "gpt-4"}}

            mock_resolve.side_effect = mock_resolver

            run_phase2(str(tensor_spec), str(snapshot1_file), output_dir=str(output1_dir))
            run_phase2(str(tensor_spec), str(snapshot2_file), output_dir=str(output2_dir))

            # Outputs should be different
            output1_file = output1_dir / "phase2_output.json"
            output2_file = output2_dir / "phase2_output.json"

            with open(output1_file) as f:
                output1 = json.load(f)
            with open(output2_file) as f:
                output2 = json.load(f)

            assert output1 != output2  # Different snapshots should yield different results

    except ImportError:
        pytest.skip("Phase 2 tensor engine not yet implemented")


@pytest.mark.skip("Phase 2 tensor engine not yet implemented")
def test_phase2_resume_capability(temp_artifacts_dir):
    """Test that Phase 2 --resume works correctly."""
    snapshot_file = temp_artifacts_dir / "snapshot.md"
    tensor_spec = temp_artifacts_dir / "tensor_spec.json"
    output_dir = temp_artifacts_dir / "phase2_run"
    cache_dir = output_dir / "cache"

    # Setup inputs
    with open(snapshot_file, "w") as f:
        f.write("# Test snapshot\nsnapshot_hash: test123")

    with open(tensor_spec, "w") as f:
        json.dump({"tensor": "M", "cells": 4}, f)  # Mock small tensor

    try:
        from chirality.application.phase2.tensor_engine import run_phase2

        with patch(
            "chirality.application.phase2.tensor_engine.resolve_tensor_cell"
        ) as mock_resolve:
            # First run - mock completing 2 of 4 cells
            call_count = 0

            def mock_partial_run(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    return {"value": f"cell_{call_count}", "metadata": {}}
                else:
                    raise Exception("Simulated failure after 2 cells")

            mock_resolve.side_effect = mock_partial_run

            # First run should fail partway
            with pytest.raises(Exception, match="Simulated failure"):
                run_phase2(str(tensor_spec), str(snapshot_file), output_dir=str(output_dir))

            # Verify partial cache exists
            assert cache_dir.exists()
            cached_files = list(cache_dir.glob("*.json"))
            assert len(cached_files) == 2  # Only 2 cells completed

            # Second run with resume - should complete remaining cells
            def mock_resume_run(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                return {"value": f"cell_{call_count}", "metadata": {}}

            mock_resolve.side_effect = mock_resume_run
            call_count = 2  # Reset to continue from where we left off

            run_phase2(
                str(tensor_spec), str(snapshot_file), output_dir=str(output_dir), resume=True
            )

            # Should now have completed all cells
            final_output = output_dir / "phase2_output.json"
            assert final_output.exists()

    except ImportError:
        pytest.skip("Phase 2 tensor engine not yet implemented")
