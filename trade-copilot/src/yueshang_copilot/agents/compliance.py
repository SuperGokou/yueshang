"""Compliance radar agent: lists likely required certifications and flags risks."""
from __future__ import annotations

import json
import logging

from yueshang_copilot.core.schema import (
    ComplianceFinding,
    ComplianceRequest,
    ComplianceResponse,
)
from yueshang_copilot.llm.router import get_llm
from yueshang_copilot.rag.retriever import Retriever

logger = logging.getLogger(__name__)


_SYSTEM = """You are a cross-border trade compliance analyst. Given a product description,
target markets, materials, and electrical features, list specific compliance requirements
that apply. Cover at minimum: required certifications (CE, FCC, RoHS, REACH, CCC, FDA, UKCA,
PSE, KC, BIS, INMETRO etc.), labelling, restricted-substance limits, and battery/wireless
specific rules where relevant.

Respond as strict JSON:
{
  "findings": [
    {"market":"EU","requirement":"...","severity":"required|recommended|informational","rationale":"..."}
  ],
  "summary": "1-2 sentence high-level summary"
}
"""


def assess(request: ComplianceRequest, collection: str = "compliance") -> ComplianceResponse:
    user = (
        f"Product: {request.product_description}\n"
        f"Target markets: {', '.join(request.target_markets)}\n"
        f"Materials: {', '.join(request.materials) if request.materials else 'unspecified'}\n"
        f"Has battery: {request.has_battery}\n"
        f"Has wireless: {request.has_wireless}\n"
    )

    # Retrieve compliance reference docs
    try:
        chunks = Retriever(collection=collection, top_k=8).retrieve(
            request.product_description + " " + " ".join(request.target_markets)
        )
        if chunks:
            user += "\nReference excerpts:\n" + "\n---\n".join(c.text for c in chunks[:5])
    except Exception as e:
        logger.warning("compliance retrieval skipped: %s", e)

    raw = get_llm().chat(_SYSTEM, user, max_tokens=1400, temperature=0.0, json_mode=True)
    try:
        data = json.loads(raw)
    except Exception:
        data = {"findings": [], "summary": raw[:300]}
    findings = [ComplianceFinding(**f) for f in data.get("findings", [])
                if {"market", "requirement", "severity", "rationale"} <= f.keys()]
    return ComplianceResponse(findings=findings, summary=data.get("summary", ""))
