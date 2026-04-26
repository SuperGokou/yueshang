"""Buyer profile / due-diligence agent (lightweight)."""
from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import BaseModel, Field

from yueshang_copilot.llm.router import get_llm

logger = logging.getLogger(__name__)


class BuyerProfileRequest(BaseModel):
    company_name: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    source_message: Optional[str] = None


class BuyerProfileResponse(BaseModel):
    summary: str
    risk_flags: list[str] = Field(default_factory=list)
    likely_industry: Optional[str] = None
    likely_country: Optional[str] = None
    suggested_followups: list[str] = Field(default_factory=list)


_SYSTEM = """You are an export sales analyst. From the partial information provided about a
prospective buyer (company name, email, website, message), produce a brief profile:

- summary (1-2 sentences)
- risk_flags (free email domain, mismatched country code, unrealistic request, etc.)
- likely_industry (best guess)
- likely_country (best guess)
- suggested_followups (3 concrete questions to ask)

Output strict JSON. Do not invent specific facts; if unknown, say so."""


def profile(request: BuyerProfileRequest) -> BuyerProfileResponse:
    user = (
        f"Company: {request.company_name or '(unknown)'}\n"
        f"Email: {request.email or '(unknown)'}\n"
        f"Website: {request.website or '(unknown)'}\n"
        f"Source message: {request.source_message or '(none)'}\n"
    )
    raw = get_llm().chat(_SYSTEM, user, max_tokens=600, temperature=0.2, json_mode=True)
    try:
        data = json.loads(raw)
    except Exception:
        data = {"summary": raw[:300], "risk_flags": [], "suggested_followups": []}
    return BuyerProfileResponse(**{
        "summary": data.get("summary", ""),
        "risk_flags": data.get("risk_flags", []),
        "likely_industry": data.get("likely_industry"),
        "likely_country": data.get("likely_country"),
        "suggested_followups": data.get("suggested_followups", []),
    })
