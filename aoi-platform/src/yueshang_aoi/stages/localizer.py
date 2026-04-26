"""Stage 1: locate the product in a raw image."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import cv2
import numpy as np

from yueshang_aoi.core.config import LocalizerConfig


@dataclass(frozen=True)
class LocalizationResult:
    image: np.ndarray                          # cropped/deskewed product image
    bbox: tuple[int, int, int, int]            # (x, y, w, h) on input
    angle_deg: float = 0.0
    metadata: dict | None = None


class Localizer(Protocol):
    def locate(self, image: np.ndarray) -> LocalizationResult: ...


class IdentityLocalizer:
    """No-op: returns the input image unchanged. Use when ROI detector handles full frame."""

    def locate(self, image: np.ndarray) -> LocalizationResult:
        h, w = image.shape[:2]
        return LocalizationResult(image=image, bbox=(0, 0, w, h))


class PerspectiveLocalizer:
    """Adaptive threshold + largest contour + 4-point perspective. Good for flat objects on contrasting background."""

    def __init__(
        self,
        block_size: int = 51,
        c: int = 5,
        min_area_ratio: float = 0.10,
        **_ignored,
    ):
        self._block_size = block_size if block_size % 2 else block_size + 1
        self._c = c
        self._min_area_ratio = min_area_ratio

    def locate(self, image: np.ndarray) -> LocalizationResult:
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        thr = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
            self._block_size, self._c,
        )
        thr = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        cnts, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return IdentityLocalizer().locate(image)

        cnt = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(cnt) < self._min_area_ratio * h * w:
            return IdentityLocalizer().locate(image)

        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect).astype(np.float32)
        ow, oh = self._target_size(rect)
        dst = np.array([[0, oh], [0, 0], [ow, 0], [ow, oh]], dtype=np.float32)
        m = cv2.getPerspectiveTransform(box, dst)
        warped = cv2.warpPerspective(image, m, (int(ow), int(oh)))

        x, y, bw, bh = cv2.boundingRect(cnt)
        return LocalizationResult(
            image=warped, bbox=(x, y, bw, bh), angle_deg=rect[-1],
        )

    @staticmethod
    def _target_size(rect) -> tuple[float, float]:
        (_, _), (rw, rh), _ = rect
        return (max(rw, rh), min(rw, rh))


class ThresholdLocalizer:
    """Otsu threshold + largest connected component. Cheap, good for very contrasted backgrounds."""

    def locate(self, image: np.ndarray) -> LocalizationResult:
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return IdentityLocalizer().locate(image)
        x, y, bw_, bh_ = cv2.boundingRect(max(cnts, key=cv2.contourArea))
        crop = image[y:y + bh_, x:x + bw_]
        return LocalizationResult(image=crop, bbox=(x, y, bw_, bh_))


def build_localizer(cfg: LocalizerConfig) -> Localizer:
    if cfg.strategy == "none":
        return IdentityLocalizer()
    if cfg.strategy == "opencv_perspective":
        return PerspectiveLocalizer(**cfg.params)
    if cfg.strategy == "threshold":
        return ThresholdLocalizer()
    if cfg.strategy == "yolo_box":
        # Defer heavy import. Falls back to identity if model not configured.
        from yueshang_aoi.stages._yolo_localizer import YoloLocalizer
        return YoloLocalizer(**cfg.params)
    raise ValueError(f"Unknown localizer strategy: {cfg.strategy}")
