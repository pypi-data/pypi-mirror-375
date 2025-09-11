# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Azure OpenAI service implementation for the Pipecat AI framework."""

from typing import Any, Dict, List, Optional

from loguru import logger
from openai import AsyncAzureOpenAI
from openai._streaming import AsyncStream
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam

from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.openai.llm import OpenAILLMService


class AzureLLMService(OpenAILLMService):
    """A service for interacting with Azure OpenAI using the OpenAI-compatible interface.

    This service extends OpenAILLMService to connect to Azure's OpenAI endpoint while
    maintaining full compatibility with OpenAI's interface and functionality.


    Args:
        api_key: The API key for accessing Azure OpenAI.
        endpoint: The Azure endpoint URL.
        model: The model identifier to use.
        api_version: Azure API version. Defaults to "2024-09-01-preview".
        reasoning_effort: If provided for reasoning models, sets the effort (e.g. "minimal").
        **kwargs: Additional keyword arguments passed to OpenAILLMService.

    """

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: str,
        model: str,
        api_version: str = "2024-09-01-preview",
        reasoning_effort: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the Azure LLM service.

        Args:
            api_key: The API key for accessing Azure OpenAI.
            endpoint: The Azure endpoint URL.
            model: The model identifier to use.
            api_version: Azure API version. Defaults to "2024-09-01-preview".
            **kwargs: Additional keyword arguments passed to OpenAILLMService.
        """
        # Initialize variables before calling parent __init__() because that
        # will call create_client() and we need those values there.
        self._endpoint = endpoint
        self._api_version = api_version
        self._reasoning_effort = reasoning_effort
        super().__init__(api_key=api_key, model=model, **kwargs)

    def create_client(self, api_key=None, base_url=None, **kwargs):
        """Create OpenAI-compatible client for Azure OpenAI endpoint.

        Args:
            api_key: API key for authentication. Uses instance key if None.
            base_url: Base URL for the client. Ignored for Azure implementation.
            **kwargs: Additional keyword arguments. Ignored for Azure implementation.

        Returns:
            AsyncAzureOpenAI: Configured Azure OpenAI client instance.
        """
        logger.debug(f"Creating Azure OpenAI client with endpoint {self._endpoint}")
        azure_deployment = kwargs.pop("azure_deployment", None)
        return AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=self._endpoint,
            api_version=self._api_version,
            azure_deployment=azure_deployment,
        )

    def _is_reasoning_model(self) -> bool:
        """Check if the current model supports reasoning parameters.

        Based on search results:
        - GPT-5, GPT-5-mini, and GPT-5-nano are reasoning models
        - GPT-5-chat is a standard chat model that doesn't use reasoning by default

        Returns:
            True if model supports reasoning parameters.
        """
        model_name_lower = self.model_name.lower()

        # Reasoning-capable models
        reasoning_models = {"gpt-5-nano", "gpt-5", "gpt-5-mini"}
        return model_name_lower in reasoning_models

    async def get_chat_completions(
        self, context: OpenAILLMContext, messages: List[ChatCompletionMessageParam]
    ) -> AsyncStream[ChatCompletionChunk]:
        """Get streaming chat completions from Azure OpenAI API.

        Handles both reasoning and standard models according to Azure AI Foundry documentation.
        Reasoning models use automatic chain of thought and have parameter limitations.
        """
        params = {
            "model": self.model_name,
            "stream": True,
            "messages": messages,
            "tools": context.tools,
            "tool_choice": context.tool_choice,
            "stream_options": {"include_usage": True},
            "max_tokens": self._settings["max_tokens"],
            "max_completion_tokens": self._settings["max_completion_tokens"],
        }

        if self._is_reasoning_model():
            # Reasoning models generally do NOT support temperature, presence_penalty, top_p
            if self._reasoning_effort:
                params["reasoning_effort"] = self._reasoning_effort
            if self._settings.get("seed"):
                params["seed"] = self._settings["seed"]
        else:
            # Standard models support all parameters
            params.update(
                {
                    "frequency_penalty": self._settings["frequency_penalty"],
                    "presence_penalty": self._settings["presence_penalty"],
                    "seed": self._settings["seed"],
                    "temperature": self._settings["temperature"],
                    "top_p": self._settings["top_p"],
                }
            )

        # Add any extra parameters from settings
        extra_params = self._settings.get("extra", {})
        params.update(extra_params)

        chunks = await self._client.chat.completions.create(**params)
        return chunks