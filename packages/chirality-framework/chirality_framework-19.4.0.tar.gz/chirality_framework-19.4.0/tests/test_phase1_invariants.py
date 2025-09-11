"""
Test Phase 1 architectural invariants and contracts.

Enforces the critical requirements documented in MANIFEST.md:
- JSON tails present for all required stages
- Matrix Z invariants (no interpreted stage, uses X lensed)
- Matrix D 4-stage requirement
- No forbidden placeholders in static stages
"""

import pytest
from pathlib import Path

from chirality.infrastructure.prompts.registry import get_registry
from chirality.infrastructure.prompts.json_tails import get_tail


class TestJSONTailsInvariants:
    """Ensure all required stages have proper JSON tail contracts."""
    
    def test_all_mechanical_stages_have_json_tails(self):
        """All mechanical stages must have JSON tail contracts."""
        required_mechanical = [
            ("C", "mechanical"),
            ("F", "mechanical"), 
            ("D", "mechanical"),  # D is 4-stage
            ("X", "mechanical"),
            ("E", "mechanical"),
        ]
        
        for matrix, step in required_mechanical:
            # Should not raise ValueError
            tail = get_tail(matrix, step)
            assert "Return JSON only" in tail
            assert f'"name":"{matrix}"' in tail
            assert f'"step":"{step}"' in tail
    
    def test_all_interpreted_stages_have_json_tails(self):
        """All interpreted stages must have JSON tail contracts.""" 
        required_interpreted = [
            ("C", "interpreted"),
            ("F", "interpreted"),
            ("D", "interpreted"),  # D is 4-stage
            ("X", "interpreted"), 
            ("E", "interpreted"),
        ]
        
        for matrix, step in required_interpreted:
            # Should not raise ValueError
            tail = get_tail(matrix, step)
            assert "Return JSON only" in tail
            assert f'"name":"{matrix}"' in tail
            assert f'"step":"{step}"' in tail
    
    def test_all_lensed_stages_have_json_tails(self):
        """All lensed stages must have JSON tail contracts."""
        required_lensed = [
            ("C", "lensed"),
            ("F", "lensed"),
            ("D", "lensed"),  # D is 4-stage
            ("X", "lensed"),
            ("E", "lensed"),
            ("Z", "lensed"),  # Z has lensed stage
        ]
        
        for matrix, step in required_lensed:
            # Should not raise ValueError
            tail = get_tail(matrix, step)
            assert "Return JSON only" in tail
            assert f'"name":"{matrix}"' in tail
            assert f'"step":"{step}"' in tail
    
    def test_z_principles_has_json_tail(self):
        """Z principles extraction must have JSON tail contract."""
        tail = get_tail("Z", "principles")
        assert "Return JSON only" in tail
        assert '"artifact":"principles"' in tail
        assert '"source":"Z"' in tail


class TestMatrixZInvariants:
    """Enforce Matrix Z architectural constraints."""
    
    def test_z_has_no_interpreted_stage_asset(self):
        """Matrix Z must NOT have an interpreted.md file (stage skipped)."""
        registry = get_registry()
        
        # Z should not have interpreted asset registered
        with pytest.raises(KeyError, match="Asset 'phase1_z_interpreted' not found"):
            registry.get_text("phase1_z_interpreted")
    
    def test_z_has_required_assets_only(self):
        """Matrix Z must have exactly lensed.md and principles.md."""
        registry = get_registry()
        
        # Z must have lensed stage
        z_lensed = registry.get_text("phase1_z_lensed")
        assert "Matrix X **lensed** layer" in z_lensed
        assert "conversation history" in z_lensed
        
        # Z must have principles stage  
        z_principles = registry.get_text("phase1_z_principles")
        assert "Matrix Z" in z_principles
        assert "validation principles" in z_principles.lower()
    
    def test_z_lensed_references_x_lensed_from_history(self):
        """Z/lensed.md must explicitly reference X lensed from conversation history."""
        registry = get_registry()
        z_lensed = registry.get_text("phase1_z_lensed")
        
        # Must reference X lensed (not interpreted)
        assert "Matrix X **lensed**" in z_lensed
        assert "conversation history" in z_lensed
        
        # Must NOT reference X interpreted
        assert "Matrix X **interpreted**" not in z_lensed
        assert "X interpreted" not in z_lensed
    
    def test_z_has_no_interpreted_json_tail(self):
        """Matrix Z must not have interpreted stage JSON tail."""
        with pytest.raises(ValueError, match="No tail defined"):
            get_tail("Z", "interpreted")


class TestMatrixDInvariants:
    """Enforce Matrix D 4-stage requirement."""
    
    def test_d_has_all_four_stage_assets(self):
        """Matrix D must have mechanical, interpreted, and lensed stages."""
        registry = get_registry()
        
        # D must have all 3 conversational stages (4th stage is lenses generation)
        d_mechanical = registry.get_text("phase1_d_mechanical")
        assert "mechanical" in d_mechanical.lower() or "construction" in d_mechanical.lower()
        
        d_interpreted = registry.get_text("phase1_d_interpreted") 
        assert "addition" in d_interpreted.lower() or "resolve" in d_interpreted.lower()
        
        d_lensed = registry.get_text("phase1_d_lensed")
        assert "lens" in d_lensed.lower()
    
    def test_d_interpreted_mentions_addition_only(self):
        """D interpreted stage must resolve addition only, not multiplication."""
        registry = get_registry()
        d_interpreted = registry.get_text("phase1_d_interpreted")
        
        # Should mention addition/concatenation
        content_lower = d_interpreted.lower()
        assert "addition" in content_lower or "+" in d_interpreted or "concatenat" in content_lower
        
        # Should explicitly say NOT to apply multiplication 
        assert "do not apply multiplication" in content_lower or "not apply multiplication" in content_lower
        # Should not instruct to resolve or perform multiplication (only addition)
        assert "resolve multiplication" not in content_lower
        # OK: "Do NOT apply multiplication" (negative instruction)
        # BAD: "Apply multiplication" (positive instruction) without negation


class TestForbiddenPlaceholders:
    """Ensure no forbidden placeholders in static stages."""
    
    def test_interpreted_stages_have_no_content_placeholders(self):
        """Interpreted stages must not have {{content}} or {{previous_output}} placeholders."""
        registry = get_registry()
        
        interpreted_assets = [
            "phase1_c_interpreted",
            "phase1_f_interpreted", 
            "phase1_d_interpreted",
            "phase1_x_interpreted",
            "phase1_e_interpreted",
        ]
        
        for asset_id in interpreted_assets:
            content = registry.get_text(asset_id)
            assert "{{content}}" not in content, f"{asset_id} contains forbidden {{{{content}}}} placeholder"
            assert "{{previous_output}}" not in content, f"{asset_id} contains forbidden {{{{previous_output}}}} placeholder"
    
    def test_lensed_stages_have_no_content_placeholders(self):
        """Lensed stages must not have {{content}} placeholders (rely on history)."""
        registry = get_registry()
        
        lensed_assets = [
            "phase1_c_lensed",
            "phase1_f_lensed",
            "phase1_d_lensed", 
            "phase1_x_lensed",
            "phase1_e_lensed",
            "phase1_z_lensed",
        ]
        
        for asset_id in lensed_assets:
            content = registry.get_text(asset_id)
            assert "{{content}}" not in content, f"{asset_id} contains forbidden {{{{content}}}} placeholder"
            assert "{{previous_output}}" not in content, f"{asset_id} contains forbidden {{{{previous_output}}}} placeholder"
    
    def test_z_principles_has_no_content_placeholders(self):
        """Z principles stage must not have content placeholders."""
        registry = get_registry()
        content = registry.get_text("phase1_z_principles")
        
        assert "{{content}}" not in content
        assert "{{previous_output}}" not in content
        assert "{{z_lensed}}" not in content


class TestAssetStructureCompleteness:
    """Verify complete asset structure exists."""
    
    def test_all_required_phase1_assets_exist(self):
        """All required Phase 1 assets must be registered and loadable."""
        registry = get_registry()
        
        required_assets = [
            # Matrix C
            "phase1_c_mechanical", "phase1_c_interpreted", "phase1_c_lensed",
            # Matrix F  
            "phase1_f_mechanical", "phase1_f_interpreted", "phase1_f_lensed",
            # Matrix D (4-stage)
            "phase1_d_mechanical", "phase1_d_interpreted", "phase1_d_lensed",
            # Matrix X
            "phase1_x_mechanical", "phase1_x_interpreted", "phase1_x_lensed", 
            # Matrix E
            "phase1_e_mechanical", "phase1_e_interpreted", "phase1_e_lensed",
            # Matrix Z (special case)
            "phase1_z_lensed", "phase1_z_principles",
        ]
        
        for asset_id in required_assets:
            # Should not raise ValueError
            content = registry.get_text(asset_id)
            assert content.strip(), f"Asset {asset_id} is empty"
            assert "{{json_tail}}" in content, f"Asset {asset_id} missing JSON tail placeholder"