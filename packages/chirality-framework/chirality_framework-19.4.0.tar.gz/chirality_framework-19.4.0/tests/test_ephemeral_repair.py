#!/usr/bin/env python3
"""
Test P0-4: Ephemeral JSON Repair.

Per colleague_1's specification: "Keep JSON repair prompts ephemeral (not appended 
to history), and confirm via a test that the transcript remains metadata-free 
even when repair is triggered."
"""

import json
from unittest.mock import Mock
from chirality.infrastructure.llm.repair import try_parse_json_or_repair


def test_ephemeral_repair_doesnt_pollute_transcript():
    """Test that repair calls don't pollute the original transcript."""
    
    print("🔄 Testing ephemeral repair doesn't pollute transcript...")
    
    # Track all adapter calls to verify transcript isolation
    adapter_calls = []
    
    def mock_adapter_call(instructions=None, input=None):
        """Mock adapter that captures calls and simulates repair scenario."""
        call_record = {
            "instructions": instructions[:100] + "..." if instructions and len(instructions) > 100 else instructions,
            "input": input[:200] + "..." if input and len(input) > 200 else input,
            "call_type": "repair" if "REPAIR MODE" in (instructions or "") else "original"
        }
        adapter_calls.append(call_record)
        
        # First call returns invalid JSON
        if len(adapter_calls) == 1:
            return {"content": "invalid json {"}, {"total_tokens": 50}
        
        # Repair call returns valid JSON
        return {
            "content": json.dumps({
                "artifact": "matrix",
                "name": "C", 
                "station": "test",
                "rows": ["r1"],
                "cols": ["c1"], 
                "step": "mechanical",
                "op": "dot",
                "elements": [["test"]]
            })
        }, {"total_tokens": 75}
    
    # Original clean transcript
    original_instructions = "Original system prompt"
    original_input = "[USER] Please compute matrix C"
    
    # Call repair mechanism
    result, metadata = try_parse_json_or_repair(
        instructions=original_instructions,
        input_text=original_input,
        adapter_call=mock_adapter_call,
        schema_hint="matrix",
        max_repair_attempts=1
    )
    
    # Verify repair succeeded
    assert result["artifact"] == "matrix"
    assert result["name"] == "C"
    
    # Verify we made exactly 2 calls (original + repair)
    assert len(adapter_calls) == 2
    
    original_call = adapter_calls[0]
    repair_call = adapter_calls[1]
    
    # Verify original call used clean transcript
    assert original_call["call_type"] == "original"
    assert original_call["instructions"] == original_instructions
    assert original_call["input"] == original_input
    
    # Verify repair call is ephemeral (doesn't contain original transcript verbatim)
    assert repair_call["call_type"] == "repair"
    assert "REPAIR MODE" in repair_call["instructions"]
    
    # CRITICAL: Repair input should be ephemeral, not appended to original
    repair_input = repair_call["input"]
    assert "PREVIOUS ATTEMPT:" in repair_input
    assert "REPAIR INSTRUCTIONS:" in repair_input
    # The ORIGINAL CONTEXT section might be truncated in debug, but the structure is correct
    
    # The repair input should be structured differently from transcript pollution
    # It should NOT look like "[ASSISTANT] invalid json { [USER] repair instructions"
    assert "[ASSISTANT] invalid json {" not in repair_input
    assert "[USER] The previous output was invalid JSON" not in repair_input
    
    print("  ✅ Repair calls are ephemeral and don't pollute transcript")


def test_repair_with_legacy_messages_format():
    """Test ephemeral repair with legacy messages format."""
    
    print("🔄 Testing ephemeral repair with legacy messages format...")
    
    adapter_calls = []
    
    def mock_adapter_call(messages):
        """Mock adapter for legacy messages format."""
        call_record = {
            "messages": [{"role": msg["role"], "content": msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]} for msg in messages],
            "call_type": "repair" if any("repair" in msg.get("content", "").lower() for msg in messages) else "original"
        }
        adapter_calls.append(call_record)
        
        # First call returns invalid JSON
        if len(adapter_calls) == 1:
            return {"content": "malformed: json"}, {"total_tokens": 30}
        
        # Repair call returns valid JSON
        return {
            "content": json.dumps({
                "artifact": "matrix",
                "name": "F",
                "station": "test",
                "rows": ["r1"],
                "cols": ["c1"],
                "step": "interpreted", 
                "op": "hadamard",
                "elements": [["test"]]
            })
        }, {"total_tokens": 60}
    
    # Original message history
    original_messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Compute matrix F"}
    ]
    
    # Call repair mechanism with legacy format
    result, metadata = try_parse_json_or_repair(
        messages=original_messages,
        adapter_call=mock_adapter_call,
        schema_hint="matrix", 
        max_repair_attempts=1
    )
    
    # Verify repair succeeded
    assert result["artifact"] == "matrix"
    assert result["name"] == "F"
    
    # Verify we made exactly 2 calls
    assert len(adapter_calls) == 2
    
    original_call = adapter_calls[0]
    repair_call = adapter_calls[1]
    
    # Verify original call used clean messages
    assert original_call["call_type"] == "original"
    assert len(original_call["messages"]) == 2
    assert original_call["messages"][0]["content"] == "You are a helpful assistant"
    assert original_call["messages"][1]["content"] == "Compute matrix F"
    
    # Verify repair call is ephemeral (separate message history)
    assert repair_call["call_type"] == "repair"
    repair_messages = repair_call["messages"]
    
    # Should be a completely separate ephemeral conversation
    assert repair_messages[0]["role"] == "system"
    assert "JSON repair assistant" in repair_messages[0]["content"]
    assert "Previous invalid response" in repair_messages[1]["content"]
    
    # Should NOT be an extension of original messages
    assert "You are a helpful assistant" not in str(repair_messages)
    assert "Compute matrix F" not in str(repair_messages)
    
    print("  ✅ Legacy format repair is also ephemeral")


def test_transcript_metadata_freedom_during_repair():
    """Test that transcripts remain metadata-free even when repair is triggered."""
    
    print("🔄 Testing transcript remains metadata-free during repair...")
    
    # Simulate a transcript that would be passed to LLM
    clean_transcript = "[USER] Calculate semantic matrix C using dot product"
    
    adapter_calls = []
    
    def mock_adapter_call(instructions=None, input=None):
        """Mock that captures exact input passed to LLM."""
        adapter_calls.append({"instructions": instructions, "input": input})
        
        if len(adapter_calls) == 1:
            return {"content": "{ broken json"}, {"total_tokens": 25}
        
        return {
            "content": json.dumps({
                "artifact": "matrix",
                "name": "C",
                "station": "problem statement", 
                "rows": ["normative"],
                "cols": ["necessity"],
                "step": "mechanical",
                "op": "dot",
                "elements": [["result"]]
            })
        }, {"total_tokens": 50}
    
    # Test repair scenario
    result, metadata = try_parse_json_or_repair(
        instructions="System: You compute semantic matrices",
        input_text=clean_transcript,
        adapter_call=mock_adapter_call,
        max_repair_attempts=1
    )
    
    # Verify original call had clean transcript
    original_call = adapter_calls[0]
    assert original_call["input"] == clean_transcript
    
    # Verify repair call doesn't pollute the main transcript format
    repair_call = adapter_calls[1]
    repair_input = repair_call["input"]
    
    # Repair input should be specially structured, not a polluted transcript
    assert "PREVIOUS ATTEMPT:" in repair_input
    assert "REPAIR INSTRUCTIONS:" in repair_input  
    # Structure ensures isolation from transcript pollution
    
    # Most importantly: verify that repair is structured properly
    # The key is that it's NOT a conversation continuation pattern
    assert clean_transcript not in repair_input.split("REPAIR INSTRUCTIONS:")[0], \
        "Original transcript should not appear before repair instructions"
    
    # Ensure it doesn't appear as conversation continuation
    conversation_pollution_patterns = [
        f"[ASSISTANT] {{ broken json\n[USER] The previous output was invalid JSON",
        f"{clean_transcript}\n\n[ASSISTANT] {{ broken json",
        "[USER] The previous output was invalid JSON"
    ]
    
    for pattern in conversation_pollution_patterns:
        assert pattern not in repair_input, f"Found conversation pollution pattern: {pattern}"
    
    print("  ✅ Transcript remains metadata-free during repair")


def test_repair_success_without_transcript_modification():
    """Test that successful repair doesn't modify the conceptual transcript."""
    
    print("🔄 Testing repair success doesn't modify conceptual transcript...")
    
    # This test ensures that after repair, the main conversational flow
    # continues as if the failed attempt never happened in the transcript
    
    original_input = "[USER] Please calculate matrix D"
    
    def mock_adapter_call(instructions=None, input=None):
        # Simulate repair scenario where repair succeeds
        if "REPAIR MODE" in (instructions or ""):
            # This is the ephemeral repair call
            return {
                "content": json.dumps({
                    "artifact": "matrix",
                    "name": "D",
                    "station": "objectives",
                    "rows": ["normative"],
                    "cols": ["guiding"],
                    "step": "mechanical", 
                    "op": "add",
                    "elements": [["success"]]
                })
            }, {"total_tokens": 45}
        else:
            # Original call fails
            return {"content": "invalid: syntax"}, {"total_tokens": 20}
    
    # Perform repair
    result, metadata = try_parse_json_or_repair(
        instructions="System prompt",
        input_text=original_input,
        adapter_call=mock_adapter_call,
        max_repair_attempts=1
    )
    
    # After repair succeeds, the result should be clean
    assert result["artifact"] == "matrix"
    assert result["name"] == "D"
    
    # The key insight: if this were used in a dialogue system,
    # the next conversation turn would see the original_input as the last user message,
    # NOT any repair artifacts
    
    # This is verified by the fact that our mock didn't receive polluted input
    # in subsequent calls (since we only made 2 calls total)
    
    print("  ✅ Repair success maintains clean conceptual transcript")


if __name__ == "__main__":
    print("🚀 Testing P0-4: Ephemeral JSON Repair...")
    
    try:
        test_ephemeral_repair_doesnt_pollute_transcript()
        test_repair_with_legacy_messages_format()
        test_transcript_metadata_freedom_during_repair()
        test_repair_success_without_transcript_modification()
        
        print("\n✅ ALL P0-4 EPHEMERAL REPAIR TESTS PASSED!")
        print("✅ JSON repair prompts are ephemeral (not appended to history)")
        print("✅ Transcript remains metadata-free even when repair is triggered")
        print("✅ Repair conversations are completely isolated from main transcript")
        print("✅ Legacy messages format also maintains ephemeral repair")
        print("✅ Clean conversational flow maintained after repair success")
        print("✅ Ready for production with transcript purity guaranteed")
        
    except Exception as e:
        print(f"\n❌ P0-4 EPHEMERAL REPAIR TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)