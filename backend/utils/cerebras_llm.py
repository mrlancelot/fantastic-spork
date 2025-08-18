"""
Custom LlamaIndex LLM wrapper for Cerebras Cloud SDK.
Implements the LlamaIndex LLM interface to make Cerebras compatible with LlamaIndex agents.
"""

import os
import logging
from typing import Any, Dict, Optional, Sequence, AsyncGenerator, Generator
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseGen,
    ChatResponseAsyncGen,
    CompletionResponse,
    CompletionResponseGen,
    CompletionResponseAsyncGen,
    LLMMetadata,
    MessageRole,
)
from llama_index.core.llms.custom import CustomLLM
from llama_index.core.callbacks import CallbackManager
from cerebras.cloud.sdk import Cerebras
import asyncio

logger = logging.getLogger(__name__)

class CerebrasLLM(CustomLLM):
    """
    Custom LlamaIndex LLM wrapper for Cerebras Cloud SDK.
    This wrapper makes the Cerebras SDK compatible with LlamaIndex's LLM interface,
    allowing it to be used with LlamaIndex agents and workflows.
    """
    model_name: str = "llama-4-scout-17b-16e-instruct"
    temperature: float = 0.1
    max_tokens: Optional[int] = 4096
    api_key: Optional[str] = None
    def __init__(
        self,
        model_name: str = "llama-4-scout-17b-16e-instruct",
        temperature: float = 0.1,
        max_tokens: Optional[int] = 4096,
        api_key: Optional[str] = None,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Cerebras LLM wrapper.
        Args:
            model_name: The Cerebras model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            api_key: Cerebras API key (if not provided, uses CEREBRAS_API_KEY env var)
            callback_manager: LlamaIndex callback manager
            **kwargs: Additional arguments
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable is required")

        self._client = Cerebras(api_key=self.api_key)
        super().__init__(
            callback_manager=callback_manager,
            **kwargs,
        )
    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "CerebrasLLM"
    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=8192,
            num_output=self.max_tokens or 4096,
            is_chat_model=True,
            model_name=self.model_name,
        )
    def _messages_to_cerebras_format(self, messages: Sequence[ChatMessage]) -> list:
        """Convert LlamaIndex ChatMessage format to Cerebras format."""
        cerebras_messages = []
        for message in messages:
            role = message.role.value if hasattr(message.role, 'value') else str(message.role)

            if role == MessageRole.SYSTEM.value:
                cerebras_role = "system"
            elif role == MessageRole.USER.value:
                cerebras_role = "user"
            elif role == MessageRole.ASSISTANT.value:
                cerebras_role = "assistant"
            else:
                cerebras_role = "user"
            cerebras_messages.append({
                "role": cerebras_role,
                "content": message.content
            })
        return cerebras_messages
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        """Complete a prompt using Cerebras."""
        try:

            messages = [{"role": "user", "content": prompt}]
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )

            content = response.choices[0].message.content
            return CompletionResponse(
                text=content,
                raw=response,
            )
        except Exception as e:
            logger.error(f"Cerebras completion error: {e}")
            raise
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        """Stream complete a prompt using Cerebras."""
        try:
            messages = [{"role": "user", "content": prompt}]
            stream = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
                **kwargs
            )
            def gen() -> Generator[CompletionResponse, None, None]:
                content = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        delta = chunk.choices[0].delta.content
                        content += delta
                        yield CompletionResponse(
                            text=content,
                            delta=delta,
                            raw=chunk,
                        )
            return gen()
        except Exception as e:
            logger.error(f"Cerebras stream completion error: {e}")
            raise
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        """Chat with Cerebras using message history."""
        try:
            cerebras_messages = self._messages_to_cerebras_format(messages)
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=cerebras_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )

            content = response.choices[0].message.content
            return ChatResponse(
                message=ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=content,
                ),
                raw=response,
            )
        except Exception as e:
            logger.error(f"Cerebras chat error: {e}")
            raise
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        """Stream chat with Cerebras using message history."""
        try:
            cerebras_messages = self._messages_to_cerebras_format(messages)
            stream = self._client.chat.completions.create(
                model=self.model_name,
                messages=cerebras_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
                **kwargs
            )
            def gen() -> Generator[ChatResponse, None, None]:
                content = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        delta = chunk.choices[0].delta.content
                        content += delta
                        yield ChatResponse(
                            message=ChatMessage(
                                role=MessageRole.ASSISTANT,
                                content=content,
                            ),
                            delta=delta,
                            raw=chunk,
                        )
            return gen()
        except Exception as e:
            logger.error(f"Cerebras stream chat error: {e}")
            raise
    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        """Async complete a prompt using Cerebras."""

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.complete, prompt, formatted, **kwargs)
    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        """Async stream complete a prompt using Cerebras."""

        sync_gen = self.stream_complete(prompt, formatted, **kwargs)
        async def async_gen() -> AsyncGenerator[CompletionResponse, None]:
            loop = asyncio.get_event_loop()
            for item in sync_gen:
                yield await loop.run_in_executor(None, lambda: item)
        return async_gen()
    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Async chat with Cerebras using message history."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.chat, messages, **kwargs)
    async def astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        """Async stream chat with Cerebras using message history."""

        sync_gen = self.stream_chat(messages, **kwargs)
        async def async_gen() -> AsyncGenerator[ChatResponse, None]:
            loop = asyncio.get_event_loop()
            for item in sync_gen:
                yield await loop.run_in_executor(None, lambda: item)
        return async_gen()


def create_cerebras_llm(
    model_name: str = "llama3.1-70b",
    temperature: float = 0.1,
    max_tokens: Optional[int] = 4096,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> CerebrasLLM:
    """Create a Cerebras LLM instance with the specified configuration.
    Args:
        model_name: The Cerebras model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        api_key: Cerebras API key (if not provided, uses CEREBRAS_API_KEY env var)
        **kwargs: Additional arguments
    Returns:
        Configured CerebrasLLM instance
    """
    return CerebrasLLM(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
        **kwargs,
    )
