"""Settings loaded from environment / .env."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Literal["anthropic", "qwen", "deepseek", "local"] = "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    dashscope_api_key: str = ""
    qwen_model: str = "qwen2.5-72b-instruct"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"

    embed_model: str = "BAAI/bge-m3"
    rerank_model: str = "BAAI/bge-reranker-v2-m3"

    chroma_persist_dir: str = "./.chroma"
    default_collection: str = "demo"

    default_lang: str = "zh"
    supported_langs: str = "zh,en,es,pt,ar,ja,de,fr"

    @property
    def supported_langs_list(self) -> list[str]:
        return [s.strip() for s in self.supported_langs.split(",") if s.strip()]


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
