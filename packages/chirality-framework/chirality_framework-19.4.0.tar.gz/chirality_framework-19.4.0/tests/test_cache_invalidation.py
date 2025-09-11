"""
Test cache invalidation scenarios.

Validates that cache keys properly invalidate when dependencies change,
ensuring deterministic behavior and preventing stale cached results.
"""

import json
import tempfile
from pathlib import Path

import pytest

from chirality.infrastructure.caching import CellCache


@pytest.fixture
def temp_cache():
    """Create temporary cache directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = CellCache(Path(temp_dir), enabled=True)
        yield cache


def test_cache_invalidation_on_operands_change(temp_cache):
    """Test that cache invalidates when operands change."""
    # Cache a result with specific operands
    cache_key1 = temp_cache.compute_cache_key(
        tensor_name="M",
        indices=(0, 1, 2),
        operands_hash="hash_operands_v1",
        lens_id="lens1",
        snapshot_hash="snap1",
        model="gpt-5-nano",
    )

    result1 = {"value": "result_from_operands_v1"}
    temp_cache.put(cache_key1, result1)

    # Same parameters but different operands hash
    cache_key2 = temp_cache.compute_cache_key(
        tensor_name="M",
        indices=(0, 1, 2),
        operands_hash="hash_operands_v2",  # Changed
        lens_id="lens1",
        snapshot_hash="snap1",
        model="gpt-5-nano",
    )

    # Keys should be different (cache miss expected)
    assert cache_key1 != cache_key2

    # First result should be cached
    cached1 = temp_cache.get(cache_key1)
    assert cached1 == result1

    # Second should be a cache miss
    cached2 = temp_cache.get(cache_key2)
    assert cached2 is None


def test_cache_invalidation_on_snapshot_change(temp_cache):
    """Test that cache invalidates when Phase 1 snapshot changes."""
    base_params = {
        "tensor_name": "W",
        "indices": (0, 0, 1, 2, 3),
        "operands_hash": "stable_operands",
        "lens_id": "lens_xyz",
        "model": "gpt-5-nano",
    }

    # Cache with snapshot v1
    cache_key1 = temp_cache.compute_cache_key(**base_params, snapshot_hash="phase1_snapshot_v1")

    result1 = {"value": "result_with_snapshot_v1"}
    temp_cache.put(cache_key1, result1)

    # Same parameters but different snapshot
    cache_key2 = temp_cache.compute_cache_key(
        **base_params, snapshot_hash="phase1_snapshot_v2"  # Changed
    )

    # Should be different cache keys
    assert cache_key1 != cache_key2

    # First should be cached, second should miss
    assert temp_cache.get(cache_key1) == result1
    assert temp_cache.get(cache_key2) is None


def test_cache_invalidation_on_kernel_change(temp_cache):
    """Test that cache invalidates when kernel hash changes."""
    base_params = {
        "tensor_name": "U",
        "indices": (1, 2, 0, 3, 1, 2),
        "operands_hash": "stable_operands",
        "lens_id": "lens_abc",
        "snapshot_hash": "stable_snapshot",
        "model": "gpt-5-nano",
    }

    # Cache with kernel v1
    cache_key1 = temp_cache.compute_cache_key(**base_params, kernel_hash="kernel_v1")

    result1 = {"value": "result_with_kernel_v1"}
    temp_cache.put(cache_key1, result1)

    # Same parameters but different kernel
    cache_key2 = temp_cache.compute_cache_key(**base_params, kernel_hash="kernel_v2")  # Changed

    # Should invalidate
    assert cache_key1 != cache_key2
    assert temp_cache.get(cache_key1) == result1
    assert temp_cache.get(cache_key2) is None


def test_cache_invalidation_on_lens_catalog_change(temp_cache):
    """Test that cache invalidates when lens catalog changes."""
    base_params = {
        "tensor_name": "N",
        "indices": (0, 1, 2, 3, 4, 5, 6),
        "operands_hash": "stable_operands",
        "lens_id": "lens_123",
        "snapshot_hash": "stable_snapshot",
        "kernel_hash": "stable_kernel",
        "model": "gpt-5-nano",
    }

    # Cache with lens catalog v1
    cache_key1 = temp_cache.compute_cache_key(**base_params, lens_catalog_digest="lens_catalog_v1")

    result1 = {"value": "result_with_lens_catalog_v1"}
    temp_cache.put(cache_key1, result1)

    # Same parameters but different lens catalog
    cache_key2 = temp_cache.compute_cache_key(
        **base_params, lens_catalog_digest="lens_catalog_v2"  # Changed
    )

    # Should invalidate
    assert cache_key1 != cache_key2
    assert temp_cache.get(cache_key1) == result1
    assert temp_cache.get(cache_key2) is None


def test_cache_invalidation_on_model_params(temp_cache):
    """Test that cache invalidates when model parameters change."""
    base_params = {
        "tensor_name": "M",
        "indices": (0, 1),
        "operands_hash": "stable_operands",
        "lens_id": "stable_lens",
        "snapshot_hash": "stable_snapshot",
        "kernel_hash": "stable_kernel",
        "lens_catalog_digest": "stable_catalog",
    }

    # Cache with specific model params
    cache_key1 = temp_cache.compute_cache_key(
        **base_params, model="gpt-5-nano", temperature=0.2, top_p=0.9
    )

    result1 = {"value": "result_with_temp_0.2"}
    temp_cache.put(cache_key1, result1)

    # Different temperature
    cache_key2 = temp_cache.compute_cache_key(
        **base_params, model="gpt-5-nano", temperature=0.7, top_p=0.9  # Changed
    )

    # Different top_p
    cache_key3 = temp_cache.compute_cache_key(
        **base_params, model="gpt-5-nano", temperature=0.2, top_p=0.8  # Changed
    )

    # Different model
    cache_key4 = temp_cache.compute_cache_key(
        **base_params, model="gpt-5", temperature=0.2, top_p=0.9  # Changed
    )

    # All should be different
    cache_keys = [cache_key1, cache_key2, cache_key3, cache_key4]
    assert len(set(cache_keys)) == 4

    # Only first should be cached
    assert temp_cache.get(cache_key1) == result1
    assert temp_cache.get(cache_key2) is None
    assert temp_cache.get(cache_key3) is None
    assert temp_cache.get(cache_key4) is None


def test_cache_invalidation_on_gpt5_params(temp_cache):
    """Test that cache invalidates when GPT-5 specific parameters change."""
    base_params = {
        "tensor_name": "W",
        "indices": (0, 1, 2, 3, 4),
        "operands_hash": "stable_operands",
        "lens_id": "stable_lens",
        "snapshot_hash": "stable_snapshot",
        "model": "gpt-5",
    }

    # Cache with specific GPT-5 params
    cache_key1 = temp_cache.compute_cache_key(
        **base_params, verbosity="medium", reasoning_effort="medium", max_tokens=1000
    )

    result1 = {"value": "result_with_medium_params"}
    temp_cache.put(cache_key1, result1)

    # Different verbosity
    cache_key2 = temp_cache.compute_cache_key(
        **base_params, verbosity="high", reasoning_effort="medium", max_tokens=1000  # Changed
    )

    # Different reasoning effort
    cache_key3 = temp_cache.compute_cache_key(
        **base_params, verbosity="medium", reasoning_effort="minimal", max_tokens=1000  # Changed
    )

    # Different max_tokens
    cache_key4 = temp_cache.compute_cache_key(
        **base_params, verbosity="medium", reasoning_effort="medium", max_tokens=2000  # Changed
    )

    # All should be different
    cache_keys = [cache_key1, cache_key2, cache_key3, cache_key4]
    assert len(set(cache_keys)) == 4

    # Only first should be cached
    assert temp_cache.get(cache_key1) == result1
    for key in cache_keys[1:]:
        assert temp_cache.get(key) is None


def test_cache_stable_on_optional_params(temp_cache):
    """Test that cache is stable when optional params are None vs not provided."""
    base_params = {
        "tensor_name": "M",
        "indices": (0, 1),
        "operands_hash": "stable_operands",
        "lens_id": "stable_lens",
        "snapshot_hash": "stable_snapshot",
        "model": "gpt-5-nano",
    }

    # Cache key with no optional GPT-5 params
    cache_key1 = temp_cache.compute_cache_key(**base_params)

    # Cache key with explicit None values
    cache_key2 = temp_cache.compute_cache_key(
        **base_params, verbosity=None, reasoning_effort=None, max_tokens=None
    )

    # Should be identical (None values shouldn't affect cache key)
    assert cache_key1 == cache_key2

    # Cache a result with first key
    result = {"value": "stable_result"}
    temp_cache.put(cache_key1, result)

    # Should be retrievable with second key
    assert temp_cache.get(cache_key2) == result


def test_operands_hash_deterministic(temp_cache):
    """Test that operands hash is deterministic for same data."""
    operands1 = {"left": "concept_a", "right": "concept_b"}
    operands2 = {"right": "concept_b", "left": "concept_a"}  # Different order

    # Should produce same hash (keys sorted)
    hash1 = temp_cache.compute_operands_hash(operands1)
    hash2 = temp_cache.compute_operands_hash(operands2)
    assert hash1 == hash2

    # Different data should produce different hash
    operands3 = {"left": "concept_a", "right": "concept_c"}
    hash3 = temp_cache.compute_operands_hash(operands3)
    assert hash1 != hash3


def test_cache_key_collision_resistance(temp_cache):
    """Test that similar but different parameters produce different cache keys."""
    # Create many similar cache keys with small variations
    base_params = {
        "tensor_name": "M",
        "operands_hash": "base_operands",
        "lens_id": "base_lens",
        "snapshot_hash": "base_snapshot",
        "model": "gpt-5-nano",
    }

    cache_keys = []

    # Vary indices
    for i in range(10):
        for j in range(10):
            key = temp_cache.compute_cache_key(**base_params, indices=(i, j))
            cache_keys.append(key)

    # Vary tensor names
    for tensor in ["W", "U", "N"]:  # M is already in base_params
        modified_params = base_params.copy()
        modified_params["tensor_name"] = tensor
        key = temp_cache.compute_cache_key(**modified_params, indices=(0, 0))
        cache_keys.append(key)

    # All keys should be unique
    assert len(cache_keys) == len(set(cache_keys)), "Cache key collision detected!"


def test_cache_persistence_across_restarts(temp_cache):
    """Test that cache persists across CellCache instance restarts."""
    cache_dir = temp_cache.cache_dir

    # Cache a result
    cache_key = temp_cache.compute_cache_key(
        tensor_name="M",
        indices=(5, 7),
        operands_hash="persistent_operands",
        lens_id="persistent_lens",
        snapshot_hash="persistent_snapshot",
        model="gpt-5-nano",
    )

    result = {"value": "persistent_result", "metadata": {"test": True}}
    temp_cache.put(cache_key, result)

    # Verify cached
    assert temp_cache.get(cache_key) == result

    # Create new cache instance with same directory
    new_cache = CellCache(cache_dir, enabled=True)

    # Should load from disk
    cached_result = new_cache.get(cache_key)
    assert cached_result == result
