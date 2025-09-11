import builtins
from types import SimpleNamespace
from unittest.mock import patch

import os
from chirality.infrastructure.llm.openai_adapter import call_responses, get_client
from chirality.infrastructure.llm import openai_adapter as oa


class DummyUsage:
    input_tokens = 10
    output_tokens = 5
    total_tokens = 15
    input_token_details = SimpleNamespace(cached_tokens=0)


def _mk_response_with_output_text():
    return SimpleNamespace(
        model="gpt-5",
        output_text='{"ok": true}',
        usage=DummyUsage(),
    )


def _mk_response_with_objecty_output():
    inner = SimpleNamespace(text='{"ok": true}')
    content = [inner]
    first = SimpleNamespace(content=content)
    return SimpleNamespace(
        model="gpt-5",
        output=[first],
        usage=DummyUsage(),
    )


def _spy_create(collected_kwargs):
    def _create(**kwargs):
        collected_kwargs.append(kwargs)
        # Return a default; test can monkey-patch to another
        return _mk_response_with_output_text()

    return _create


def test_adapter_sends_text_config_and_extracts_output_text():
    collected = []
    with patch("chirality.infrastructure.llm.openai_adapter.OpenAI") as MockOpenAI:
        inst = MockOpenAI.return_value
        inst.responses.create.side_effect = _spy_create(collected)

        # Force probe to be treated as already done
        os.environ.setdefault("OPENAI_API_KEY", "sk-test")
        oa._client = None
        client = get_client()
        client._rf_probed = True

        res = call_responses(instructions="sys", input="user", expects_json=True)
        assert res["output_text"], "adapter should return non-empty output_text"

    assert collected, "responses.create should be called"
    assert any(
        "text" in k and isinstance(k["text"], dict) and k["text"].get("format") == "json_object"
        for k in collected
    ), "text.format=json_object must be passed when expects_json=True"


def test_adapter_extracts_from_objecty_output():
    collected = []
    with patch("chirality.infrastructure.llm.openai_adapter.OpenAI") as MockOpenAI:
        inst = MockOpenAI.return_value
        inst.responses.create.side_effect = lambda **kwargs: _mk_response_with_objecty_output()

        os.environ.setdefault("OPENAI_API_KEY", "sk-test")
        oa._client = None
        client = get_client()
        client._rf_probed = True

        res = call_responses(instructions="sys", input="user", expects_json=True)
        assert res["output_text"], "should extract non-empty text from object-shaped output"
