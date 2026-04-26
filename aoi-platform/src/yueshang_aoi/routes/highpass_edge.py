"""Route D: Highpass + edge density. Detects scratches and dark streaks."""
from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from yueshang_aoi.core.result import RouteVerdict


class HighpassEdgeRoute:
    name = "highpass_edge"

    def __init__(
        self,
        enabled: bool = True,
        edge_density_threshold: float = 0.06,
        canny_low: int = 60,
        canny_high: int = 160,
    ):
        self.enabled = enabled
        self._density_thr = edge_density_threshold
        self._low = canny_low
        self._high = canny_high

    def inspect(self, part_image: np.ndarray, context: dict[str, Any]) -> RouteVerdict:
        if part_image.size == 0:
            return RouteVerdict(self.name, False, confidence=0.0)
        gray = cv2.cvtColor(part_image, cv2.COLOR_BGR2GRAY) if part_image.ndim == 3 else part_image
        edges = cv2.Canny(gray, self._low, self._high)
        density = float(np.count_nonzero(edges)) / edges.size
        is_def = density > self._density_thr
        return RouteVerdict(
            self.name,
            is_defect=is_def,
            defect_type="dark_streak" if is_def else None,
            confidence=min(1.0, density / max(self._density_thr, 1e-6)),
            metadata={"edge_density": round(density, 4)},
        )
