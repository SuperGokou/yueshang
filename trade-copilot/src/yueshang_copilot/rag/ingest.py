"""Ingest documents into the vector store. CLI: python -m yueshang_copilot.rag.ingest <path>."""
from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path
from typing import Iterator

import click
from rich.console import Console
from rich.progress import track

from yueshang_copilot.rag.embeddings import embed_texts
from yueshang_copilot.rag.store import VectorStore

logger = logging.getLogger(__name__)
console = Console()


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def _read_file(path: Path) -> str:
    suf = path.suffix.lower()
    if suf in {".md", ".txt", ".csv", ".html", ".htm"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suf == ".pdf":
        from pypdf import PdfReader
        text_parts = []
        for page in PdfReader(str(path)).pages:
            text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    if suf == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(str(path)).paragraphs)
    raise ValueError(f"Unsupported format: {suf}")


def _chunk(text: str, target_chars: int = 900, overlap: int = 120) -> Iterator[str]:
    """Naive paragraph-aware chunker. Good enough for MVP."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    buf = ""
    for p in paragraphs:
        if len(buf) + len(p) + 1 > target_chars and buf:
            yield buf
            buf = buf[-overlap:] + "\n" + p
        else:
            buf = (buf + "\n" + p) if buf else p
    if buf:
        yield buf


def ingest_path(path: Path, collection: str = "demo", lang: str | None = None) -> int:
    store = VectorStore(collection=collection)
    files: list[Path] = []
    if path.is_file():
        files = [path]
    else:
        files = [p for p in path.rglob("*")
                 if p.is_file() and p.suffix.lower() in {".md", ".txt", ".pdf", ".docx", ".html", ".csv"}]
    if not files:
        console.print("[yellow]No supported files found.[/yellow]")
        return 0

    total_chunks = 0
    for f in track(files, description="Ingesting..."):
        try:
            text = _read_file(f)
        except Exception as e:
            console.print(f"[red]Skip {f.name}: {e}[/red]")
            continue
        chunks = list(_chunk(text))
        if not chunks:
            continue
        embeddings = embed_texts(chunks)
        ids = [f"{f.stem}-{i}-{_sha1(c)}" for i, c in enumerate(chunks)]
        metadatas = [
            {"source": str(f), "filename": f.name, "chunk": i, "lang": lang or "auto"}
            for i in range(len(chunks))
        ]
        store.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
        total_chunks += len(chunks)
    console.print(f"[green]Done. {total_chunks} chunks across {len(files)} files. Total in collection: {store.count()}[/green]")
    return total_chunks


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--collection", default="demo")
@click.option("--lang", default=None, help="Optional explicit language tag (zh/en/...)")
def main(path: Path, collection: str, lang: str | None):
    """Ingest a file or directory into the RAG vector store."""
    ingest_path(path, collection=collection, lang=lang)


if __name__ == "__main__":
    main()
