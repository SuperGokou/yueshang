"""Base interface for inspection routes."""
from __future__ import annotations

from typing import Any, Protocol

import numpy as np

from yueshang_aoi.core.result import RouteVerdict


class Route(Protocol):
    """A detection route inspects one part image and returns a verdict."""

    name: str
    enabled: bool

    def inspect(self, part_image: np.ndarray, context: dict[str, Any]) -> RouteVerdict: ...
