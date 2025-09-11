from unittest.mock import patch
import os
from chirality.infrastructure.llm.openai_adapter import call_responses, get_client
from chirality.infrastructure.llm import openai_adapter as oa


def test_adapter_maps_json_schema_to_text_param():
    collected = []

    def spy_create(**kwargs):
        collected.append(kwargs)
        class R:
            output_text = '{"ok": true}'
            usage = None
        return R()

    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "Result",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"ok": {"type": "boolean"}},
                "required": ["ok"],
                "additionalProperties": False,
            },
        },
    }

    with patch("chirality.infrastructure.llm.openai_adapter.OpenAI") as MockOpenAI:
        inst = MockOpenAI.return_value
        inst.responses.create.side_effect = spy_create
        os.environ.setdefault("OPENAI_API_KEY", "sk-test")
        oa._client = None
        client = get_client()
        client._rf_probed = True

        res = call_responses(
            instructions="sys", input="user", text={"format":"json_schema","schema":schema["json_schema"]}, expects_json=True
        )
        assert res["output_text"], "should return non-empty output"

    assert collected, "responses.create should be called"
    params = collected[-1]
    assert "text" in params and isinstance(params["text"], dict)
    rf = params["text"]
    assert rf.get("format") == "json_schema"
    assert "schema" in rf and isinstance(rf["schema"], dict)
