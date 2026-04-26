"""Retrieval pipeline: embed query → vector search → optional rerank."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from yueshang_copilot.core.schema import Citation
from yueshang_copilot.rag.embeddings import embed_texts
from yueshang_copilot.rag.store import StoredDoc, VectorStore


@dataclass
class RetrievedChunk:
    text: str
    source: str
    score: float
    metadata: dict


class Retriever:
    def __init__(self, collection: str = "demo", top_k: int = 8, rerank: bool = False):
        self._store = VectorStore(collection=collection)
        self._top_k = top_k
        self._rerank = rerank
        self._reranker = None
        if rerank:
            from sentence_transformers import CrossEncoder
            from yueshang_copilot.core.config import get_settings
            self._reranker = CrossEncoder(get_settings().rerank_model)

    def retrieve(self, query: str, where: Optional[dict] = None) -> list[RetrievedChunk]:
        q_embed = embed_texts([query])[0]
        hits = self._store.query(q_embed, top_k=self._top_k, where=where)
        chunks = [
            RetrievedChunk(
                text=h.text,
                source=h.metadata.get("source", h.id),
                score=1.0,                              # placeholder; real score later
                metadata=h.metadata,
            )
            for h in hits
        ]
        if self._rerank and self._reranker and chunks:
            pairs = [(query, c.text) for c in chunks]
            scores = self._reranker.predict(pairs)
            for c, s in zip(chunks, scores):
                c.score = float(s)
            chunks.sort(key=lambda c: c.score, reverse=True)
        return chunks

    def to_citations(self, chunks: list[RetrievedChunk], max_n: int = 5) -> list[Citation]:
        out: list[Citation] = []
        for c in chunks[:max_n]:
            snippet = c.text[:200].replace("\n", " ")
            out.append(Citation(source=c.source, score=c.score, snippet=snippet))
        return out
