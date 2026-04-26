"""Embedding model wrapper. Uses BGE-M3 by default (multi-lingual)."""
from __future__ import annotations

import threading
from functools import lru_cache

from yueshang_copilot.core.config import get_settings


class _EmbedSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cfg = get_settings()
                from sentence_transformers import SentenceTransformer
                cls._instance._model = SentenceTransformer(cfg.embed_model)
        return cls._instance

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()


@lru_cache(maxsize=1)
def get_embedder() -> _EmbedSingleton:
    return _EmbedSingleton()


def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_embedder().encode(texts)
