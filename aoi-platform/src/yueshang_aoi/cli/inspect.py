"""Command-line interface for YueshangAOI."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from yueshang_aoi import InspectionPipeline, load_profile
from yueshang_aoi.core.config import list_builtin_profiles

console = Console()
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@click.group()
def main():
    """YueshangAOI · Universal AI Visual Inspection."""


@main.command("list-profiles")
def list_profiles_cmd():
    """List available built-in product profiles."""
    profiles = list_builtin_profiles()
    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
        return
    t = Table(title="Available Profiles")
    t.add_column("Name", style="cyan")
    t.add_column("Display")
    t.add_column("Routes")
    for name in profiles:
        try:
            p = load_profile(name)
            display = f"{p.display_name_zh} / {p.display_name_en}"
            routes = ", ".join(r.name for r in p.routes if r.enabled)
        except Exception as e:
            display, routes = f"[red]{e}[/red]", ""
        t.add_row(name, display, routes)
    console.print(t)


@main.command("inspect")
@click.option("--profile", required=True, help="Profile name (eg keyboard) or path to YAML.")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True),
              help="Input image or directory.")
@click.option("--output", "output_dir", default="./out", type=click.Path(),
              help="Output directory.")
@click.option("--report-lang", default="zh", type=click.Choice(["zh", "en", "es", "pt"]),
              help="Report language.")
@click.option("--formats", default="json,html", help="Comma-separated formats: json,html")
def inspect_cmd(profile: str, input_path: str, output_dir: str, report_lang: str, formats: str):
    """Run inspection on an image or directory."""
    profile_obj = load_profile(profile)
    pipeline = InspectionPipeline(profile_obj)
    fmt_tuple = tuple(s.strip() for s in formats.split(","))

    in_path = Path(input_path)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    images = [in_path] if in_path.is_file() else sorted(
        p for p in in_path.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
    )
    if not images:
        console.print("[red]No images to process.[/red]")
        sys.exit(1)

    summary_table = Table(title=f"Inspection Summary · profile={profile}")
    summary_table.add_column("File"); summary_table.add_column("Status")
    summary_table.add_column("Parts"); summary_table.add_column("NG")
    summary_table.add_column("Top defects"); summary_table.add_column("Time (s)")

    for img in images:
        try:
            result = pipeline.run(img)
        except Exception as e:
            console.print(f"[red]Failed: {img.name}: {e}[/red]")
            continue
        result.save_report(out_path, lang=report_lang, formats=fmt_tuple)
        top = ", ".join(f"{k}({v})" for k, v in
                        sorted(result.defect_summary.items(), key=lambda x: -x[1])[:3]) or "-"
        color = "green" if result.overall_status == "OK" else "red"
        summary_table.add_row(
            img.name, f"[{color}]{result.overall_status}[/{color}]",
            str(result.total_parts), str(result.ng_count), top,
            f"{result.elapsed_seconds:.2f}",
        )
    console.print(summary_table)


if __name__ == "__main__":
    main()
