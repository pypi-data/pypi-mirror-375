#!/usr/bin/env python3
"""
Runtime test that inspects orchestrator stages and asserts the adapter 
was invoked with no messages key in kwargs, per colleague_1's suggestion.
"""

import json
from unittest.mock import Mock, patch
from pathlib import Path

from chirality.domain.semantics.lens import generate_lens, apply_lens


def test_lens_functions_no_messages_kwargs():
    """Test that lens functions call adapter without messages kwargs."""
    
    print("🔄 Testing lens functions use proper Responses API parameters...")
    
    # Mock response for Responses API
    mock_response = {"output_text": "test semantic lens result"}
    
    call_responses_calls = []
    
    def mock_call_responses(**kwargs):
        call_responses_calls.append(kwargs)
        return mock_response
    
    # Mock the new call_responses function
    with patch('chirality.domain.semantics.lens.call_responses', mock_call_responses):
        
        # Test generate_lens
        result = generate_lens("Problem Statement", "normative", "necessity")
        assert result == "test semantic lens result"
        assert len(call_responses_calls) == 1
        
        # Verify call used instructions + input, not messages
        kwargs = call_responses_calls[0]
        assert "instructions" in kwargs, "Missing instructions parameter"
        assert "input" in kwargs, "Missing input parameter"
        assert "messages" not in kwargs, "FORBIDDEN: messages parameter found"
        
        print(f"  ✅ generate_lens() uses: {list(kwargs.keys())}")
        
        # Test apply_lens
        call_responses_calls.clear()
        result = apply_lens("test content", "test lens")
        assert result == "test semantic lens result"
        assert len(call_responses_calls) == 1
        
        # Verify call used instructions + input, not messages
        kwargs = call_responses_calls[0]
        assert "instructions" in kwargs, "Missing instructions parameter"
        assert "input" in kwargs, "Missing input parameter"
        assert "messages" not in kwargs, "FORBIDDEN: messages parameter found"
        
        print(f"  ✅ apply_lens() uses: {list(kwargs.keys())}")


def test_semantic_multiply_no_messages_kwargs():
    """Test that semantic resolvers use proper Responses API parameters."""
    
    print("🔄 Testing semantic resolvers use proper Responses API parameters...")
    
    from chirality.infrastructure.semantics.resolvers import semantic_multiply_llm
    
    # Mock response
    mock_response = {"output_text": "justification"}
    
    call_responses_calls = []
    
    def mock_call_responses(**kwargs):
        call_responses_calls.append(kwargs)
        return mock_response
    
    # Mock the new call_responses function  
    with patch('chirality.infrastructure.semantics.resolvers.call_responses', mock_call_responses):
        
        result = semantic_multiply_llm("sufficient", "reason")
        assert result == "justification"
        assert len(call_responses_calls) == 1
        
        # Verify call used instructions + input, not messages
        kwargs = call_responses_calls[0]
        assert "instructions" in kwargs, "Missing instructions parameter"
        assert "input" in kwargs, "Missing input parameter"  
        assert "messages" not in kwargs, "FORBIDDEN: messages parameter found"
        
        print(f"  ✅ semantic_multiply_llm() uses: {list(kwargs.keys())}")


if __name__ == "__main__":
    print("🚀 Running adapter kwargs inspection tests...")
    
    try:
        test_lens_functions_no_messages_kwargs()
        test_semantic_multiply_no_messages_kwargs()
        
        print("\n🎉 ALL ADAPTER KWARGS TESTS PASSED!")
        print("✅ No messages kwargs found in adapter calls")
        print("✅ All functions use instructions + input format")
        print("✅ Responses API compliance verified at runtime")
        
    except Exception as e:
        print(f"\n❌ ADAPTER KWARGS TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)