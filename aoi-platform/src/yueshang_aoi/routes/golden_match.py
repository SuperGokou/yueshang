"""Route B: Golden reference matching. Compares part to a known-good reference."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np

from yueshang_aoi.core.result import RouteVerdict


class GoldenMatchRoute:
    """Lightweight implementation: SSIM-style similarity vs a per-class golden image.

    Production version stores per-part-class golden tiles indexed by an ID classifier.
    This MVP loads a single golden image (or directory) and uses normalized cross-correlation.
    """

    name = "golden_match"

    def __init__(
        self,
        enabled: bool = True,
        golden_dir: str | None = None,
        similarity_threshold: float = 0.78,
        resize_to: int = 96,
    ):
        self.enabled = enabled
        self._threshold = similarity_threshold
        self._resize_to = resize_to
        self._goldens: dict[str, np.ndarray] = {}
        if golden_dir and Path(golden_dir).exists():
            for p in Path(golden_dir).glob("*.*"):
                img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self._goldens[p.stem] = self._normalize(img)

    def inspect(self, part_image: np.ndarray, context: dict[str, Any]) -> RouteVerdict:
        if not self._goldens or part_image.size == 0:
            return RouteVerdict(self.name, False, confidence=0.0,
                                metadata={"reason": "no_reference"})
        gray = cv2.cvtColor(part_image, cv2.COLOR_BGR2GRAY) if part_image.ndim == 3 else part_image
        probe = self._normalize(gray)

        # Try every golden, take best match
        best = -1.0
        best_id: Optional[str] = None
        for gid, g in self._goldens.items():
            score = float(cv2.matchTemplate(probe, g, cv2.TM_CCOEFF_NORMED).max())
            if score > best:
                best, best_id = score, gid

        is_def = best < self._threshold
        return RouteVerdict(
            self.name,
            is_defect=is_def,
            defect_type="surface_anomaly" if is_def else None,
            confidence=max(0.0, 1.0 - best),
            metadata={"matched": best_id, "similarity": round(best, 4)},
        )

    def _normalize(self, img: np.ndarray) -> np.ndarray:
        return cv2.resize(img, (self._resize_to, self._resize_to))
