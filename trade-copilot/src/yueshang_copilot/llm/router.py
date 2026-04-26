"""LLM provider router. Switch backends via config without changing call sites."""
from __future__ import annotations

import logging
from typing import Optional

from yueshang_copilot.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin facade over Anthropic / DashScope (Qwen) / DeepSeek / local."""

    def __init__(self):
        self._cfg = get_settings()
        self._provider = self._cfg.llm_provider

    def chat(
        self,
        system: str,
        user: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> str:
        """Synchronous chat completion. Returns assistant text."""
        if self._provider == "anthropic":
            return self._chat_anthropic(system, user, max_tokens, temperature, json_mode)
        if self._provider == "qwen":
            return self._chat_qwen(system, user, max_tokens, temperature, json_mode)
        if self._provider == "deepseek":
            return self._chat_deepseek(system, user, max_tokens, temperature, json_mode)
        if self._provider == "local":
            return self._chat_local(system, user, max_tokens, temperature)
        raise ValueError(f"Unknown LLM provider: {self._provider}")

    def _chat_anthropic(self, system, user, max_tokens, temperature, json_mode) -> str:
        from anthropic import Anthropic
        client = Anthropic(api_key=self._cfg.anthropic_api_key)
        if json_mode:
            user = user + "\n\nRespond ONLY with valid JSON. No prose."
        msg = client.messages.create(
            model=self._cfg.anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in msg.content if hasattr(b, "text"))

    def _chat_qwen(self, system, user, max_tokens, temperature, json_mode) -> str:
        from openai import OpenAI
        client = OpenAI(
            api_key=self._cfg.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        rsp = client.chat.completions.create(
            model=self._cfg.qwen_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=max_tokens, temperature=temperature, **kwargs,
        )
        return rsp.choices[0].message.content or ""

    def _chat_deepseek(self, system, user, max_tokens, temperature, json_mode) -> str:
        from openai import OpenAI
        client = OpenAI(
            api_key=self._cfg.deepseek_api_key,
            base_url="https://api.deepseek.com",
        )
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        rsp = client.chat.completions.create(
            model=self._cfg.deepseek_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=max_tokens, temperature=temperature, **kwargs,
        )
        return rsp.choices[0].message.content or ""

    def _chat_local(self, system, user, max_tokens, temperature) -> str:
        from openai import OpenAI
        client = OpenAI(api_key="local", base_url="http://localhost:11434/v1")
        rsp = client.chat.completions.create(
            model="qwen2.5",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=max_tokens, temperature=temperature,
        )
        return rsp.choices[0].message.content or ""


_client: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
