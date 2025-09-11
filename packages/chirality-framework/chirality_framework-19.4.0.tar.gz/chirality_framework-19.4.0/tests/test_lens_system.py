"""
Comprehensive tests for the Phase 1 lens system.

Tests catalog generation, management, overrides, and precedence resolution
as specified in colleague_1's Phase C plan.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from chirality.application.lenses import (
    LensCatalogGenerator, 
    LensCatalogManager,
    LensOverridesManager,
    LensResolver
)
from chirality.domain.matrices.canonical import get_canonical_matrix


class TestLensCatalogGeneration:
    """Test catalog generation with invalidation."""
    
    def test_catalog_generator_initialization(self):
        """Test generator can be initialized."""
        generator = LensCatalogGenerator(model="gpt-4o-mini")
        assert generator.model == "gpt-4o-mini"
        assert "Problem Statement" in generator.station_matrices
        assert generator.station_matrices["Problem Statement"]["matrix_id"] == "C"
    
    @patch('chirality.application.lenses.catalog_generator.Path.exists')
    @patch('chirality.application.lenses.catalog_generator.Path.read_text')
    def test_normative_context_loading(self, mock_read_text, mock_exists):
        """Test loading of normative system prompt."""
        mock_exists.return_value = True
        mock_read_text.return_value = "Mock normative content"
        
        generator = LensCatalogGenerator()
        context = generator._load_normative_context()
        
        assert context == "Mock normative content"
        mock_exists.assert_called_once()
        mock_read_text.assert_called_once()
    
    def test_context_hash_computation(self):
        """Test context hash computation for invalidation."""
        generator = LensCatalogGenerator()
        
        hash1 = generator._compute_context_hash("test content")
        hash2 = generator._compute_context_hash("test content")
        hash3 = generator._compute_context_hash("different content")
        
        assert hash1 == hash2  # Same content = same hash
        assert hash1 != hash3  # Different content = different hash
        assert len(hash1) == 16  # Should be truncated to 16 chars
    
    @patch('chirality.application.lenses.catalog_generator.Path.exists')
    @patch('chirality.application.lenses.catalog_generator.Path.read_text')
    def test_station_context_building(self, mock_read_text, mock_exists):
        """Test building context for specific stations."""
        mock_exists.return_value = True
        mock_read_text.return_value = "Mock normative"
        
        generator = LensCatalogGenerator()
        context = generator._build_station_context("Problem Statement")
        
        assert "Mock normative" in context
        assert "Problem Statement" in context
        assert "Matrix C" in context
        assert "semantic valley" in context.lower()


class TestLensCatalogManager:
    """Test catalog management with invalidation logic."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.catalog_path = Path(self.temp_dir) / "test_catalog.json"
        self.manager = LensCatalogManager(self.catalog_path)
    
    def test_manager_initialization(self):
        """Test manager initializes with correct path."""
        assert self.manager.catalog_path == self.catalog_path
        assert self.manager._cached_catalog is None
    
    def test_catalog_validation_missing_file(self):
        """Test validation fails when catalog file missing."""
        assert not self.manager._is_catalog_valid()
    
    def test_catalog_validation_invalid_json(self):
        """Test validation fails with invalid JSON."""
        self.catalog_path.write_text("invalid json")
        assert not self.manager._is_catalog_valid()
    
    def test_catalog_validation_missing_meta(self):
        """Test validation fails when meta section missing."""
        catalog = {"catalog": {}}
        self.catalog_path.write_text(json.dumps(catalog))
        assert not self.manager._is_catalog_valid()
    
    @patch('chirality.application.lenses.catalog_manager.Path.exists')
    @patch('chirality.application.lenses.catalog_manager.Path.read_text')
    def test_catalog_validation_hash_mismatch(self, mock_read_text, mock_exists):
        """Test validation fails when hashes don't match (invalidation trigger)."""
        mock_exists.return_value = True
        mock_read_text.return_value = "normative content"
        
        # Create catalog with different hashes
        catalog = {
            "meta": {
                "system_sha": "old_hash",
                "normative_sha": "old_hash", 
                "asset_sha": "old_hash"
            },
            "catalog": {}
        }
        self.catalog_path.write_text(json.dumps(catalog))
        
        assert not self.manager._is_catalog_valid()
    
    def test_load_nonexistent_catalog_raises_error(self):
        """Test loading nonexistent catalog raises appropriate error."""
        with pytest.raises(FileNotFoundError, match="Lens catalog not found"):
            self.manager.load_catalog()
    
    def test_get_nonexistent_station_raises_error(self):
        """Test getting nonexistent station raises appropriate error."""
        # Create minimal valid catalog
        catalog = {
            "meta": {},
            "catalog": {"Validation": {"station": "Validation"}}
        }
        self.catalog_path.write_text(json.dumps(catalog))
        
        with pytest.raises(ValueError, match="Station 'NonExistent' not found"):
            self.manager.get_station_lenses("NonExistent")


class TestLensOverridesManager:
    """Test override system with precedence."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.overrides_path = Path(self.temp_dir) / "test_overrides.json"
        self.manager = LensOverridesManager(self.overrides_path)
    
    def test_manager_initialization(self):
        """Test manager initializes correctly."""
        assert self.manager.overrides_path == self.overrides_path
        assert self.manager._cached_overrides is None
    
    def test_load_empty_overrides(self):
        """Test loading when no overrides file exists."""
        overrides = self.manager.load_overrides()
        assert overrides == {"overrides": {}}
    
    def test_load_invalid_json_returns_empty(self):
        """Test loading invalid JSON returns empty structure."""
        self.overrides_path.write_text("invalid json")
        overrides = self.manager.load_overrides()
        assert overrides == {"overrides": {}}
    
    @patch('chirality.application.lenses.overrides_manager.Path.exists')
    @patch('chirality.application.lenses.overrides_manager.Path.read_text')
    def test_add_override_with_provenance(self, mock_read_text, mock_exists):
        """Test adding override includes full provenance."""
        mock_exists.return_value = True
        mock_read_text.return_value = "normative content"
        
        lenses_data = {
            "matrix_id": "C",
            "rows": ["r1", "r2"],
            "cols": ["c1", "c2"],
            "lenses": [["lens1", "lens2"], ["lens3", "lens4"]]
        }
        
        self.manager.add_override("Problem Statement", lenses_data, source="auto")
        
        overrides = self.manager.load_overrides()
        override = overrides["overrides"]["Problem Statement"]
        
        assert override["station"] == "Problem Statement"
        assert override["matrix_id"] == "C"
        assert override["lenses"] == [["lens1", "lens2"], ["lens3", "lens4"]]
        assert override["meta"]["source"] == "auto"
        assert override["meta"]["generated_at"]  # Should have timestamp
        assert "system_sha" in override["meta"]
        assert "normative_sha" in override["meta"]
    
    def test_get_nonexistent_override_returns_none(self):
        """Test getting nonexistent override returns None."""
        assert self.manager.get_override("NonExistent") is None
        assert not self.manager.has_override("NonExistent")
    
    def test_remove_nonexistent_override_returns_false(self):
        """Test removing nonexistent override returns False."""
        assert not self.manager.remove_override("NonExistent")
    
    def test_clear_all_overrides(self):
        """Test clearing all overrides."""
        # Add some overrides first
        overrides = {"overrides": {"Station1": {}, "Station2": {}}}
        self.overrides_path.write_text(json.dumps(overrides))
        
        count = self.manager.clear_all_overrides()
        assert count == 2
        
        # Verify they're cleared
        new_overrides = self.manager.load_overrides()
        assert new_overrides["overrides"] == {}


class TestLensResolver:
    """Test unified lens resolution with precedence."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.catalog_path = Path(self.temp_dir) / "catalog.json"
        self.overrides_path = Path(self.temp_dir) / "overrides.json"
        
        # Create resolver in catalog mode
        self.resolver_catalog = LensResolver(
            lens_mode="catalog",
            catalog_path=self.catalog_path,
            overrides_path=self.overrides_path
        )
        
        # Create resolver in auto mode
        self.resolver_auto = LensResolver(
            lens_mode="auto",
            catalog_path=self.catalog_path,
            overrides_path=self.overrides_path
        )
    
    def test_resolver_initialization(self):
        """Test resolver initializes with correct settings."""
        assert self.resolver_catalog.lens_mode == "catalog"
        assert self.resolver_auto.lens_mode == "auto"
        assert "Problem Statement" in self.resolver_catalog.station_matrices
    
    def test_precedence_override_wins(self):
        """Test override takes precedence over catalog."""
        # Create catalog
        catalog_data = {
            "meta": {},
            "catalog": {
                "Validation": {
                    "station": "Validation",
                    "matrix_id": "Z",
                    "lenses": [["catalog_lens"]],
                    "meta": {}
                }
            }
        }
        self.catalog_path.write_text(json.dumps(catalog_data))
        
        # Create override
        override_data = {
            "overrides": {
                "Validation": {
                    "station": "Validation",
                    "matrix_id": "Z", 
                    "lenses": [["override_lens"]],
                    "meta": {"source": "manual"}
                }
            }
        }
        self.overrides_path.write_text(json.dumps(override_data))
        
        result = self.resolver_catalog.resolve_lenses("Validation")
        assert result["source"] == "override"
        assert result["lenses"] == [["override_lens"]]
    
    def test_catalog_mode_no_catalog_raises_error(self):
        """Test catalog mode raises error when no catalog available."""
        with pytest.raises(ValueError, match="No lenses available.*catalog mode"):
            self.resolver_catalog.resolve_lenses("Problem Statement")
    
    def test_auto_mode_generates_lenses(self):
        """Test auto mode generates lenses when catalog unavailable."""
        # This should not raise an error in auto mode
        result = self.resolver_auto.resolve_lenses("Problem Statement")
        assert result["source"] == "auto"
        assert result["station"] == "Problem Statement"
        assert result["matrix_id"] == "C"
        assert len(result["lenses"]) == 3  # Matrix C is 3x4
        assert len(result["lenses"][0]) == 4
    
    def test_get_lens_source_precedence(self):
        """Test lens source reporting shows correct precedence."""
        # No sources available
        source = self.resolver_catalog.get_lens_source("Problem Statement")
        assert "error" in source
        
        # Auto mode would generate
        source = self.resolver_auto.get_lens_source("Problem Statement")
        assert "auto" in source and "generate" in source
    
    def test_validate_lens_system(self):
        """Test lens system validation."""
        results = self.resolver_catalog.validate_lens_system()
        
        assert "catalog" in results
        assert "overrides" in results
        assert "stations" in results
        assert "station_details" in results
        
        # Should have entries for all stations
        expected_stations = ["Problem Statement", "Requirements", "Objectives", 
                           "Verification", "Validation", "Evaluation"]
        for station in expected_stations:
            assert station in results["station_details"]


class TestLensSystemIntegration:
    """Test end-to-end lens system integration."""
    
    def setup_method(self):
        """Setup integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.artifacts_dir = Path(self.temp_dir) / "artifacts"
        self.artifacts_dir.mkdir()
        
        self.catalog_path = self.artifacts_dir / "lens_catalog.json"
        self.overrides_path = self.artifacts_dir / "lens_overrides.json"
    
    def test_full_workflow_catalog_to_override(self):
        """Test complete workflow from catalog generation to override."""
        
        # Step 1: Generate catalog
        manager = LensCatalogManager(self.catalog_path)
        
        # Mock the generation to avoid actual LLM calls
        with patch.object(manager, 'ensure_catalog') as mock_ensure:
            mock_catalog = {
                "meta": {"system_sha": "abc123", "generated_at": "2023-01-01"},
                "catalog": {
                    "Validation": {
                        "station": "Validation",
                        "matrix_id": "Z",
                        "rows": ["r1"],
                        "cols": ["c1", "c2"],
                        "lenses": [["catalog_lens1", "catalog_lens2"]],
                        "meta": {}
                    }
                }
            }
            mock_ensure.return_value = mock_catalog
            
            catalog = manager.ensure_catalog()
            assert "Validation" in catalog["catalog"]
        
        # Step 2: Add override
        overrides_mgr = LensOverridesManager(self.overrides_path)
        lenses_data = {
            "matrix_id": "Z",
            "rows": ["r1"],
            "cols": ["c1", "c2"], 
            "lenses": [["override_lens1", "override_lens2"]]
        }
        
        with patch.object(overrides_mgr, '_load_normative_context') as mock_norm:
            mock_norm.return_value = "mock normative"
            overrides_mgr.add_override("Validation", lenses_data, source="manual")
        
        # Step 3: Test precedence resolution
        resolver = LensResolver(
            lens_mode="catalog",
            catalog_path=self.catalog_path,
            overrides_path=self.overrides_path
        )
        
        # Mock the managers to use our test data
        resolver.catalog_manager.load_catalog = lambda: mock_catalog
        resolver.overrides_manager.load_overrides = lambda: {
            "overrides": {
                "Validation": {
                    "station": "Validation",
                    "matrix_id": "Z",
                    "lenses": [["override_lens1", "override_lens2"]],
                    "meta": {"source": "manual"}
                }
            }
        }
        
        # Should get override, not catalog
        result = resolver.resolve_lenses("Validation")
        assert result["source"] == "override"
        assert result["lenses"] == [["override_lens1", "override_lens2"]]
    
    def test_mode_behavior_differences(self):
        """Test behavior differences between catalog and auto modes."""
        
        resolver_catalog = LensResolver(lens_mode="catalog")
        resolver_auto = LensResolver(lens_mode="auto")
        
        # With working catalog available:
        
        # Both should indicate catalog is available
        source = resolver_catalog.get_lens_source("Problem Statement")
        assert "catalog" in source
        
        # Auto mode would use catalog if available, otherwise generate
        source = resolver_auto.get_lens_source("Problem Statement")  
        assert "catalog" in source or ("auto" in source and "generate" in source)


class TestLensSchemaValidation:
    """Test schema validation for catalogs and overrides."""
    
    def test_catalog_schema_validation_success(self):
        """Test successful catalog schema validation."""
        temp_path = Path(tempfile.mktemp(suffix=".json"))
        
        valid_catalog = {
            "meta": {
                "system_sha": "abc123",
                "normative_sha": "def456",
                "asset_sha": "ghi789",
                "model": "gpt-4o",
                "stations": ["Validation"],
                "generated_at": "2023-01-01T00:00:00"
            },
            "catalog": {
                "Validation": {
                    "station": "Validation",
                    "matrix_id": "Z",
                    "rows": ["r1", "r2"],
                    "cols": ["c1", "c2"],
                    "lenses": [["lens1", "lens2"], ["lens3", "lens4"]],
                    "meta": {"generated_at": "2023-01-01T00:00:00"}
                }
            }
        }
        
        temp_path.write_text(json.dumps(valid_catalog))
        
        manager = LensCatalogManager(temp_path)
        assert manager.validate_catalog_schema()
        
        temp_path.unlink()
    
    def test_catalog_schema_validation_missing_keys(self):
        """Test catalog schema validation fails with missing keys."""
        temp_path = Path(tempfile.mktemp(suffix=".json"))
        
        invalid_catalog = {
            "meta": {},  # Missing required meta keys
            "catalog": {}
        }
        
        temp_path.write_text(json.dumps(invalid_catalog))
        
        manager = LensCatalogManager(temp_path)
        assert not manager.validate_catalog_schema()
        
        temp_path.unlink()
    
    def test_overrides_schema_validation_success(self):
        """Test successful overrides schema validation."""
        temp_path = Path(tempfile.mktemp(suffix=".json"))
        
        valid_overrides = {
            "overrides": {
                "Validation": {
                    "station": "Validation",
                    "matrix_id": "Z",
                    "rows": ["r1"],
                    "cols": ["c1", "c2"],
                    "lenses": [["lens1", "lens2"]],
                    "meta": {
                        "source": "auto",
                        "system_sha": "abc123",
                        "normative_sha": "def456",
                        "asset_sha": "ghi789",
                        "model": "gpt-4o",
                        "params": {},
                        "generated_at": "2023-01-01T00:00:00"
                    }
                }
            }
        }
        
        temp_path.write_text(json.dumps(valid_overrides))
        
        manager = LensOverridesManager(temp_path)
        assert manager.validate_overrides_schema()
        
        temp_path.unlink()


class TestLensSystemErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_station_names(self):
        """Test handling of invalid station names."""
        resolver = LensResolver()
        
        with pytest.raises(ValueError, match="Unknown station"):
            resolver._generate_lenses_for_station("Invalid Station")
    
    def test_missing_generation_assets(self):
        """Test handling when generation assets are missing."""
        resolver = LensResolver(lens_mode="auto")
        
        # Mock registry to simulate missing asset
        with patch.object(resolver.registry, 'get_text') as mock_get:
            mock_get.side_effect = KeyError("Asset not found")
            
            with pytest.raises(ValueError, match="Generation asset not found"):
                resolver._generate_lenses_for_station("Problem Statement")
    
    def test_corrupted_files_recovery(self):
        """Test recovery from corrupted files."""
        temp_path = Path(tempfile.mktemp(suffix=".json"))
        temp_path.write_text("corrupted json {")
        
        # Should not crash, should return empty structure
        manager = LensOverridesManager(temp_path)
        overrides = manager.load_overrides()
        assert overrides == {"overrides": {}}
        
        temp_path.unlink()