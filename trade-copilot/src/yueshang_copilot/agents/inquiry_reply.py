"""Inquiry reply agent: drafts a professional response to a buyer's inquiry."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from yueshang_copilot.core.schema import InquiryReplyResponse, InquiryRequest
from yueshang_copilot.llm.router import get_llm

logger = logging.getLogger(__name__)


_SYSTEM = """You are a senior export-sales specialist writing on behalf of the user's company.

Your job: read an incoming buyer inquiry and draft a reply that is:
1. Polite and professional, but not over-flowery
2. Asks for the missing information needed to quote (quantity, target unit price, target market,
   shipping terms, deadline, customizations) WITHOUT listing them as a checklist when possible
3. Demonstrates understanding of the buyer's intent
4. Suggests next steps (sample, video call, factory audit) when appropriate
5. Stays in the requested language

Also: identify the buyer's intent in 5 words or less.

Output format (strict, no extra prose):

INTENT: <intent in 5 words or less>
---REPLY---
<the email body to send>
"""


def reply(request: InquiryRequest) -> InquiryReplyResponse:
    sys = _SYSTEM
    if request.company_profile:
        sys = sys + f"\n\nCOMPANY CONTEXT:\n{request.company_profile}"

    user = (
        f"Tone: {request.response_tone}\n"
        f"Reply language: {request.lang}\n\n"
        f"BUYER INQUIRY:\n{request.inquiry}"
    )
    raw = get_llm().chat(sys, user, max_tokens=900, temperature=0.4)

    intent, body = _split(raw)

    today = datetime.now()
    follow_ups = [
        (today + timedelta(days=2)).strftime("%Y-%m-%d"),
        (today + timedelta(days=5)).strftime("%Y-%m-%d"),
        (today + timedelta(days=10)).strftime("%Y-%m-%d"),
    ]
    return InquiryReplyResponse(
        reply=body.strip(),
        lang=request.lang,
        follow_up_dates=follow_ups,
        detected_intent=intent.strip(),
    )


def _split(raw: str) -> tuple[str, str]:
    intent = ""
    body = raw
    if "---REPLY---" in raw:
        head, body = raw.split("---REPLY---", 1)
        for line in head.splitlines():
            if line.strip().upper().startswith("INTENT:"):
                intent = line.split(":", 1)[1].strip()
                break
    return intent, body
