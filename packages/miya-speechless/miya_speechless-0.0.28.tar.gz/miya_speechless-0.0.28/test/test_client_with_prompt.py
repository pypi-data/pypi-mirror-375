import pytest
from typing import Dict, List
import os

from miya_speechless.models.llm_client import LLMClient, LLMConfig, LLMError
from miya_speechless.nlp.sentiment_analysis import classify_sentiment
from miya_speechless.nlp.loader import render_messages


class MockLLMClient(LLMClient):
    def __init__(self, cfg: LLMConfig, mock_completion):
        super().__init__(cfg)
        self._mock_completion = mock_completion

    def _call_completion(self, *args, **kwargs):
        return self._mock_completion(*args, **kwargs)

    def ask(
        self,
        messages: List[dict],
        *,
        model: str = None,
        temperature: float = None,
        **kwargs,
    ) -> str:
        model_name = model or self.cfg.model
        temp = temperature if temperature is not None else self.cfg.temperature
        try:
            resp = self._call_completion(
                model=f"{self.cfg.provider}/{model_name}",
                messages=messages,
                temperature=temp,
                api_key=self.cfg.api_key,
                **kwargs,
            )
            return resp["choices"][0]["message"]["content"]
        except Exception as exc:
            raise LLMError(
                provider=self.cfg.provider,
                model=model_name,
                message="LLM request failed",
                original=exc,
            )


@pytest.fixture(scope="session")
def cfg() -> LLMConfig:
    return LLMConfig(provider="openai", api_key="test-key", model="gpt-4o")


def _fake_completion_success(*_, **__) -> Dict[str, List[Dict[str, Dict[str, str]]]]:
    return {"choices": [{"message": {"content": "Hello, user!"}}]}


def _fake_completion_error(*_, **__):
    raise RuntimeError("provider blew up")


def test_ask_success(cfg: LLMConfig):
    client = MockLLMClient(cfg, mock_completion=_fake_completion_success)
    result = client.ask(messages=[{"role": "user", "content": "Ping"}])
    assert result == "Hello, user!"


def test_ask_failure_raises_llmerror(cfg: LLMConfig):
    client = MockLLMClient(cfg, mock_completion=_fake_completion_error)

    with pytest.raises(LLMError) as exc:
        client.ask(messages=[{"role": "user", "content": "Ping"}])

    err = exc.value
    assert err.provider == "openai"
    assert err.model == "gpt-4o"
    assert "LLM request failed" in str(err)


@pytest.mark.parametrize("template_name", ["tags", "summarize", "sentiment_score"])
def test_render_template_injects_text(template_name):
    convo = "Hello, this is a dummy conversation."
    messages = render_messages(template_name, transcribed_and_diarized=convo)

    full_content = "\n".join(m["content"] for m in messages)
    assert convo in full_content, f"{template_name}.j2 did not inject the variable"


def test_render_template_keeps_json_format():
    messages = render_messages("summarize", transcribed_and_diarized="dummy")

    full_content = "\n".join(msg["content"] for msg in messages)

    for key in (
        '"reason":',
        '"description":',
        '"products":',
        '"satisfaction":',
        '"fup":',
        '"tone_of_voice":',
        '"tags":',
    ):
        assert key in full_content, f"Missing expected key: {key}"


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY to be set in environment",
)
def test_ask_with_openai_live():
    """Test the real OpenAI client with a real prompt (integration)."""
    cfg = LLMConfig(
        provider="openai",
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o",
        temperature=0.1,
    )

    client = LLMClient(cfg)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]

    response = client.ask(messages)
    assert isinstance(response, str)
    assert "paris" in response.lower()


@pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="No API key in env")
@pytest.mark.parametrize(
    "convo,expected",
    [
        (
            "I'm so happy with the support I received! Everything went smoothly.",
            "Positive",
        ),
        (
            "This was the worst experience I've ever had. Nothing worked.",
            "Negative",
        ),
        (
            "It was okay, not great, not terrible. Just fine.",
            "Neutral",
        ),
    ],
)
def test_sentiment_classification_with_live_openai(convo: str, expected: str):
    """Test full prompt + response + classification using real OpenAI API."""
    cfg = LLMConfig(
        provider="openai",
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o",
        temperature=0.0,
    )
    client = LLMClient(cfg)

    messages = render_messages("sentiment_score", transcribed_and_diarized=convo)

    raw_score = client.ask(messages)

    try:
        score = float(raw_score.strip())
    except ValueError:
        pytest.fail(f"Expected numeric sentiment score, got: {raw_score}")

    classification = classify_sentiment(score)

    assert (
        classification == expected
    ), f"Expected {expected}, got {classification} (score: {score})"
