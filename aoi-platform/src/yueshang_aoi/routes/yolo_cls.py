"""Route A: YOLOv8-cls CNN classifier. The workhorse route for surface defects."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from yueshang_aoi.core.result import RouteVerdict


class YoloClassifierRoute:
    name = "yolo_cls"

    def __init__(
        self,
        enabled: bool = True,
        model_path: str | None = None,
        confidence_threshold: float = 0.55,
        ok_class: str = "ok",
        imgsz: int = 224,
    ):
        self.enabled = enabled
        self._threshold = confidence_threshold
        self._ok_class = ok_class
        self._imgsz = imgsz
        self._model = None
        if model_path and Path(model_path).exists():
            from ultralytics import YOLO
            self._model = YOLO(model_path)

    def inspect(self, part_image: np.ndarray, context: dict[str, Any]) -> RouteVerdict:
        if self._model is None:
            return RouteVerdict(self.name, False, confidence=0.0,
                                metadata={"reason": "model_not_loaded"})
        if part_image.size == 0:
            return RouteVerdict(self.name, False, confidence=0.0)

        result = self._model.predict(part_image, imgsz=self._imgsz, verbose=False)[0]
        probs = result.probs
        if probs is None:
            return RouteVerdict(self.name, False, confidence=0.0)

        top1_id = int(probs.top1)
        top1_name = result.names[top1_id]
        top1_conf = float(probs.top1conf)

        is_def = top1_name != self._ok_class and top1_conf >= self._threshold
        return RouteVerdict(
            self.name,
            is_defect=is_def,
            defect_type=top1_name if is_def else None,
            confidence=top1_conf,
            metadata={"all_probs": probs.data.cpu().numpy().tolist()},
        )
