"""The generic three-stage inspection pipeline."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np

from yueshang_aoi.core.config import ProductProfile
from yueshang_aoi.core.result import (
    InspectionResult,
    PartInspection,
    RouteVerdict,
)
from yueshang_aoi.routes.registry import build_routes
from yueshang_aoi.stages.localizer import build_localizer
from yueshang_aoi.stages.roi_detector import build_roi_detector

logger = logging.getLogger(__name__)


class InspectionPipeline:
    """Three-stage AOI pipeline driven by a `ProductProfile`.

    Stage 1: localize the product in the raw image (perspective, crop, deskew).
    Stage 2: detect parts / ROIs (eg keycaps, pins, weld points).
    Stage 3: run multi-route inspection on every part; fuse verdicts.
    """

    def __init__(self, profile: ProductProfile):
        self._profile = profile
        self._localizer = build_localizer(profile.localizer)
        self._roi_detector = build_roi_detector(profile.roi_detector)
        self._routes = build_routes(profile.routes)

    @property
    def profile(self) -> ProductProfile:
        return self._profile

    def run(self, image: Union[str, Path, np.ndarray]) -> InspectionResult:
        """Run inspection on a single image. Returns immutable result."""
        start = time.perf_counter()
        image_path: Optional[str] = None
        if isinstance(image, (str, Path)):
            image_path = str(image)
            img = self._read_image(Path(image))
        else:
            img = image
        h, w = img.shape[:2]

        # Stage 1: localize
        localized = self._localizer.locate(img)
        logger.info("Stage 1 localized: bbox=%s", localized.bbox)

        # Stage 2: ROIs
        rois = self._roi_detector.detect(localized.image)
        logger.info("Stage 2 found %d ROIs", len(rois))

        # Stage 3: multi-route inspection
        parts: list[PartInspection] = []
        for roi in rois:
            verdicts: list[RouteVerdict] = []
            for route in self._routes:
                if not route.enabled:
                    continue
                v = route.inspect(roi.image, context={"profile": self._profile})
                verdicts.append(v)
            part = self._fuse(roi, verdicts)
            parts.append(part)

        # Aggregate
        defect_summary: dict[str, int] = {}
        for p in parts:
            if p.is_ng and p.final_defect_type:
                defect_summary[p.final_defect_type] = defect_summary.get(p.final_defect_type, 0) + 1
        overall = "NG" if any(p.is_ng for p in parts) else "OK"

        return InspectionResult(
            product_id=Path(image_path).stem if image_path else "image",
            profile_name=self._profile.name,
            parts=parts,
            overall_status=overall,
            defect_summary=defect_summary,
            elapsed_seconds=time.perf_counter() - start,
            image_path=image_path,
            image_size=(w, h),
        )

    def _fuse(self, roi, verdicts: list[RouteVerdict]) -> PartInspection:
        strategy = self._profile.fusion.strategy
        positive = [v for v in verdicts if v.is_defect]

        if strategy == "any_positive":
            is_ng = len(positive) >= self._profile.fusion.min_routes_for_ng
        elif strategy == "majority":
            is_ng = len(positive) > len(verdicts) / 2
        elif strategy == "weighted":
            score = sum(v.confidence for v in positive)
            is_ng = score >= self._profile.fusion.min_routes_for_ng
        else:
            is_ng = bool(positive)

        if is_ng and positive:
            top = max(positive, key=lambda v: v.confidence)
            defect_type = top.defect_type
            confidence = top.confidence
            triggered = top.route_name
        else:
            defect_type = None
            confidence = 0.0
            triggered = None

        return PartInspection(
            part_id=roi.part_id,
            part_class=roi.part_class,
            bbox=roi.bbox,
            routes=verdicts,
            final_status="NG" if is_ng else "OK",
            final_defect_type=defect_type,
            final_confidence=confidence,
            triggered_route=triggered,
        )

    @staticmethod
    def _read_image(path: Path) -> np.ndarray:
        if path.suffix.lower() in {".tif", ".tiff"}:
            import tifffile
            arr = tifffile.imread(str(path))
            if arr.ndim == 2:
                arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
            elif arr.shape[-1] == 4:
                arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            return arr
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"Could not read image: {path}")
        return img
