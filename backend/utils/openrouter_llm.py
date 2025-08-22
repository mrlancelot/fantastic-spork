"""
Custom OpenRouter LLM wrapper for LlamaIndex.
Bypasses model validation while maintaining function calling and structured output support.
"""

import os
import httpx
import json
from typing import Any, Dict, List, Optional, Sequence, Type
from pydantic import BaseModel
from llama_index.llms.openai import OpenAI
from llama_index.core.base.llms.types import ChatMessage, ChatResponse
from llama_index.core.prompts.base import PromptTemplate
import openai


class OpenRouterLLM(OpenAI):
    """Custom OpenRouter LLM that bypasses model validation."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        default_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """Initialize OpenRouter LLM with custom configuration."""
        # Set up default headers for OpenRouter
        headers = {
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "TravelAI Backend"
        }
        if default_headers:
            headers.update(default_headers)
        
        # Initialize with a dummy OpenAI model to bypass validation
        # We'll override the model in the actual API calls
        super().__init__(
            model="gpt-3.5-turbo",  # Dummy model for validation
            api_key=api_key,
            api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            timeout=timeout,
            default_headers=headers,
            **kwargs
        )
        
        # Store the actual model name after parent init
        self._actual_model = model
        
        # Override the OpenAI client to use our model
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers=headers,
            timeout=timeout,
            max_retries=max_retries
        )
        
        self._async_client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers=headers,
            timeout=timeout,
            max_retries=max_retries
        )
    
    @property
    def model(self) -> str:
        """Return the actual model name."""
        return self._actual_model if hasattr(self, '_actual_model') else self._model
    
    def _get_model_kwargs(self, **kwargs: Any) -> Dict[str, Any]:
        """Override to use the actual model name."""
        model_kwargs = super()._get_model_kwargs(**kwargs)
        if hasattr(self, '_actual_model'):
            model_kwargs["model"] = self._actual_model
        return model_kwargs
    
    def structured_predict(
        self,
        output_cls: Type[BaseModel],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any
    ) -> BaseModel:
        """Generate a structured output based on the prompt and output class."""
        # Get the JSON schema from the Pydantic model
        schema = output_cls.model_json_schema()
        
        # Format the prompt with provided arguments
        formatted_prompt = prompt.format(**prompt_args)
        
        # Add JSON schema instructions to the prompt
        structured_prompt = f"""{formatted_prompt}

You MUST respond with valid JSON that exactly matches this schema:
{json.dumps(schema, indent=2)}

Remember to:
1. Include all required fields
2. Use the exact field names specified
3. Follow the correct data types
4. Return ONLY the JSON object, no additional text or markdown formatting"""

        # Create messages for the chat completion
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant that always returns valid JSON responses matching the provided schema."),
            ChatMessage(role="user", content=structured_prompt)
        ]
        
        # Get the response from the LLM
        response = self.chat(messages, **(llm_kwargs or {}))
        
        # Parse the response content
        try:
            # Extract JSON from the response
            response_text = response.message.content
            
            # Try to find JSON in the response (in case it's wrapped in markdown or other text)
            if "```json" in response_text:
                # Extract JSON from markdown code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract from generic code block
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            # Parse JSON and create Pydantic model instance
            json_data = json.loads(response_text.strip())
            return output_cls(**json_data)
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON object
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            if matches:
                for match in matches:
                    try:
                        json_data = json.loads(match)
                        return output_cls(**json_data)
                    except:
                        continue
            
            # If all parsing attempts fail, raise an error
            raise ValueError(f"Failed to parse structured output: {e}\nResponse: {response_text}")
        except Exception as e:
            raise ValueError(f"Failed to create structured output: {e}")
    
    async def astructured_predict(
        self,
        output_cls: Type[BaseModel],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any
    ) -> BaseModel:
        """Async version of structured_predict."""
        # Get the JSON schema from the Pydantic model
        schema = output_cls.model_json_schema()
        
        # Format the prompt with provided arguments
        formatted_prompt = prompt.format(**prompt_args)
        
        # Add JSON schema instructions to the prompt
        structured_prompt = f"""{formatted_prompt}

You MUST respond with valid JSON that exactly matches this schema:
{json.dumps(schema, indent=2)}

Remember to:
1. Include all required fields
2. Use the exact field names specified
3. Follow the correct data types
4. Return ONLY the JSON object, no additional text or markdown formatting"""

        # Create messages for the chat completion
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant that always returns valid JSON responses matching the provided schema."),
            ChatMessage(role="user", content=structured_prompt)
        ]
        
        # Get the response from the LLM
        response = await self.achat(messages, **(llm_kwargs or {}))
        
        # Parse the response content
        try:
            # Extract JSON from the response
            response_text = response.message.content
            
            # Try to find JSON in the response (in case it's wrapped in markdown or other text)
            if "```json" in response_text:
                # Extract JSON from markdown code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract from generic code block
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            # Parse JSON and create Pydantic model instance
            json_data = json.loads(response_text.strip())
            return output_cls(**json_data)
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON object
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            if matches:
                for match in matches:
                    try:
                        json_data = json.loads(match)
                        return output_cls(**json_data)
                    except:
                        continue
            
            # If all parsing attempts fail, raise an error
            raise ValueError(f"Failed to parse structured output: {e}\nResponse: {response_text}")
        except Exception as e:
            raise ValueError(f"Failed to create structured output: {e}")