"""Vector store wrapper (ChromaDB persistent client)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from yueshang_copilot.core.config import get_settings


@dataclass
class StoredDoc:
    id: str
    text: str
    metadata: dict
    embedding: Optional[list[float]] = None


class VectorStore:
    """ChromaDB-backed store. Embeddings produced upstream."""

    def __init__(self, collection: Optional[str] = None):
        cfg = get_settings()
        import chromadb

        self._client = chromadb.PersistentClient(path=cfg.chroma_persist_dir)
        name = collection or cfg.default_collection
        self._coll = self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ):
        if not ids:
            return
        self._coll.upsert(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

    def query(
        self,
        embedding: list[float],
        top_k: int = 8,
        where: Optional[dict] = None,
    ) -> list[StoredDoc]:
        result = self._coll.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where,
        )
        out: list[StoredDoc] = []
        if not result.get("ids") or not result["ids"][0]:
            return out
        for i, doc_id in enumerate(result["ids"][0]):
            out.append(StoredDoc(
                id=doc_id,
                text=result["documents"][0][i],
                metadata=result["metadatas"][0][i] or {},
            ))
        return out

    def count(self) -> int:
        return self._coll.count()

    def reset(self):
        self._client.delete_collection(self._coll.name)
        self._coll = self._client.get_or_create_collection(name=self._coll.name)
