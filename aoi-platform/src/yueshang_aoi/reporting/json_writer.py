"""Write JSON inspection reports."""
from __future__ import annotations

from pathlib import Path

from yueshang_aoi.core.result import InspectionResult


def write_json_report(result: InspectionResult, output_dir: Path) -> Path:
    out = output_dir / f"{result.product_id}.json"
    out.write_text(result.to_json(), encoding="utf-8")
    return out
