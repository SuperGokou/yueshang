"""Smoke test: pipeline runs end-to-end without trained models on a synthetic image."""
import numpy as np

from yueshang_aoi import InspectionPipeline, load_profile


def _make_test_image(h: int = 480, w: int = 640) -> np.ndarray:
    rng = np.random.default_rng(seed=0)
    img = rng.integers(120, 180, size=(h, w, 3), dtype=np.uint8)
    img[100:120, 100:120] = 0          # planted dark blob
    img[200:210, 300:320] = 255        # planted bright blob
    return img


def test_plastic_part_profile_runs_without_models():
    profile = load_profile("plastic_part")
    pipeline = InspectionPipeline(profile)
    img = _make_test_image()
    result = pipeline.run(img)
    assert result.profile_name == "plastic_part"
    assert result.total_parts >= 1
    # planted defects should at least register as NG
    assert result.overall_status == "NG"


def test_metal_part_profile_loads():
    profile = load_profile("metal_part")
    pipeline = InspectionPipeline(profile)
    result = pipeline.run(_make_test_image())
    assert result.profile_name == "metal_part"
