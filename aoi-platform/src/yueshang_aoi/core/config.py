"""Profile loading and validation. A Profile = product-specific configuration."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, ConfigDict


_BUILTIN_PROFILES_DIR = Path(__file__).resolve().parents[3] / "configs" / "profiles"
_DEFAULTS_PATH = Path(__file__).resolve().parents[3] / "configs" / "defaults.yaml"


class DefectCategory(BaseModel):
    """One defect type (eg "scratch", "burr")."""

    id: int
    code: str                                  # english slug, used as key
    label_zh: str                              # 中文显示
    label_en: str                              # English display
    label_es: Optional[str] = None             # Español
    label_pt: Optional[str] = None             # Português
    severity: str = "major"                    # critical | major | minor
    group: str = "surface"                     # surface | structural | contamination | point_defect
    color: str = "#FF6600"                     # annotation color


class LocalizerConfig(BaseModel):
    """Stage 1: Product localization strategy."""

    strategy: str = "opencv_perspective"       # opencv_perspective | yolo_box | threshold | none
    params: dict[str, Any] = Field(default_factory=dict)


class ROIDetectorConfig(BaseModel):
    """Stage 2: Part/ROI detection strategy."""

    strategy: str = "yolo_box"                 # yolo_box | grid | template_match
    model_path: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)


class RouteConfig(BaseModel):
    """Stage 3 route configuration."""

    name: str                                  # yolo_cls | golden_match | opencv_anomaly | highpass_edge
    enabled: bool = True
    weight: float = 1.0
    params: dict[str, Any] = Field(default_factory=dict)


class FusionConfig(BaseModel):
    """Multi-route fusion strategy."""

    strategy: str = "any_positive"             # any_positive | weighted | majority
    min_routes_for_ng: int = 1


class ProductProfile(BaseModel):
    """Top-level product configuration."""

    model_config = ConfigDict(extra="allow")

    name: str
    display_name_zh: str
    display_name_en: str
    description: Optional[str] = None
    version: str = "1.0.0"

    defect_categories: list[DefectCategory] = Field(default_factory=list)
    localizer: LocalizerConfig = Field(default_factory=LocalizerConfig)
    roi_detector: ROIDetectorConfig = Field(default_factory=ROIDetectorConfig)
    routes: list[RouteConfig] = Field(default_factory=list)
    fusion: FusionConfig = Field(default_factory=FusionConfig)

    def defect_by_code(self, code: str) -> Optional[DefectCategory]:
        for d in self.defect_categories:
            if d.code == code:
                return d
        return None


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Recursively merge overlay onto base. Lists are replaced, not merged."""
    out = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_profile(name_or_path: str) -> ProductProfile:
    """Load a profile by built-in name or path to a YAML file."""
    candidate = Path(name_or_path)
    if candidate.suffix in {".yaml", ".yml"} and candidate.exists():
        path = candidate
    else:
        path = _BUILTIN_PROFILES_DIR / f"{name_or_path}.yaml"
        if not path.exists():
            raise FileNotFoundError(
                f"Profile '{name_or_path}' not found. Looked at {path}"
            )

    defaults = _read_yaml(_DEFAULTS_PATH)
    overlay = _read_yaml(path)
    merged = _deep_merge(defaults, overlay)
    return ProductProfile(**merged)


def list_builtin_profiles() -> list[str]:
    if not _BUILTIN_PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in _BUILTIN_PROFILES_DIR.glob("*.yaml"))
