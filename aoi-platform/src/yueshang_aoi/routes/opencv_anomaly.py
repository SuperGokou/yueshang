"""Route C: OpenCV-based anomaly detection. Cheap, deterministic, good for stains/black-dots."""
from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from yueshang_aoi.core.result import RouteVerdict


class OpenCVAnomalyRoute:
    """Detects low-brightness blobs (stains, black dots) and high-brightness blobs (bright marks)."""

    name = "opencv_anomaly"

    def __init__(
        self,
        enabled: bool = True,
        dark_threshold: int = 60,
        bright_threshold: int = 220,
        min_blob_area: int = 8,
        max_blob_area_ratio: float = 0.05,
    ):
        self.enabled = enabled
        self._dark_thr = dark_threshold
        self._bright_thr = bright_threshold
        self._min_area = min_blob_area
        self._max_area_ratio = max_blob_area_ratio

    def inspect(self, part_image: np.ndarray, context: dict[str, Any]) -> RouteVerdict:
        if part_image.size == 0:
            return RouteVerdict(self.name, False, confidence=0.0)
        gray = cv2.cvtColor(part_image, cv2.COLOR_BGR2GRAY) if part_image.ndim == 3 else part_image
        h, w = gray.shape
        max_area = self._max_area_ratio * h * w

        dark = cv2.threshold(gray, self._dark_thr, 255, cv2.THRESH_BINARY_INV)[1]
        bright = cv2.threshold(gray, self._bright_thr, 255, cv2.THRESH_BINARY)[1]

        dark_blobs = self._count_blobs(dark, max_area)
        bright_blobs = self._count_blobs(bright, max_area)

        if dark_blobs > 0:
            return RouteVerdict(
                self.name, True, defect_type="black_dot",
                confidence=min(1.0, dark_blobs * 0.4),
                metadata={"blob_count": dark_blobs},
            )
        if bright_blobs > 0:
            return RouteVerdict(
                self.name, True, defect_type="bright_mark",
                confidence=min(1.0, bright_blobs * 0.4),
                metadata={"blob_count": bright_blobs},
            )
        return RouteVerdict(self.name, False, confidence=0.0)

    def _count_blobs(self, mask: np.ndarray, max_area: float) -> int:
        n_labels, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        count = 0
        for i in range(1, n_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if self._min_area <= area <= max_area:
                count += 1
        return count
