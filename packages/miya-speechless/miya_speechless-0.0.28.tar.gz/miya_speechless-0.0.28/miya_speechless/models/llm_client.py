"""OpenAI API client for the Scout app."""

from dataclasses import dataclass
from litellm import completion
from typing import List, Dict, Any
from tenacity import retry, wait_exponential, stop_after_attempt

TIMEOUT_SECONDS = 30


class LLMError(Exception):
    """Raised when an LLM request ultimately fails."""

    def __init__(
        self,
        provider: str,
        model: str,
        message: str,
        *,
        status: int = None,
        original: Exception = None,
    ):
        """
        Initialize the LLMError with the specified provider, model, and message.

        Args:
            provider (str): The provider of the LLM.
            model (str): The model of the LLM.
            message (str): The message to display.
            status (int | None): The status code of the error.
            original (Exception | None): The original exception.
        """
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.status = status
        self.original = original

    def __str__(self) -> str:
        """This is used to display the error in the logs"""
        core = f"[{self.provider}:{self.model}] {self.args[0]}"
        return f"{core} (status={self.status})" if self.status else core


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for the LLMClient."""

    provider: str
    api_key: str
    model: str = "gpt-4o"
    temperature: float = 0.1


class LLMClient:
    """Tiny wrapper around LiteLLM `completion()` with retries & defaults."""

    def __init__(self, cfg: LLMConfig) -> None:
        """
        Initialize the LLMClient with the specified configuration.

        Args:
            cfg (LLMConfig): The configuration for the LLMClient.
        """
        self.cfg = cfg

    @retry(
        wait=wait_exponential(multiplier=1, max=10),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def ask(
        self,
        messages: List[Dict[str, str]],
        *,
        model: str = None,  # noqa: DAR401
        temperature: float = None,
        **kwargs: Any,
    ) -> str:
        """
        Send a chat completion request and return the assistant’s text.

        Args:
            messages (List[Dict[str, str]]): The messages to send to the LLM.
            model (str | None): The model to use for completion.
            temperature (float | None): The sampling temperature.
            **kwargs: Additional keyword arguments to pass to the LiteLLM completion function.

        Returns:
            str: The response from the LLM.

        Raises:
            LLMError: If the LLM request fails.
        """
        model_name = model or self.cfg.model
        temp = temperature if temperature is not None else self.cfg.temperature

        provider_name = self.cfg.provider
        full_model_name = f"{provider_name}/{model_name}"
        try:
            resp = completion(
                model=full_model_name,
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
