"""HS Code agent: classify a product into harmonized tariff codes."""
from __future__ import annotations

import json
import logging
from typing import Any

from yueshang_copilot.core.schema import HSCodeMatch, HSCodeRequest, HSCodeResponse
from yueshang_copilot.llm.router import get_llm
from yueshang_copilot.rag.retriever import Retriever

logger = logging.getLogger(__name__)


_SYSTEM = """You are an expert customs classifier with deep knowledge of the Harmonized System.
Given a product description and target country, return the 3 most likely HS codes (6 to 10
digit, depending on the country's tariff schedule). Use the provided HS reference excerpts
when available, otherwise rely on your training. Always respond as strict JSON matching:

{
  "matches": [
    {"code": "string", "description": "string", "confidence": 0.0-1.0,
     "duty_rate": "string|null", "notes": "string|null"}
  ],
  "primary_language": "en|zh|...",
  "target_country": "..."
}
"""


def classify(request: HSCodeRequest, collection: str = "hscode") -> HSCodeResponse:
    name = request.product_name_en or request.product_name_zh or ""
    parts = [
        f"Product (EN): {request.product_name_en}" if request.product_name_en else "",
        f"Product (ZH): {request.product_name_zh}" if request.product_name_zh else "",
        f"Description: {request.description}" if request.description else "",
        f"Material: {request.material}" if request.material else "",
        f"Target country: {request.target_country}",
    ]
    user_lines = [p for p in parts if p]

    # Retrieve HS reference snippets if collection exists
    context = ""
    try:
        chunks = Retriever(collection=collection, top_k=6).retrieve(name)
        if chunks:
            context = "Reference excerpts:\n" + "\n---\n".join(c.text for c in chunks[:4])
    except Exception as e:
        logger.warning("HS reference retrieval skipped: %s", e)

    user = "\n".join(user_lines) + ("\n\n" + context if context else "")
    raw = get_llm().chat(_SYSTEM, user, max_tokens=800, temperature=0.0, json_mode=True)
    data: dict[str, Any] = _safe_json(raw)
    matches_raw = data.get("matches", [])
    matches = [HSCodeMatch(**m) for m in matches_raw if "code" in m]

    return HSCodeResponse(
        matches=matches,
        target_country=request.target_country,
        primary_language=data.get("primary_language", "en"),
    )


def _safe_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        # try to extract first JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                pass
    return {}
