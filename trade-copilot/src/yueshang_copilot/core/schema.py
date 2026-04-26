"""Shared pydantic schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    score: float
    snippet: str = ""


class RAGAnswer(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    lang: str = "zh"
    elapsed_seconds: float = 0.0


class HSCodeRequest(BaseModel):
    product_name_zh: Optional[str] = None
    product_name_en: Optional[str] = None
    description: Optional[str] = None
    material: Optional[str] = None
    target_country: str = "US"


class HSCodeMatch(BaseModel):
    code: str
    description: str
    confidence: float
    duty_rate: Optional[str] = None
    notes: Optional[str] = None


class HSCodeResponse(BaseModel):
    matches: list[HSCodeMatch]
    target_country: str
    primary_language: str = "en"


class InquiryRequest(BaseModel):
    inquiry: str
    lang: str = "en"
    company_profile: Optional[str] = None
    response_tone: str = "professional"     # professional | friendly | concise


class InquiryReplyResponse(BaseModel):
    reply: str
    lang: str
    follow_up_dates: list[str] = Field(default_factory=list)
    detected_intent: str = ""


class ComplianceRequest(BaseModel):
    product_description: str
    target_markets: list[str] = Field(default_factory=lambda: ["EU", "US"])
    materials: list[str] = Field(default_factory=list)
    has_battery: bool = False
    has_wireless: bool = False


class ComplianceFinding(BaseModel):
    market: str
    requirement: str
    severity: str          # required | recommended | informational
    rationale: str


class ComplianceResponse(BaseModel):
    findings: list[ComplianceFinding]
    summary: str


class ProductPageRequest(BaseModel):
    product_name: str
    bullet_features: list[str] = Field(default_factory=list)
    materials: Optional[str] = None
    target_platform: str = "amazon"            # amazon | shopify | ebay | alibaba
    target_lang: str = "en"
    seo_keywords: list[str] = Field(default_factory=list)


class ProductPageResponse(BaseModel):
    title: str
    bullets: list[str]
    description: str
    keywords: list[str]
    lang: str
    platform: str
