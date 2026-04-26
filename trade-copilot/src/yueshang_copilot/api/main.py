"""FastAPI gateway exposing all Copilot agents and RAG QA."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from yueshang_copilot.agents import buyer_profile as agt_buyer
from yueshang_copilot.agents import compliance as agt_comp
from yueshang_copilot.agents import hscode as agt_hs
from yueshang_copilot.agents import inquiry_reply as agt_inq
from yueshang_copilot.agents import product_page as agt_pp
from yueshang_copilot.core.schema import (
    ComplianceRequest,
    ComplianceResponse,
    HSCodeRequest,
    HSCodeResponse,
    InquiryReplyResponse,
    InquiryRequest,
    ProductPageRequest,
    ProductPageResponse,
    RAGAnswer,
)
from yueshang_copilot.rag import qa as rag_qa


app = FastAPI(
    title="YueshangCopilot API",
    version="0.1.0",
    description="Foreign-trade & cross-border AI Copilot — by Yueshang Technology.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "yueshang-copilot"}


@app.post("/agents/hscode", response_model=HSCodeResponse, tags=["agents"])
def hscode(req: HSCodeRequest):
    return agt_hs.classify(req)


@app.post("/agents/inquiry-reply", response_model=InquiryReplyResponse, tags=["agents"])
def inquiry_reply(req: InquiryRequest):
    return agt_inq.reply(req)


@app.post("/agents/compliance", response_model=ComplianceResponse, tags=["agents"])
def compliance(req: ComplianceRequest):
    return agt_comp.assess(req)


@app.post("/agents/product-page", response_model=ProductPageResponse, tags=["agents"])
def product_page(req: ProductPageRequest):
    return agt_pp.generate(req)


@app.post("/agents/buyer-profile", response_model=agt_buyer.BuyerProfileResponse, tags=["agents"])
def buyer_profile(req: agt_buyer.BuyerProfileRequest):
    return agt_buyer.profile(req)


@app.get("/rag/answer", response_model=RAGAnswer, tags=["rag"])
def rag_answer(question: str, collection: str = "demo", lang: str = "zh", top_k: int = 6):
    return rag_qa.answer(question, collection=collection, lang=lang, top_k=top_k)
