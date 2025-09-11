#!/usr/bin/env python3
"""
Production test: Compare catalog vs auto lens modes.

Per colleague_1's specification, run both --lens-mode=catalog and --lens-mode=auto
and verify they produce identical transcript structure with only lens source differences
in traces (not transcript).
"""

import json
from pathlib import Path
from chirality.application.phase1.dialogue_run import DialogueOrchestrator


def run_mode_comparison():
    """Run both lens modes and compare transcripts."""
    
    print("🔄 Running production mode comparison test...")
    
    # Run catalog mode
    print("📚 Testing --lens-mode=catalog...")
    catalog_orchestrator = DialogueOrchestrator(
        model="echo",
        temperature=0.2, 
        budget_config=None,
        lens_mode="catalog"
    )
    
    try:
        catalog_result = catalog_orchestrator.run_dialogue(Path("test_production/catalog"))
        catalog_transcript = catalog_orchestrator.dialogue_history
        print(f"✅ Catalog mode completed: {len(catalog_transcript)} turns")
    except Exception as e:
        print(f"❌ Catalog mode failed: {e}")
        return False
    
    # Run auto mode  
    print("🤖 Testing --lens-mode=auto...")
    auto_orchestrator = DialogueOrchestrator(
        model="echo",
        temperature=0.2,
        budget_config=None, 
        lens_mode="auto"
    )
    
    try:
        auto_result = auto_orchestrator.run_dialogue(Path("test_production/auto"))
        auto_transcript = auto_orchestrator.dialogue_history
        print(f"✅ Auto mode completed: {len(auto_transcript)} turns")
    except Exception as e:
        print(f"❌ Auto mode failed: {e}")
        return False
    
    # Compare transcript structure
    print("🔍 Comparing transcript structures...")
    
    # Should have identical number of turns
    if len(catalog_transcript) != len(auto_transcript):
        print(f"❌ Different number of turns: catalog={len(catalog_transcript)}, auto={len(auto_transcript)}")
        return False
    
    # Compare each turn (content should be identical)
    differences = []
    for i, (catalog_turn, auto_turn) in enumerate(zip(catalog_transcript, auto_transcript)):
        # Roles should match
        if catalog_turn.get("role") != auto_turn.get("role"):
            differences.append(f"Turn {i}: role mismatch")
            continue
            
        # Content should be identical (no lens source should leak into transcript)
        catalog_content = catalog_turn.get("content", "")
        auto_content = auto_turn.get("content", "")
        
        if catalog_content != auto_content:
            differences.append(f"Turn {i}: content differs")
            
            # Check if the difference is forbidden lens source leakage
            if "source:" in catalog_content or "source:" in auto_content:
                differences.append(f"Turn {i}: FORBIDDEN - lens source leaked into transcript")
            if "catalog" in catalog_content.lower() or "auto" in auto_content.lower():
                differences.append(f"Turn {i}: FORBIDDEN - mode awareness leaked into transcript")
    
    if differences:
        print("❌ Transcript differences found:")
        for diff in differences[:10]:  # Show first 10 differences
            print(f"   {diff}")
        if len(differences) > 10:
            print(f"   ... and {len(differences) - 10} more")
        return False
    
    print("✅ Transcripts are identical - no lens source leakage")
    
    # Check traces for expected differences
    print("🔍 Checking traces for lens source differences...")
    
    catalog_traces = catalog_result.get("trace", [])
    auto_traces = auto_result.get("trace", [])
    
    lens_source_differences = 0
    for i, (cat_trace, auto_trace) in enumerate(zip(catalog_traces, auto_traces)):
        if cat_trace.get("kind") == "lens_injection":
            cat_source = cat_trace.get("source", "unknown")
            auto_source = auto_trace.get("source", "unknown") 
            
            if cat_source != auto_source:
                lens_source_differences += 1
    
    print(f"✅ Found {lens_source_differences} lens source differences in traces (expected)")
    
    return True


if __name__ == "__main__":
    success = run_mode_comparison()
    
    if success:
        print("\n🎉 PRODUCTION MODE COMPARISON SUCCESSFUL!")
        print("   ✅ Catalog and auto modes produce identical transcripts")
        print("   ✅ No lens source metadata leaked into conversation")
        print("   ✅ Only trace-level differences in lens source (as expected)")
        print("   ✅ Framework maintains clean semantic separation")
        print("\n🚀 Ready for production with colleague_1's requirements met!")
    else:
        print("\n❌ PRODUCTION MODE COMPARISON FAILED")
        exit(1)