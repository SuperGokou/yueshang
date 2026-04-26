"""Product detail page generator (multilingual, platform-aware)."""
from __future__ import annotations

import json
import logging

from yueshang_copilot.core.schema import ProductPageRequest, ProductPageResponse
from yueshang_copilot.llm.router import get_llm

logger = logging.getLogger(__name__)


_PLATFORM_GUIDES = {
    "amazon": (
        "Amazon: title <= 200 chars, lead with brand + key feature. "
        "Bullets <= 5, each <= 250 chars, benefit-led. "
        "Description: HTML-light, scannable. Backend keywords matter."
    ),
    "shopify": (
        "Shopify: title is SEO-led. "
        "Description: rich HTML, story-driven. Bullets optional. "
        "Include H2/H3 sections."
    ),
    "ebay": (
        "eBay: title <= 80 chars, keyword-stuffed. "
        "Bullets: feature/spec list. "
        "Description: simple HTML, mobile-first."
    ),
    "alibaba": (
        "Alibaba International: B2B tone. "
        "Title: model + spec + MOQ. "
        "Bullets focus on customization, MOQ, lead time. "
        "Description: trade terms (FOB, EXW), packaging."
    ),
}

_SYSTEM = """You are a senior cross-border e-commerce copywriter fluent in zh/en/es/pt/de/fr/ja/ar.

Generate a product detail page tailored to the target platform and language. Platform conventions:
{platform_guides}

Output strict JSON:
{{
  "title": "...",
  "bullets": ["...", "..."],
  "description": "...",
  "keywords": ["...", "..."]
}}
"""


def generate(request: ProductPageRequest) -> ProductPageResponse:
    sys = _SYSTEM.format(
        platform_guides="\n- ".join(f"{k}: {v}" for k, v in _PLATFORM_GUIDES.items())
    )
    user = (
        f"Product: {request.product_name}\n"
        f"Materials: {request.materials or 'unspecified'}\n"
        f"Bullet features:\n- " + "\n- ".join(request.bullet_features) + "\n"
        f"\nTarget platform: {request.target_platform}\n"
        f"Target language: {request.target_lang}\n"
        f"SEO keywords seed: {', '.join(request.seo_keywords)}\n"
    )
    raw = get_llm().chat(sys, user, max_tokens=1400, temperature=0.5, json_mode=True)
    try:
        data = json.loads(raw)
    except Exception:
        data = {"title": "", "bullets": [], "description": raw[:500], "keywords": []}

    return ProductPageResponse(
        title=data.get("title", ""),
        bullets=data.get("bullets", []),
        description=data.get("description", ""),
        keywords=data.get("keywords", []),
        lang=request.target_lang,
        platform=request.target_platform,
    )
