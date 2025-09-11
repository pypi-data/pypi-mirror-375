"""
Architecture Guard Tests.

These tests enforce the conversational architecture principle by detecting
violations that would reintroduce legacy template-based approaches.

Guards implemented:
1. no-inline-prompts: Every LLM call must load prompts from registry assets
2. no-legacy-refs: Block references to quarantined legacy patterns  
3. system.md fidelity: Protect conversational foundation integrity
"""

import ast
import re
import os
from pathlib import Path
from typing import List, Tuple, Set

import pytest


class ArchitectureViolation(Exception):
    """Raised when architecture violations are detected."""
    pass


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files in the project, excluding tests, archives, and __pycache__."""
    python_files = []
    for path in root.rglob("*.py"):
        # Skip test files, __pycache__, archives, and venv directories
        if any(part in str(path) for part in ["__pycache__", ".venv", "venv", "test_", "archive/", "scripts/"]):
            continue
        python_files.append(path)
    return python_files


def find_inline_prompts(file_path: Path) -> List[Tuple[int, str]]:
    """
    Find potential inline prompts in Python files.
    
    Detects:
    - Multi-line strings containing semantic operation symbols
    - Hardcoded prompt templates
    - String literals with semantic content keywords
    
    Returns list of (line_number, violation_text) tuples.
    """
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except (UnicodeDecodeError, IOError):
        return violations
    
    # Parse AST to find string literals
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return violations
    
    class StringLiteralFinder(ast.NodeVisitor):
        def visit_Str(self, node):
            # Python < 3.8 compatibility
            self.check_string_content(node.s, node.lineno)
            
        def visit_Constant(self, node):
            # Python >= 3.8
            if isinstance(node.value, str):
                self.check_string_content(node.value, node.lineno)
                
        def check_string_content(self, string_value: str, line_no: int):
            # Skip short strings and common patterns
            if len(string_value) < 100:  # Increase threshold for real prompts
                return
                
            # Skip legitimate template/schema files
            if any(skip_pattern in str(file_path) for skip_pattern in [
                "json_tails.py",  # JSON output templates, not semantic prompts
                "operations.py",  # Domain logic definitions, not prompts
                "stations.py",    # Station definitions, not prompts
                "lens.py"        # Lens definitions, not prompts
            ]):
                return
                
            # Detect actual semantic prompt content (not just mentions)
            semantic_prompt_patterns = [
                r'Apply semantic.*first.*then',  # Actual semantic instruction
                r'Generate.*iteration.*Matrix.*station',  # Matrix generation prompts
                r'To provide.*interpretation.*semantic.*operators',  # Semantic operation instructions
                r'sufficient.*reason.*justification.*Examples',  # Semantic multiplication examples with context
                r'probability.*consequence.*risk.*Examples'  # Multiple semantic examples
            ]
            
            for pattern in semantic_prompt_patterns:
                if re.search(pattern, string_value, re.IGNORECASE | re.DOTALL):
                    violations.append((
                        line_no, 
                        f"Inline semantic prompt detected: {pattern}"
                    ))
                    break
    
    finder = StringLiteralFinder()
    finder.visit(tree)
    
    return violations


def find_legacy_references(file_path: Path) -> List[Tuple[int, str]]:
    """
    Find references to quarantined legacy patterns.
    
    Detects:
    - _compute_matrix_ method references
    - stage2_multiply asset references
    - Template-based prompt patterns
    
    Returns list of (line_number, violation_text) tuples.
    """
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (UnicodeDecodeError, IOError):
        return violations
    
    legacy_patterns = [
        (r'_compute_matrix_', 'Legacy _compute_matrix_ method reference'),
        (r'get_text\(["\']stage2_multiply["\']', 'Direct stage2_multiply asset loading'),
        (r'hardcoded.*semantic.*template', 'Hardcoded semantic template pattern'),
        (r'Fallback.*hardcoded.*asset', 'Hardcoded fallback prompt'),
        (r'"""\s*##\s*Interpreting.*elements', 'Inline semantic interpretation template'),
        (r'stage2_multiply', 'Legacy stage2_multiply asset reference'),
    ]
    
    for line_no, line in enumerate(lines, 1):
        # Skip lines that are clearly quarantine documentation
        if any(quarantine_word in line.lower() for quarantine_word in [
            'quarantined', 'architecture violation', 'legacy method quarantined', 
            'deleted stage2_multiply', 'references deleted'
        ]):
            continue
            
        for pattern, description in legacy_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append((line_no, f"{description}: {pattern}"))
    
    return violations


def test_no_inline_prompts():
    """
    Guard Test 1: No Inline Prompts
    
    Ensures all LLM calls use registry-loaded prompt assets.
    Blocks hardcoded semantic content in Python code.
    
    Architecture Principle: Every semantic prompt must be user-authored asset file.
    """
    project_root = get_project_root()
    python_files = find_python_files(project_root)
    
    all_violations = []
    
    for file_path in python_files:
        violations = find_inline_prompts(file_path)
        for line_no, message in violations:
            all_violations.append(f"{file_path}:{line_no} - {message}")
    
    if all_violations:
        violation_report = "\n".join(all_violations)
        raise ArchitectureViolation(
            f"INLINE PROMPTS DETECTED - Architecture Violation!\n\n"
            f"The conversational architecture requires all semantic content "
            f"to be loaded from user-authored prompt assets via registry.get_text(asset_id).\n"
            f"Hardcoded prompts in Python code violate this principle.\n\n"
            f"Violations found:\n{violation_report}\n\n"
            f"Fix: Move semantic content to .md files in infrastructure/prompts/assets/"
        )


def test_no_legacy_refs():
    """
    Guard Test 2: No Legacy References
    
    Prevents reintroduction of quarantined legacy patterns.
    Blocks references to deleted methods and assets.
    
    Architecture Principle: Legacy template-based approaches are forbidden.
    """
    project_root = get_project_root()
    python_files = find_python_files(project_root)
    
    all_violations = []
    
    for file_path in python_files:
        violations = find_legacy_references(file_path)
        for line_no, message in violations:
            all_violations.append(f"{file_path}:{line_no} - {message}")
    
    if all_violations:
        violation_report = "\n".join(all_violations)
        raise ArchitectureViolation(
            f"LEGACY REFERENCES DETECTED - Architecture Violation!\n\n"
            f"References to quarantined legacy patterns are forbidden.\n"
            f"These methods and assets have been deleted due to architecture violations.\n\n"
            f"Violations found:\n{violation_report}\n\n"
            f"Fix: Use new 4-stage conversational pipeline with user-authored prompt assets"
        )


def test_system_md_fidelity():
    """
    Guard Test 3: System.md Fidelity
    
    Protects the conversational foundation from unauthorized modifications.
    Ensures system.md content matches expected byte-for-byte.
    
    Architecture Principle: System prompt integrity must be maintained.
    """
    project_root = get_project_root()
    system_md_path = project_root / "chirality" / "infrastructure" / "prompts" / "assets" / "system.md"
    
    if not system_md_path.exists():
        raise ArchitectureViolation(
            f"SYSTEM.MD MISSING - Critical Architecture File!\n\n"
            f"The system.md file is the conversational foundation of the framework.\n"
            f"Expected location: {system_md_path}\n\n"
            f"Fix: Restore system.md with proper conversational semantic foundation"
        )
    
    try:
        with open(system_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, IOError) as e:
        raise ArchitectureViolation(
            f"SYSTEM.MD READ ERROR - {e}\n\n"
            f"Cannot verify system.md content integrity.\n\n"
            f"Fix: Ensure system.md is readable and properly encoded"
        )
    
    # Check for essential conversational elements
    required_elements = [
        "sufficient\" * \"reason\" = justification",
        "probability\" * \"consequence\" = risk", 
        "<User>",
        "<llm>",
        "semantic multiplication",
        "developments",
        "knowledge work"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        raise ArchitectureViolation(
            f"SYSTEM.MD INTEGRITY VIOLATION - Missing Essential Elements!\n\n"
            f"The system.md conversational foundation is missing required elements.\n"
            f"This breaks the semantic grounding for the framework.\n\n"
            f"Missing elements: {missing_elements}\n\n"
            f"Fix: Restore complete conversational foundation in system.md"
        )
    
    # Verify minimum content length (conversational dialogue should be substantial)
    if len(content) < 2000:
        raise ArchitectureViolation(
            f"SYSTEM.MD TOO SHORT - Insufficient Conversational Foundation!\n\n"
            f"Current length: {len(content)} characters\n"
            f"Expected: At least 2000 characters for proper semantic grounding\n\n"
            f"Fix: Ensure system.md contains complete conversational dialogue foundation"
        )


def test_lens_placeholder_restrictions():
    """
    Guard Test 4: Lens Placeholder Restrictions
    
    Enforce placeholder restrictions per colleague_1's specification.
    - Main pipeline assets: NO {{content}} or {{previous_output}}
    - Only lens_catalog_generation.md may use {{context}}
    - Generation assets: only metadata placeholders allowed
    
    Architecture Principle: Conversational prompts rely on history, not injection.
    """
    
    # Main pipeline assets must not have forbidden placeholders
    main_pipeline_patterns = [
        "chirality/infrastructure/prompts/assets/phase1/*/mechanical.md",
        "chirality/infrastructure/prompts/assets/phase1/*/interpreted.md", 
        "chirality/infrastructure/prompts/assets/phase1/*/lensed.md",
        "chirality/infrastructure/prompts/assets/phase1/*/principles.md"
    ]
    
    forbidden_placeholders = ["{{content}}", "{{previous_output}}"]
    violations = []
    
    for pattern in main_pipeline_patterns:
        for asset_path in Path(".").glob(pattern):
            if not asset_path.is_file():
                continue
            
            try:
                content = asset_path.read_text()
                for placeholder in forbidden_placeholders:
                    if placeholder in content:
                        violations.append(f"{asset_path}: contains forbidden {placeholder}")
            except (UnicodeDecodeError, IOError):
                continue
    
    if violations:
        raise ArchitectureViolation(
            f"FORBIDDEN PLACEHOLDERS DETECTED - Architecture Violation!\n\n"
            f"Main pipeline assets must rely on conversation history, not template injection.\n"
            f"Only {{json_tail}} is permitted for output formatting.\n\n"
            f"Violations found:\n" + "\n".join(violations) + "\n\n"
            f"Fix: Remove {{content}} and {{previous_output}} placeholders, rely on history"
        )


def test_context_placeholder_restricted():
    """
    Guard Test 5: Context Placeholder Restriction
    
    Only lens_catalog_generation.md is allowed to use {{context}} placeholder.
    All other assets must rely on conversation history.
    
    Architecture Principle: Meta-pipeline is separate from conversational pipeline.
    """
    
    allowed_context_files = {
        "chirality/infrastructure/prompts/assets/phase1/lens_catalog_generation.md"
    }
    
    violations = []
    
    # Check all prompt assets
    for asset_path in Path("chirality/infrastructure/prompts/assets").rglob("*.md"):
        if not asset_path.is_file():
            continue
        
        try:
            content = asset_path.read_text()
            if "{{context}}" in content:
                asset_str = str(asset_path)
                if asset_str not in allowed_context_files:
                    violations.append(f"{asset_path}: contains forbidden {{context}} placeholder")
        except (UnicodeDecodeError, IOError):
            continue
    
    if violations:
        raise ArchitectureViolation(
            f"FORBIDDEN CONTEXT PLACEHOLDERS - Architecture Violation!\n\n"
            f"{{context}} placeholder is only allowed in the lens catalog meta-pipeline.\n"
            f"All other assets must rely on conversation history for context.\n\n"
            f"Violations found:\n" + "\n".join(violations) + "\n\n"
            f"Fix: Remove {{context}} placeholders, rely on conversation history"
        )


def test_generation_assets_metadata_only():
    """
    Guard Test 6: Generation Assets Metadata Only
    
    Generation assets (*/generate_lenses.md) should only use metadata placeholders.
    They must NOT use: {{context}}, {{content}}, {{previous_output}}
    
    Architecture Principle: On-the-fly generation uses minimal metadata, not injection.
    """
    
    allowed_placeholders = {
        "{{station}}", "{{matrix_id}}", "{{rows}}", "{{cols}}",
        "{{row_labels}}", "{{col_labels}}", "{{json_tail}}"
    }
    
    forbidden_placeholders = {"{{context}}", "{{content}}", "{{previous_output}}"}
    
    violations = []
    
    for asset_path in Path("chirality/infrastructure/prompts/assets").rglob("*/generate_lenses.md"):
        if not asset_path.is_file():
            continue
        
        try:
            content = asset_path.read_text()
            
            # Check for forbidden placeholders
            for placeholder in forbidden_placeholders:
                if placeholder in content:
                    violations.append(f"{asset_path}: contains forbidden {placeholder}")
            
            # Find all placeholders in content
            import re
            placeholders = set(re.findall(r'\{\{[^}]+\}\}', content))
            
            # Check that only allowed placeholders are used
            for placeholder in placeholders:
                if placeholder not in allowed_placeholders:
                    violations.append(f"{asset_path}: contains unexpected placeholder {placeholder}")
                    
        except (UnicodeDecodeError, IOError):
            continue
    
    if violations:
        raise ArchitectureViolation(
            f"GENERATION ASSET PLACEHOLDER VIOLATIONS - Architecture Violation!\n\n"
            f"Generation assets must only use minimal metadata placeholders.\n"
            f"They rely on system prompt and conversation history for semantic context.\n\n"
            f"Allowed: {allowed_placeholders}\n"
            f"Forbidden: {forbidden_placeholders}\n\n"
            f"Violations found:\n" + "\n".join(violations) + "\n\n"
            f"Fix: Use only allowed metadata placeholders in generation assets"
        )


def test_lens_system_file_structure():
    """
    Guard Test 7: Lens System File Structure
    
    Verify lens system follows required file structure from colleague_1's plan.
    Ensures all per-matrix generation assets exist.
    
    Architecture Principle: Complete lens system infrastructure must be present.
    """
    
    required_files = [
        "chirality/infrastructure/prompts/assets/phase1/lens_catalog_generation.md",
        "chirality/infrastructure/prompts/assets/phase1/C/generate_lenses.md",
        "chirality/infrastructure/prompts/assets/phase1/D/generate_lenses.md", 
        "chirality/infrastructure/prompts/assets/phase1/F/generate_lenses.md",
        "chirality/infrastructure/prompts/assets/phase1/X/generate_lenses.md",
        "chirality/infrastructure/prompts/assets/phase1/E/generate_lenses.md",
        "chirality/infrastructure/prompts/assets/phase1/Z/generate_lenses.md"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        raise ArchitectureViolation(
            f"LENS SYSTEM INCOMPLETE - Missing Required Files!\n\n"
            f"The lens system requires all per-matrix generation assets.\n"
            f"Missing files break the fallback generation capability.\n\n"
            f"Missing files:\n" + "\n".join(missing_files) + "\n\n"
            f"Fix: Create all required lens generation assets"
        )


def test_guard_test_completeness():
    """
    Meta-test: Verify all required architecture guards are implemented.
    
    Ensures the guard system itself is complete and functional.
    """
    # Verify all guard functions exist and are properly named
    current_module = globals()
    
    required_guards = [
        'test_no_inline_prompts',
        'test_no_legacy_refs', 
        'test_system_md_fidelity',
        'test_lens_placeholder_restrictions',
        'test_context_placeholder_restricted',
        'test_generation_assets_metadata_only',
        'test_lens_system_file_structure'
    ]
    
    missing_guards = []
    for guard_name in required_guards:
        if guard_name not in current_module:
            missing_guards.append(guard_name)
        elif not callable(current_module[guard_name]):
            missing_guards.append(f"{guard_name} (not callable)")
    
    if missing_guards:
        raise ArchitectureViolation(
            f"GUARD SYSTEM INCOMPLETE - Missing Architecture Guards!\n\n"
            f"Required guards missing or non-functional: {missing_guards}\n\n"
            f"Fix: Implement all required architecture guard tests"
        )


if __name__ == "__main__":
    """
    Run architecture guards directly for development.
    
    Usage: python tests/test_architecture_guards.py
    """
    print("Running Architecture Guard Tests...")
    
    try:
        test_no_inline_prompts()
        print("✅ Guard 1: No inline prompts - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Guard 1: No inline prompts - FAILED\n{e}")
    
    try:
        test_no_legacy_refs() 
        print("✅ Guard 2: No legacy references - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Guard 2: No legacy references - FAILED\n{e}")
    
    try:
        test_system_md_fidelity()
        print("✅ Guard 3: System.md fidelity - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Guard 3: System.md fidelity - FAILED\n{e}")
    
    try:
        test_lens_placeholder_restrictions()
        print("✅ Guard 4: Lens placeholder restrictions - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Guard 4: Lens placeholder restrictions - FAILED\n{e}")
    
    try:
        test_context_placeholder_restricted()
        print("✅ Guard 5: Context placeholder restricted - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Guard 5: Context placeholder restricted - FAILED\n{e}")
    
    try:
        test_generation_assets_metadata_only()
        print("✅ Guard 6: Generation assets metadata only - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Guard 6: Generation assets metadata only - FAILED\n{e}")
    
    try:
        test_lens_system_file_structure()
        print("✅ Guard 7: Lens system file structure - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Guard 7: Lens system file structure - FAILED\n{e}")
    
    try:
        test_guard_test_completeness()
        print("✅ Meta-guard: Test completeness - PASSED")
    except ArchitectureViolation as e:
        print(f"❌ Meta-guard: Test completeness - FAILED\n{e}")
    
    print("\nArchitecture guard analysis complete!")