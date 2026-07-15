from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from app.core.settings import AppSettings


@dataclass(slots=True)
class OllamaClient:
    settings: AppSettings

    def _base_url(self) -> str:
        return self.settings.ai_ollama_base_url.rstrip("/")

    async def health(self) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=self.settings.ai_ollama_timeout_seconds) as client:
            response = await client.get(f"{self._base_url()}/api/tags")
            response.raise_for_status()
            return response.json()

    async def list_models(self) -> list[dict[str, object]]:
        payload = await self.health()
        models = payload.get("models", []) if isinstance(payload, dict) else []
        return [model for model in models if isinstance(model, dict)]

    async def pull_model(self, model_name: str) -> dict[str, object]:
        async with httpx.AsyncClient(timeout=self.settings.ai_ollama_timeout_seconds) as client:
            response = await client.post(
                f"{self._base_url()}/api/pull",
                json={"name": model_name, "stream": False},
            )
            response.raise_for_status()
            return response.json()

    async def chat(self, *, model: str, messages: list[dict[str, str]], options: dict[str, object] | None = None) -> dict[str, object]:
        payload: dict[str, object] = {"model": model, "messages": messages, "stream": False}
        if options:
            payload["options"] = options
        async with httpx.AsyncClient(timeout=self.settings.ai_ollama_timeout_seconds) as client:
            response = await client.post(f"{self._base_url()}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()

    async def generate(self, *, model: str, prompt: str, options: dict[str, object] | None = None) -> dict[str, object]:
        payload: dict[str, object] = {"model": model, "prompt": prompt, "stream": False}
        if options:
            payload["options"] = options
        async with httpx.AsyncClient(timeout=self.settings.ai_ollama_timeout_seconds) as client:
            response = await client.post(f"{self._base_url()}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()

    async def stream_chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        options: dict[str, object] | None = None,
    ) -> AsyncIterator[str]:
        payload: dict[str, object] = {"model": model, "messages": messages, "stream": True}
        if options:
            payload["options"] = options
        async with httpx.AsyncClient(timeout=self.settings.ai_ollama_timeout_seconds) as client:
            async with client.stream("POST", f"{self._base_url()}/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        parsed = json.loads(line)
                    except json.JSONDecodeError:
                        yield line
                        continue
                    yield json.dumps(parsed)
