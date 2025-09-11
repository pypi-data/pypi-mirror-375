import pytest
from chirality.infrastructure.llm.openai_adapter import call_responses


def test_guard_rejects_model_in_kwargs():
    with pytest.raises(ValueError) as ei:
        call_responses(instructions="sys", input="user", model="gpt-5")
    assert "Unexpected parameters" in str(ei.value)


def test_guard_rejects_presence_penalty():
    with pytest.raises(ValueError) as ei:
        call_responses(instructions="sys", input="user", presence_penalty=0.5)
    assert "Unexpected parameters" in str(ei.value)

