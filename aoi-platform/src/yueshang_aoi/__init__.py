"""Yueshang AOI - Universal AI Visual Inspection Platform."""
from yueshang_aoi.core.config import load_profile, ProductProfile
from yueshang_aoi.core.pipeline import InspectionPipeline
from yueshang_aoi.core.result import InspectionResult, PartInspection, RouteVerdict

__version__ = "0.1.0"
__all__ = [
    "InspectionPipeline",
    "ProductProfile",
    "load_profile",
    "InspectionResult",
    "PartInspection",
    "RouteVerdict",
]
