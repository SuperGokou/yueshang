"""YOLO-based product localizer (lazy import)."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from yueshang_aoi.stages.localizer import IdentityLocalizer, LocalizationResult


class YoloLocalizer:
    def __init__(self, model_path: str | None = None, conf: float = 0.5, **_ignored):
        self._model = None
        self._conf = conf
        if model_path and Path(model_path).exists():
            from ultralytics import YOLO
            self._model = YOLO(model_path)

    def locate(self, image: np.ndarray) -> LocalizationResult:
        if self._model is None:
            return IdentityLocalizer().locate(image)
        h, w = image.shape[:2]
        result = self._model.predict(image, conf=self._conf, verbose=False)
        if not result or not len(result[0].boxes):
            return IdentityLocalizer().locate(image)
        box = result[0].boxes[0].xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = box
        crop = image[y1:y2, x1:x2]
        return LocalizationResult(image=crop, bbox=(int(x1), int(y1), int(x2 - x1), int(y2 - y1)))
