"""Route registry: maps route name -> implementation class."""
from __future__ import annotations

from yueshang_aoi.core.config import RouteConfig
from yueshang_aoi.routes.golden_match import GoldenMatchRoute
from yueshang_aoi.routes.highpass_edge import HighpassEdgeRoute
from yueshang_aoi.routes.opencv_anomaly import OpenCVAnomalyRoute
from yueshang_aoi.routes.yolo_cls import YoloClassifierRoute

_REGISTRY = {
    "yolo_cls": YoloClassifierRoute,
    "golden_match": GoldenMatchRoute,
    "opencv_anomaly": OpenCVAnomalyRoute,
    "highpass_edge": HighpassEdgeRoute,
}


def build_routes(configs: list[RouteConfig]):
    routes = []
    for c in configs:
        cls = _REGISTRY.get(c.name)
        if cls is None:
            raise ValueError(f"Unknown route: {c.name}. Known: {list(_REGISTRY)}")
        routes.append(cls(enabled=c.enabled, **c.params))
    return routes


def register_route(name: str, cls):
    """Plugin point for third-party routes."""
    _REGISTRY[name] = cls
