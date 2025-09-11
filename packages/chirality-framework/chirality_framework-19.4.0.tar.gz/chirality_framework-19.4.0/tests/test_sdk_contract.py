#!/usr/bin/env python3
"""
Minimal SDK Contract Test for expects_json Path

Verifies that our adapter successfully calls the OpenAI SDK with
expects_json=True and receives valid JSON responses.

Per colleague_1's guidance: prove SDK contract before full E2E run.
"""

import json
import os
from pathlib import Path

def test_minimal_sdk_contract():
    """Test minimal SDK call with expects_json=True."""
    print("🧪 Testing minimal SDK contract with expects_json=True...")
    
    # Check API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set - cannot test SDK contract")
        return False
    
    print(f"✅ OPENAI_API_KEY found (starts with: {api_key[:10]}...)")
    
    try:
        # Import adapter
        from chirality.infrastructure.llm.openai_adapter import call_responses
        
        print("✅ Successfully imported call_responses adapter")
        
        # Make minimal call with expects_json=True
        print("📞 Making minimal SDK call with expects_json=True...")
        
        response = call_responses(
            instructions="You are a JSON response generator. Always return valid JSON.",
            input="Return a JSON object with 'status': 'success' and 'message': 'SDK contract verified'.",
            expects_json=True,
            store=False,  # Don't store test calls
            metadata={"test": "sdk_contract", "minimal": True}
        )
        
        print("✅ SDK call completed without errors")
        
        # Verify response structure
        if not isinstance(response, dict):
            print(f"❌ Expected dict response, got {type(response)}")
            return False
            
        # Check required fields
        required_fields = ['id', 'output_text', 'usage', 'raw']
        missing_fields = [f for f in required_fields if f not in response]
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
            
        print("✅ Response has correct structure")
        
        # Verify JSON content
        output_text = response.get('output_text', '')
        if not output_text:
            print("❌ Empty output_text in response")
            return False
            
        try:
            parsed_json = json.loads(output_text)
            print(f"✅ Valid JSON received: {parsed_json}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in output_text: {e}")
            print(f"   Raw output: {output_text[:200]}...")
            return False
        
        # Verify metadata capture
        raw_metadata = response.get('raw', {}).get('metadata', {})
        if not raw_metadata:
            print("⚠️  No metadata captured (acceptable)")
        else:
            print(f"✅ Metadata captured: {list(raw_metadata.keys())}")
        
        # Verify usage tracking
        usage = response.get('usage')
        if usage:
            print(f"✅ Usage tracking: {usage}")
        else:
            print("⚠️  No usage tracking (may be acceptable)")
        
        print("✅ SDK contract test passed!")
        return True
        
    except Exception as e:
        print(f"❌ SDK contract test failed: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def test_reasoning_capability_filtering():
    """Test that reasoning gets filtered for incompatible models."""
    print("\n🧪 Testing reasoning capability filtering...")
    
    try:
        from chirality.infrastructure.llm.openai_adapter import LLMClient
        
        client = LLMClient()
        
        # Test reasoning capability check
        gpt4_supports = client._check_reasoning_capability("gpt-4o")
        gpt5_supports = client._check_reasoning_capability("gpt-5")
        
        print(f"✅ gpt-4o supports reasoning: {gpt4_supports} (should be False)")
        print(f"✅ gpt-5 supports reasoning: {gpt5_supports} (should be True)")
        
        if gpt4_supports is not False:
            print("❌ gpt-4o should not support reasoning")
            return False
            
        if gpt5_supports is not True:
            print("❌ gpt-5 should support reasoning")
            return False
        
        print("✅ Reasoning capability filtering working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Reasoning capability test failed: {e}")
        return False


def test_guard_parameter_validation():
    """Test that guards properly validate parameters."""
    print("\n🧪 Testing guard parameter validation...")
    
    try:
        from chirality.infrastructure.api.guards import guard_llm_call
        
        # Test valid parameters
        result = guard_llm_call("test_func", 
                              instructions="test",
                              input="test", 
                              expects_json=True,
                              temperature=0.5)
        print("✅ Valid parameters accepted")
        
        # Test invalid parameter rejection
        try:
            guard_llm_call("test_func", invalid_param="test")
            print("❌ Invalid parameter should have been rejected")
            return False
        except ValueError as e:
            if "Unknown parameters" in str(e):
                print("✅ Invalid parameters properly rejected")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
        # Test model parameter rejection (should be adapter-side only)
        try:
            guard_llm_call("test_func", model="gpt-4")
            print("❌ Model parameter should have been rejected")
            return False
        except ValueError as e:
            if "Unknown parameters" in str(e) and "model" in str(e):
                print("✅ Model parameter properly rejected (adapter-side only)")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
        print("✅ Guard parameter validation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Guard validation test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Running SDK Contract Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Run contract test
    if not test_minimal_sdk_contract():
        all_passed = False
    
    # Run reasoning test  
    if not test_reasoning_capability_filtering():
        all_passed = False
        
    # Run guard test
    if not test_guard_parameter_validation():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All SDK contract tests passed!")
        print("🚀 Ready for Phase-1 E2E testing")
    else:
        print("❌ Some tests failed - fix before proceeding")
        exit(1)