from unittest.mock import patch
import os
from chirality.infrastructure.llm.openai_adapter import call_responses, get_client
from chirality.infrastructure.llm import openai_adapter as oa
import pytest


def test_probe_fails_fast_on_unsupported_text_param():
    def raise_typeerror(**kwargs):
        raise TypeError("unexpected keyword argument 'response_format'")

    with patch("chirality.infrastructure.llm.openai_adapter.OpenAI") as MockOpenAI:
        inst = MockOpenAI.return_value
        inst.responses.create.side_effect = raise_typeerror

        os.environ.setdefault("OPENAI_API_KEY", "sk-test")
        oa._client = None
        client = get_client()
        # Reset probe to force it to run
        client._rf_probed = False

        with pytest.raises(RuntimeError) as ei:
            call_responses(instructions="sys", input="user", expects_json=True)
        assert "does not support response_format" in str(ei.value)
import pytest
pytest.skip("Probe removed; SDK pin required in environment.", allow_module_level=True)
