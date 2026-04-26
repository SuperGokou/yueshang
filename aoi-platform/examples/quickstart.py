"""Minimal quickstart: detect anomalies on a single image with no trained models.

Routes that require trained YOLO models will gracefully no-op when models are absent.
This example only uses opencv_anomaly + highpass_edge so it runs out of the box.
"""
from pathlib import Path

from yueshang_aoi import InspectionPipeline, load_profile


def main():
    profile = load_profile("plastic_part")          # works without ML models
    pipeline = InspectionPipeline(profile)

    image_path = Path("samples/sample_part.jpg")
    if not image_path.exists():
        print(f"Place an image at {image_path} and re-run.")
        return

    result = pipeline.run(image_path)
    print(f"Status: {result.overall_status}")
    print(f"Total parts: {result.total_parts}")
    print(f"NG parts: {result.ng_count}")
    print(f"Defects: {result.defect_summary}")

    paths = result.save_report("./out", lang="zh")
    for p in paths:
        print(f"Wrote: {p}")


if __name__ == "__main__":
    main()
