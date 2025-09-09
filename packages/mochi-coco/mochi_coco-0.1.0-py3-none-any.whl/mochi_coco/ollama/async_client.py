from typing import AsyncIterator, List, Optional, Sequence, Mapping, Any
from dataclasses import dataclass

from ollama import AsyncClient, ListResponse, ChatResponse, Message, ShowResponse

@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ModelInfo:
    name: str | None
    size_mb: float
    format: Optional[str] = None
    family: Optional[str] = None
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None
    # supported_context_size = Optional[int] = None

class AsyncOllamaClient:
    def __init__(self, host: Optional[str] = None):
        self.client = AsyncClient(host=host) if host else AsyncClient()

    async def list_models(self) -> List[ModelInfo]:
        """List all available models asynchronously."""
        try:
            # Note: ollama_list() is still synchronous, so we'll use the client's list method
            response: ListResponse = await self.client.list()
            models = []

            for model in response.models:
                size_mb = model.size / 1024 / 1024 if model.size else 0

                model_info = ModelInfo(
                    name=model.model,
                    size_mb=size_mb,
                    format=model.details.format if model.details else None,
                    family=model.details.family if model.details else None,
                    parameter_size=model.details.parameter_size if model.details else None,
                    quantization_level=model.details.quantization_level if model.details else None,
                )
                models.append(model_info)

            return models
        except Exception as e:
            raise Exception(f"Failed to list models: {e}")

    async def show_model_details(self, model_name: str) -> ShowResponse:
        """Get model details with method 'show' asynchronously."""
        try:
            model_details = await self.client.show(
                model=model_name
            )
            return model_details
        except Exception as e:
            raise Exception(f"Failed to show model details: {e}")

    async def chat_stream(self, model: str, messages: Sequence[Mapping[str, Any] | Message]) -> AsyncIterator[ChatResponse]:
        """
        Stream chat responses from the model asynchronously.
        """
        try:
            response_stream = await self.client.chat(
                model=model,
                messages=messages,
                stream=True
            )

            async for chunk in response_stream:
                if chunk.message and chunk.message.content:
                    yield chunk
                elif hasattr(chunk, 'done') and chunk.done and hasattr(chunk, 'eval_count'):
                    yield chunk
        except Exception as e:
            raise Exception(f"Chat failed: {e}")

    async def chat_single(self, model: str, messages: Sequence[Mapping[str, Any] | Message]) -> ChatResponse:
        """
        Get a single (non-streaming) chat response from the model asynchronously.
        """
        try:
            response = await self.client.chat(
                model=model,
                messages=messages,
                stream=False
            )
            return response
        except Exception as e:
            raise Exception(f"Chat failed: {e}")
