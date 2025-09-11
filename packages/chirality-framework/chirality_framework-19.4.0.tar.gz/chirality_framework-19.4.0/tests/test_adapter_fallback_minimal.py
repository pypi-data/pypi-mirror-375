import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from chirality.infrastructure.llm.openai_adapter import call_responses, get_client
from chirality.infrastructure.llm import openai_adapter as oa


class DummyUsage:
    input_tokens = 10
    output_tokens = 5
    total_tokens = 15


def _mk_sdk_ok_response():
    return SimpleNamespace(output_text='{"ok": true}', usage=DummyUsage(), model="gpt-5")


def test_sdk_accepts_rf_or_triggers_fallback_cleanly():
    """SDK accepts response_format or triggers fallback on TypeError."""
    os.environ.setdefault("OPENAI_API_KEY", "sk-test")
    oa._client = None

    # Case 1: SDK accepts response_format
    with patch("chirality.infrastructure.llm.openai_adapter.OpenAI") as MockOpenAI:
        inst = MockOpenAI.return_value
        inst.responses.create.return_value = _mk_sdk_ok_response()

        res = call_responses(
            instructions="sys",
            input="user",
            text={"format": "json_object"},
            expects_json=True,
            store=False,
        )
        assert res["output_text"], "SDK path should return non-empty output"
        assert inst.responses.create.called, "SDK create should be called"

    # Case 2: SDK rejects response_format -> fallback triggers
    with patch("chirality.infrastructure.llm.openai_adapter.OpenAI") as MockOpenAI:
        inst = MockOpenAI.return_value
        inst.responses.create.side_effect = TypeError(
            "Responses.create() got an unexpected keyword argument 'response_format'"
        )

        # Spy on raw fallback to confirm it runs
        fallback_calls = []

        def fake_raw(api_params):
            fallback_calls.append(api_params)
            return SimpleNamespace(output_text='{"ok": true}', usage=None, model="gpt-5")

        oa._client = None
        client = get_client()
        with patch.object(client, "_call_responses_raw", side_effect=fake_raw):
            res = call_responses(
                instructions="sys",
                input="user",
                text={"format": "json_object"},
                expects_json=True,
                store=False,
            )

            assert res["output_text"], "Fallback path should return non-empty output"
            assert fallback_calls, "Raw fallback should be invoked when SDK rejects response_format"


def test_fallback_returns_json_for_trivial_schema():
    """Fallback path parses output_text from raw JSON envelope (no real network)."""
    os.environ.setdefault("OPENAI_API_KEY", "sk-test")
    oa._client = None
    client = get_client()

    # Install a fake httpx in sys.modules so the raw path uses it
    class _FakeResp:
        status_code = 200

        def json(self):
            return {"output_text": json.dumps({"ok": True})}

    class _FakeClient:
        def __init__(self, timeout=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, headers=None, json=None):
            return _FakeResp()

    class _FakeHTTPX:
        class Timeout:
            def __init__(self, connect=10.0, read=60.0, write=10.0, pool=10.0):
                pass

        Client = _FakeClient

    sys.modules["httpx"] = _FakeHTTPX

    api_params = {
        "model": "gpt-5",
        "instructions": "sys",
        "input": [{"role": "user", "content": [{"type": "input_text", "text": "user"}]}],
        "response_format": {"type": "json_object"},
    }

    resp = client._call_responses_raw(api_params)
    assert hasattr(resp, "output_text") and resp.output_text
    parsed = json.loads(resp.output_text)
    assert parsed == {"ok": True}
