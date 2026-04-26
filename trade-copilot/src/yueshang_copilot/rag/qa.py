"""Top-level RAG question-answering."""
from __future__ import annotations

import time

from yueshang_copilot.core.schema import RAGAnswer
from yueshang_copilot.llm.router import get_llm
from yueshang_copilot.rag.retriever import Retriever


_SYSTEM = """You are Yueshang Copilot, a helpful trade & manufacturing assistant.
Use the provided context excerpts to answer the user's question. If the context does not
contain the answer, say so honestly and provide your best general knowledge with a clear caveat.
Always answer in the same language the user asked in (zh/en/es/pt/ar/...).
When you use information from a source, mention the filename in [brackets].
"""


def answer(question: str, collection: str = "demo", lang: str = "zh", top_k: int = 6) -> RAGAnswer:
    started = time.perf_counter()
    retriever = Retriever(collection=collection, top_k=top_k)
    chunks = retriever.retrieve(question)

    context = "\n\n".join(
        f"[{c.metadata.get('filename', c.source)}]\n{c.text}" for c in chunks[:top_k]
    ) or "(no context retrieved)"

    user = f"Question: {question}\n\nContext:\n{context}"
    text = get_llm().chat(_SYSTEM, user, max_tokens=900, temperature=0.2)

    return RAGAnswer(
        answer=text.strip(),
        citations=retriever.to_citations(chunks),
        lang=lang,
        elapsed_seconds=time.perf_counter() - started,
    )
