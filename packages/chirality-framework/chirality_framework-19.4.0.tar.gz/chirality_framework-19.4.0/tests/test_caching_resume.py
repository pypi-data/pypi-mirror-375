"""
Test caching and resume functionality.

Validates that Phase 2 caching and resume work correctly with
tensor engines and file I/O.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from chirality.infrastructure.caching import CellCache, ResumableRunner
from chirality.application.phase2.tensor_engine import TensorEngine


def test_cell_cache_basic_functionality():
    """Test that cell cache stores and retrieves correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = CellCache(cache_dir, enabled=True)

        # Test cache key computation
        cache_key = cache.compute_cache_key(
            tensor_name="M",
            indices=(0, 1, 2),
            operands_hash="abc123",
            lens_id="lens_001",
            snapshot_hash="snap123",
            model="gpt-5-nano",
            temperature=0.7,
            top_p=0.9,
        )

        # Cache should be empty initially
        assert cache.get(cache_key) is None

        # Store a result
        test_result = {"value": "test_semantic_result", "metadata": {"tokens": 100}}
        cache.put(cache_key, test_result)

        # Should be able to retrieve it
        cached_result = cache.get(cache_key)
        assert cached_result == test_result

        # Should persist to disk
        cache_file = cache_dir / f"{cache_key}.json"
        assert cache_file.exists()


def test_cell_cache_disabled():
    """Test that disabled cache doesn't store anything."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        cache = CellCache(cache_dir, enabled=False)

        cache_key = "test_key"
        test_result = {"value": "test"}

        # Put should be ignored
        cache.put(cache_key, test_result)

        # Get should return None
        assert cache.get(cache_key) is None

        # No files should be created
        assert len(list(cache_dir.glob("*.json"))) == 0


def test_resumable_runner_basic_functionality():
    """Test that resumable runner tracks progress correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts_dir = Path(temp_dir)
        runner = ResumableRunner(artifacts_dir)

        # Should create empty manifest initially
        manifest = runner.load_manifest()
        assert manifest["cells_completed"] == 0
        assert manifest["phase2_complete"] is False

        # Save a cell result
        test_result = {"value": "test_tensor_cell", "metadata": {"model": "gpt-5-nano"}}
        runner.save_cell_result("M", (0, 1), test_result)

        # Should be able to load it back
        loaded_result = runner.load_cell_result("M", (0, 1))
        assert loaded_result["value"] == "test_tensor_cell"

        # Check completed cells
        completed = runner.get_completed_cells("M")
        assert "0_1" in completed

        # Update progress
        runner.update_progress("M", 1, 10)
        manifest = runner.load_manifest()
        assert manifest["cells_completed"] == 1
        assert manifest["cells_planned"] == 10


def test_resumable_runner_manifest_tracking():
    """Test that manifest tracks multiple tensors correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts_dir = Path(temp_dir)
        runner = ResumableRunner(artifacts_dir)

        # Track progress for tensor M
        runner.update_progress("M", 5, 10)

        # Track progress for tensor W
        runner.update_progress("W", 3, 8)

        manifest = runner.load_manifest()
        assert manifest["tensors"]["M"]["cells_completed"] == 5
        assert manifest["tensors"]["M"]["total_cells"] == 10
        assert manifest["tensors"]["W"]["cells_completed"] == 3
        assert manifest["tensors"]["W"]["total_cells"] == 8

        # Overall progress should be sum
        assert manifest["cells_completed"] == 8  # 5 + 3
        assert manifest["cells_planned"] == 18  # 10 + 8


@pytest.mark.skip("TensorEngine integration test - requires full setup")
def test_tensor_engine_cache_integration():
    """Test that TensorEngine properly uses cache and resume."""
    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts_dir = Path(temp_dir)

        # Create minimal test setup
        snapshot_path = artifacts_dir / "phase1_snapshot.md"
        snapshot_path.write_text("# Phase 1 snapshot\nTest snapshot content")

        phase1_output = {
            "matrices": {
                "E": {
                    "rows": ["normative", "operative"],
                    "cols": ["guiding", "applying"],
                    "station": "Evaluation",
                    "elements": [["e00", "e01"], ["e10", "e11"]],
                }
            }
        }

        # Mock tensor spec
        tensor_spec = {
            "name": "M",
            "op": "cross",
            "sources": {"R": {"R": "array"}, "E": {"E": "matrix"}},
            "matrix_operand": "E",
        }

        # Create engine with cache enabled
        engine = TensorEngine(
            snapshot_path=snapshot_path,
            phase1_output=phase1_output,
            artifacts_dir=artifacts_dir,
            cache_enabled=True,
            resume=False,
        )

        # Mock the LLM call to be deterministic
        with patch("chirality.application.phase2.tensor_engine.call_responses_api") as mock_call:
            mock_call.return_value = (
                {"value": "mocked_tensor_result"},
                {"total_tokens": 100, "prompt_tokens": 60, "completion_tokens": 40},
            )

            # First computation should call LLM
            result1 = engine.compute_tensor(tensor_spec)
            assert mock_call.call_count > 0

            # Reset mock
            mock_call.reset_mock()

            # Second computation with same inputs should use cache
            result2 = engine.compute_tensor(tensor_spec)
            assert mock_call.call_count == 0  # No LLM calls

            # Results should be identical
            assert result1["name"] == result2["name"]


@pytest.mark.skip("TensorEngine resume test - requires full setup")
def test_tensor_engine_resume_functionality():
    """Test that TensorEngine can resume from partial completion."""
    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts_dir = Path(temp_dir)

        # Create test setup
        snapshot_path = artifacts_dir / "phase1_snapshot.md"
        snapshot_path.write_text("# Phase 1 snapshot\nTest content")

        phase1_output = {
            "matrices": {
                "E": {
                    "rows": ["normative"],
                    "cols": ["guiding"],
                    "station": "Evaluation",
                    "elements": [["e00"]],
                }
            }
        }

        tensor_spec = {
            "name": "M",
            "op": "cross",
            "sources": {"R": {"R": "array"}, "E": {"E": "matrix"}},
            "matrix_operand": "E",
        }

        # Pre-populate some cell traces (simulate partial completion)
        runner = ResumableRunner(artifacts_dir)
        runner.save_cell_result(
            "M", (0, 0, 0), {"value": "precomputed_result", "metadata": {"model": "gpt-5-nano"}}
        )
        runner.update_progress("M", 1, 4)  # 1 of 4 cells done

        # Create engine with resume enabled
        engine = TensorEngine(
            snapshot_path=snapshot_path,
            phase1_output=phase1_output,
            artifacts_dir=artifacts_dir,
            cache_enabled=True,
            resume=True,
        )

        with patch("chirality.application.phase2.tensor_engine.call_responses_api") as mock_call:
            mock_call.return_value = ({"value": "newly_computed_result"}, {"total_tokens": 50})

            result = engine.compute_tensor(tensor_spec)

            # Should have mixed results: some from resume, some computed
            stats = result.get("stats", {})
            assert stats.get("cells_from_resume", 0) > 0
            assert stats.get("total_cells", 0) > stats.get("cells_from_resume", 0)


def test_cache_key_completeness():
    """Test that cache keys include all necessary parameters."""
    cache = CellCache(Path("/tmp"), enabled=True)

    # Generate cache key with all parameters
    key1 = cache.compute_cache_key(
        tensor_name="M",
        indices=(0, 1, 2),
        operands_hash="operands123",
        lens_id="lens_abc",
        snapshot_hash="snap456",
        model="gpt-5-nano",
        temperature=0.7,
        top_p=0.9,
    )

    # Same parameters should generate same key
    key2 = cache.compute_cache_key(
        tensor_name="M",
        indices=(0, 1, 2),
        operands_hash="operands123",
        lens_id="lens_abc",
        snapshot_hash="snap456",
        model="gpt-5-nano",
        temperature=0.7,
        top_p=0.9,
    )
    assert key1 == key2

    # Different temperature should generate different key
    key3 = cache.compute_cache_key(
        tensor_name="M",
        indices=(0, 1, 2),
        operands_hash="operands123",
        lens_id="lens_abc",
        snapshot_hash="snap456",
        model="gpt-5-nano",
        temperature=0.8,  # Different!
        top_p=0.9,
    )
    assert key1 != key3

    # Different model should generate different key
    key4 = cache.compute_cache_key(
        tensor_name="M",
        indices=(0, 1, 2),
        operands_hash="operands123",
        lens_id="lens_abc",
        snapshot_hash="snap456",
        model="gpt-4o-mini",  # Different!
        temperature=0.7,
        top_p=0.9,
    )
    assert key1 != key4


def test_operands_hash_deterministic():
    """Test that operands hash is deterministic."""
    cache = CellCache(Path("/tmp"), enabled=True)

    operands1 = {"left": "value1", "right": "value2"}
    operands2 = {"left": "value1", "right": "value2"}
    operands3 = {"right": "value2", "left": "value1"}  # Different order

    hash1 = cache.compute_operands_hash(operands1)
    hash2 = cache.compute_operands_hash(operands2)
    hash3 = cache.compute_operands_hash(operands3)

    # Same content should produce same hash
    assert hash1 == hash2

    # Different order should still produce same hash (keys sorted)
    assert hash1 == hash3

    # Different content should produce different hash
    operands4 = {"left": "different", "right": "values"}
    hash4 = cache.compute_operands_hash(operands4)
    assert hash1 != hash4
