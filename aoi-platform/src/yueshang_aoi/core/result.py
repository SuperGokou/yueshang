"""Inspection result data classes (immutable)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class RouteVerdict:
    """Single route's verdict on a single part."""

    route_name: str            # "yolo_cls" | "golden_match" | "opencv_anomaly" | "highpass_edge"
    is_defect: bool
    defect_type: Optional[str] = None
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PartInspection:
    """Inspection of a single part/ROI within the product."""

    part_id: str                       # e.g. "keycap_42", "pin_07"
    part_class: Optional[str] = None   # semantic class, e.g. "A_key", "USB_pin"
    bbox: tuple[int, int, int, int] = (0, 0, 0, 0)   # x, y, w, h on full image
    routes: list[RouteVerdict] = field(default_factory=list)
    final_status: str = "OK"           # "OK" | "NG"
    final_defect_type: Optional[str] = None
    final_confidence: float = 0.0
    triggered_route: Optional[str] = None

    @property
    def is_ng(self) -> bool:
        return self.final_status == "NG"


@dataclass(frozen=True)
class InspectionResult:
    """Full product inspection result."""

    product_id: str                          # source filename or barcode
    profile_name: str                        # which profile was used
    parts: list[PartInspection] = field(default_factory=list)
    overall_status: str = "OK"               # "OK" if all parts OK, else "NG"
    defect_summary: dict[str, int] = field(default_factory=dict)  # type -> count
    elapsed_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    image_path: Optional[str] = None
    image_size: tuple[int, int] = (0, 0)     # w, h
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_parts(self) -> int:
        return len(self.parts)

    @property
    def ok_count(self) -> int:
        return sum(1 for p in self.parts if not p.is_ng)

    @property
    def ng_count(self) -> int:
        return sum(1 for p in self.parts if p.is_ng)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save_report(
        self,
        output_dir: str | Path,
        lang: str = "zh",
        formats: tuple[str, ...] = ("json", "html"),
    ) -> list[Path]:
        """Save reports in requested formats and language. Returns written paths."""
        from yueshang_aoi.reporting.html_writer import write_html_report
        from yueshang_aoi.reporting.json_writer import write_json_report

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []

        if "json" in formats:
            written.append(write_json_report(self, output_dir))
        if "html" in formats:
            written.append(write_html_report(self, output_dir, lang=lang))
        return written
