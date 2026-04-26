"""Stage 2: detect parts (ROIs) within the localized product image."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol

import cv2
import numpy as np

from yueshang_aoi.core.config import ROIDetectorConfig


@dataclass(frozen=True)
class ROI:
    part_id: str
    image: np.ndarray
    bbox: tuple[int, int, int, int]            # x, y, w, h on parent image
    part_class: Optional[str] = None
    score: float = 1.0


class ROIDetector(Protocol):
    def detect(self, image: np.ndarray) -> list[ROI]: ...


class GridROIDetector:
    """Split the image into a fixed grid. Useful for regular arrays (eg keycaps)."""

    def __init__(self, rows: int = 5, cols: int = 14, **_ignored):
        self._rows = rows
        self._cols = cols

    def detect(self, image: np.ndarray) -> list[ROI]:
        h, w = image.shape[:2]
        ph, pw = h // self._rows, w // self._cols
        rois: list[ROI] = []
        for r in range(self._rows):
            for c in range(self._cols):
                x, y = c * pw, r * ph
                crop = image[y:y + ph, x:x + pw]
                rois.append(ROI(
                    part_id=f"r{r:02d}c{c:02d}",
                    image=crop,
                    bbox=(x, y, pw, ph),
                ))
        return rois


class YoloBoxROIDetector:
    """YOLOv8 detection model finds parts."""

    def __init__(self, model_path: str | None = None, conf: float = 0.30,
                 max_det: int = 300, **_ignored):
        self._conf = conf
        self._max_det = max_det
        self._model = None
        if model_path and Path(model_path).exists():
            from ultralytics import YOLO
            self._model = YOLO(model_path)

    def detect(self, image: np.ndarray) -> list[ROI]:
        if self._model is None:
            return GridROIDetector().detect(image)
        result = self._model.predict(
            image, conf=self._conf, max_det=self._max_det, verbose=False,
        )[0]
        rois: list[ROI] = []
        names = result.names if hasattr(result, "names") else {}
        for i, box in enumerate(result.boxes):
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            cls_id = int(box.cls[0]) if box.cls is not None else 0
            crop = image[y1:y2, x1:x2]
            rois.append(ROI(
                part_id=f"part_{i:04d}",
                image=crop,
                bbox=(int(x1), int(y1), int(x2 - x1), int(y2 - y1)),
                part_class=names.get(cls_id, str(cls_id)),
                score=float(box.conf[0]) if box.conf is not None else 0.0,
            ))
        return rois


class TemplateMatchROIDetector:
    """Match a template image; useful for fixed-pattern products like PCBA."""

    def __init__(self, template_path: str | None = None, threshold: float = 0.8, **_ignored):
        self._threshold = threshold
        self._template = None
        if template_path and Path(template_path).exists():
            self._template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    def detect(self, image: np.ndarray) -> list[ROI]:
        if self._template is None:
            return []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        res = cv2.matchTemplate(gray, self._template, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(res >= self._threshold)
        h, w = self._template.shape
        rois: list[ROI] = []
        for i, (y, x) in enumerate(zip(ys, xs)):
            crop = image[y:y + h, x:x + w]
            rois.append(ROI(
                part_id=f"tpl_{i:04d}",
                image=crop,
                bbox=(int(x), int(y), w, h),
                score=float(res[y, x]),
            ))
        return rois


def build_roi_detector(cfg: ROIDetectorConfig) -> ROIDetector:
    if cfg.strategy == "yolo_box":
        return YoloBoxROIDetector(model_path=cfg.model_path, **cfg.params)
    if cfg.strategy == "grid":
        return GridROIDetector(**cfg.params)
    if cfg.strategy == "template_match":
        return TemplateMatchROIDetector(template_path=cfg.model_path, **cfg.params)
    raise ValueError(f"Unknown ROI detector strategy: {cfg.strategy}")
