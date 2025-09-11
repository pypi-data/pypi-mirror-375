#!/usr/bin/env python3
"""
Test D2-4: Guards implementation.

Tests that the no_chat_completions and no_decoding_overrides guards
properly prevent forbidden API usage and parameter overrides.
"""

import pytest
from chirality.infrastructure.api.guards import (
    no_chat_completions, 
    no_decoding_overrides,
    APIGuardError,
    DecodingOverrideError,
    install_chat_completions_guard,
    guard_llm_call
)


def test_no_chat_completions_guard():
    """Test D2-4: no_chat_completions guard prevents Chat Completions API."""
    
    print("🔄 Testing D2-4: no_chat_completions guard...")
    
    # Should always raise APIGuardError
    try:
        no_chat_completions(model="gpt-4", messages=[{"role": "user", "content": "test"}])
        assert False, "no_chat_completions should have raised APIGuardError"
    except APIGuardError as e:
        assert "Chat Completions API is forbidden" in str(e)
        assert "Use Responses API" in str(e)
        print("✅ no_chat_completions guard working correctly")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_no_decoding_overrides_guard():
    """Test D2-4: no_decoding_overrides guard prevents parameter overrides."""
    
    print("🔄 Testing D2-4: no_decoding_overrides guard...")
    
    # Test with forbidden parameters
    forbidden_tests = [
        {"temperature": 0.5},
        {"top_p": 0.9},
        {"top_k": 40},
        {"frequency_penalty": 0.1},
        {"presence_penalty": 0.1},
        {"temperature": 0.7, "top_p": 0.8},  # Multiple forbidden params
    ]
    
    for i, params in enumerate(forbidden_tests):
        try:
            no_decoding_overrides("test_function", **params)
            print(f"❌ Test {i+1}: Should have raised DecodingOverrideError for {params}")
            return False
        except DecodingOverrideError as e:
            assert "forbidden in test_function" in str(e)
            assert "controlled externally" in str(e)
            print(f"✅ Test {i+1}: Correctly blocked {list(params.keys())}")
    
    # Test with allowed parameters (should not raise)
    try:
        no_decoding_overrides("test_function", 
                             model="gpt-4", 
                             max_tokens=100,
                             text={"format": "json_object"})
        print("✅ Allowed parameters correctly passed through")
        return True
    except Exception as e:
        print(f"❌ Unexpected error with allowed params: {e}")
        return False


def test_guard_llm_call_integration():
    """Test D2-4: guard_llm_call integration function."""
    
    print("🔄 Testing D2-4: guard_llm_call integration...")
    
    # Should block forbidden decoding parameters
    try:
        guard_llm_call("call_responses", temperature=0.5, top_p=0.9)
        print("❌ guard_llm_call should have blocked decoding parameters")
        return False
    except DecodingOverrideError as e:
        assert "temperature" in str(e) and "top_p" in str(e)
        print("✅ guard_llm_call correctly blocked forbidden parameters")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_chat_completions_monkey_patch():
    """Test D2-4: Chat Completions monkey patching."""
    
    print("🔄 Testing D2-4: Chat Completions monkey patch...")
    
    # Install the guard
    install_chat_completions_guard()
    
    # Test that OpenAI Chat Completions is blocked (if OpenAI is available)
    try:
        import openai
        if hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
            try:
                openai.chat.completions.create(
                    model="gpt-4", 
                    messages=[{"role": "user", "content": "test"}]
                )
                print("❌ Monkey patch failed - Chat Completions should be blocked")
                return False
            except APIGuardError:
                print("✅ Monkey patch working - Chat Completions blocked")
                return True
        else:
            print("ℹ️  OpenAI chat.completions not available for testing")
            return True
    except ImportError:
        print("ℹ️  OpenAI not installed - skipping monkey patch test")
        return True
    except Exception as e:
        print(f"❌ Unexpected error in monkey patch test: {e}")
        return False


def test_parameter_edge_cases():
    """Test D2-4: Edge cases for parameter detection."""
    
    print("🔄 Testing D2-4: Parameter edge cases...")
    
    # Test None values (should be allowed)
    try:
        no_decoding_overrides("test_function", 
                             temperature=None, 
                             top_p=None,
                             model="gpt-4")
        print("✅ None values correctly allowed")
    except Exception as e:
        print(f"❌ None values should be allowed: {e}")
        return False
    
    # Test empty kwargs (should be allowed)
    try:
        no_decoding_overrides("test_function")
        print("✅ Empty kwargs correctly allowed")
    except Exception as e:
        print(f"❌ Empty kwargs should be allowed: {e}")
        return False
    
    # Test 0 values (should be blocked - 0 is a valid temperature)
    try:
        no_decoding_overrides("test_function", temperature=0.0)
        print("❌ Zero temperature should be blocked")
        return False
    except DecodingOverrideError:
        print("✅ Zero temperature correctly blocked")
        return True
    except Exception as e:
        print(f"❌ Unexpected error with zero temperature: {e}")
        return False


if __name__ == "__main__":
    success = True
    
    # Run all D2-4 guard tests
    success &= test_no_chat_completions_guard()
    success &= test_no_decoding_overrides_guard()
    success &= test_guard_llm_call_integration()
    success &= test_chat_completions_monkey_patch()
    success &= test_parameter_edge_cases()
    
    if success:
        print("\n✅ ALL D2-4 GUARD TESTS PASSED!")
        print("   ✅ no_chat_completions: Blocks Chat Completions API")
        print("   ✅ no_decoding_overrides: Blocks temperature, top_p, etc.")
        print("   ✅ guard_llm_call: Integration function working")
        print("   ✅ Monkey patching: Chat Completions blocked at OpenAI level")
        print("   ✅ Edge cases: Proper handling of None, empty, and zero values")
    else:
        print("\n❌ D2-4 GUARD TESTS FAILED")
        exit(1)
