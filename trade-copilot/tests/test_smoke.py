"""Smoke tests - run without external API keys."""
from yueshang_copilot.core.config import Settings, get_settings
from yueshang_copilot.core.schema import (
    HSCodeRequest,
    InquiryRequest,
    ProductPageRequest,
)


def test_settings_load():
    s = Settings()
    assert s.supported_langs_list


def test_schema_round_trip():
    req = HSCodeRequest(product_name_en="304 stainless steel mug", target_country="US")
    d = req.model_dump()
    assert d["target_country"] == "US"


def test_inquiry_schema():
    req = InquiryRequest(inquiry="Hi, do you make custom mugs?", lang="en")
    assert req.response_tone == "professional"


def test_product_page_schema():
    req = ProductPageRequest(
        product_name="Wireless charger",
        bullet_features=["15W fast charge", "Qi compatible"],
        target_platform="amazon",
        target_lang="en",
    )
    assert req.target_platform == "amazon"
