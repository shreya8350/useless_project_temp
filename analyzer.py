"""Main analysis orchestrator."""

import json
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np

from backend.cv.color_analysis import build_color_distribution, compute_color_statistics
from backend.cv.curve_analysis import analyze_curves
from backend.cv.intersection_analysis import analyze_intersections, detect_parallel_groups
from backend.cv.line_detection import detect_lines
from backend.cv.pixel_analysis import build_damage_mask, compute_intensity_histogram, detect_pixel_clusters
from backend.cv.preprocessing import preprocess_image
from backend.cv.region_analysis import analyze_regions
from backend.cv.spatial_analysis import angle_analysis, build_chart_data, generate_heatmaps, horizontal_vertical_analysis
from backend.metrics.awards import calculate_awards, generate_fun_facts
from backend.metrics.chaos import calculate_chaos
from backend.metrics.display_dna import build_line_social_network, generate_display_dna
from backend.metrics.personality import classify_personality
from backend.metrics.repairability import calculate_repairability
from backend.metrics.symmetry import calculate_breakage_level, calculate_symmetry
from backend.metrics.uselessness import calculate_uselessness
from backend.utils.helpers import generate_analysis_id, to_serializable
from backend.utils.visualization import create_annotated_overlay, create_damage_overlay, encode_image_base64

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"

_analysis_cache: dict[str, dict] = {}


def run_analysis(
    image_data: bytes,
    crop: Optional[dict] = None,
    filename: str = "upload.jpg",
) -> dict[str, Any]:
    analysis_id = generate_analysis_id()
    preprocessed = preprocess_image(image_data, crop=crop)
    processed = preprocessed.processed
    gray = preprocessed.gray
    hsv = preprocessed.hsv
    h, w = gray.shape

    lines, line_stats = detect_lines(processed, gray, hsv)

    if not lines:
        raise ValueError(
            "We couldn't find enough visual evidence of a broken display. "
            "Either the screen is surprisingly healthy or the image is too difficult to analyze."
        )

    colors = compute_color_statistics(lines, (h, w))
    color_distribution = build_color_distribution(colors)

    damage_mask = build_damage_mask(gray, lines)
    pixel_data = detect_pixel_clusters(gray, hsv, damage_mask)
    damage_mask_array = pixel_data.pop("damage_mask")

    intersections = analyze_intersections(lines, w, h)
    parallel = detect_parallel_groups(lines)
    curves = analyze_curves(lines)
    regions = analyze_regions(lines, damage_mask_array, intersections["points"], pixel_data["clusters"], w, h)
    hv_analysis = horizontal_vertical_analysis(lines)
    angles = angle_analysis(lines)
    heatmaps = generate_heatmaps(damage_mask_array, lines, intersections["points"], pixel_data["clusters"])
    intensity_hist = compute_intensity_histogram(gray, damage_mask_array)

    symmetry = calculate_symmetry(damage_mask_array)
    chaos = calculate_chaos(line_stats, colors, intersections, curves, pixel_data, regions)
    uselessness = calculate_uselessness(line_stats, colors, intersections, pixel_data, curves, regions, h * w)
    breakage = calculate_breakage_level(pixel_data, line_stats, colors, chaos)
    repairability = calculate_repairability(pixel_data, line_stats, breakage["level"], intersections)
    personality = classify_personality(line_stats, colors, intersections, curves, pixel_data, chaos)
    awards = calculate_awards(lines, colors, regions, line_stats)
    fun_facts = generate_fun_facts(lines, colors, regions, line_stats, pixel_data)
    display_dna = generate_display_dna(colors, line_stats, pixel_data, intersections, curves, uselessness)
    social_network = build_line_social_network(lines, intersections["points"])

    charts = build_chart_data(lines, colors, regions, pixel_data, intersections)
    charts["intensity_histogram"] = intensity_hist

    annotated = create_annotated_overlay(processed, lines, intersections["points"])
    damage_overlay = create_damage_overlay(processed, damage_mask_array)

    aspect_ratio = round(w / h, 3) if h else 0

    result = {
        "id": analysis_id,
        "image": {
            "filename": filename,
            "width": w,
            "height": h,
            "aspect_ratio": aspect_ratio,
            "display_region": {"x": 0, "y": 0, "width": w, "height": h},
            "original_base64": encode_image_base64(processed),
            "annotated_base64": encode_image_base64(annotated),
            "damage_overlay_base64": encode_image_base64(damage_overlay),
        },
        "summary": {
            "total_lines": line_stats["total"],
            "colors_detected": len(colors),
            "intersections": intersections["total"],
            "damage_percentage": pixel_data["damage_percentage"],
            "unaffected_percentage": pixel_data["unaffected_percentage"],
            "disclaimer": "Image-based analysis of detected visual anomalies. Not a confirmed hardware diagnosis.",
        },
        "lines": lines,
        "line_statistics": line_stats,
        "colors": colors,
        "color_distribution": color_distribution,
        "regions": regions,
        "intersections": {**intersections, "parallel_analysis": parallel},
        "pixels": {k: v for k, v in pixel_data.items() if k != "clusters" or True},
        "curves": curves,
        "horizontal_vertical": hv_analysis,
        "angles": angles,
        "metrics": {
            "uselessness": uselessness,
            "chaos": chaos,
            "symmetry": symmetry,
            "breakage": breakage,
            "repairability": repairability,
        },
        "repairability": repairability,
        "personality": personality,
        "awards": awards,
        "fun_facts": fun_facts,
        "display_dna": display_dna,
        "social_network": social_network,
        "visualizations": {
            "charts": charts,
            "heatmaps": heatmaps,
        },
    }

    result = to_serializable(result)
    _analysis_cache[analysis_id] = result

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / f"{analysis_id}.json", "w") as f:
        json.dump(result, f)

    cv2.imwrite(str(OUTPUT_DIR / f"{analysis_id}_annotated.png"), annotated)

    return result


def get_analysis(analysis_id: str) -> Optional[dict]:
    if analysis_id in _analysis_cache:
        return _analysis_cache[analysis_id]
    path = OUTPUT_DIR / f"{analysis_id}.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        _analysis_cache[analysis_id] = data
        return data
    return None


def compare_analyses(result_a: dict, result_b: dict) -> dict:
    def extract(r: dict, label: str) -> dict:
        return {
            "label": label,
            "total_lines": r["summary"]["total_lines"],
            "colors": r["summary"]["colors_detected"],
            "damage_percentage": r["summary"]["damage_percentage"],
            "average_line_width": r["line_statistics"]["average_width"],
            "intersections": r["summary"]["intersections"],
            "chaos": r["metrics"]["chaos"]["score"],
            "uselessness": r["metrics"]["uselessness"]["score"],
            "breakage": r["metrics"]["breakage"]["level"],
        }

    a = extract(result_a, "Screen A")
    b = extract(result_b, "Screen B")

    winner = "Screen A" if a["uselessness"] >= b["uselessness"] else "Screen B"
    winner_label = "A" if winner == "Screen A" else "B"

    return {
        "screen_a": a,
        "screen_b": b,
        "winner": winner,
        "message": f"Screen {winner_label} is objectively more useless.",
        "comparisons": [
            {"metric": "Total Lines", "a": a["total_lines"], "b": b["total_lines"]},
            {"metric": "Colors", "a": a["colors"], "b": b["colors"]},
            {"metric": "Damage %", "a": a["damage_percentage"], "b": b["damage_percentage"]},
            {"metric": "Avg Line Width", "a": a["average_line_width"], "b": b["average_line_width"]},
            {"metric": "Intersections", "a": a["intersections"], "b": b["intersections"]},
            {"metric": "Chaos Index", "a": a["chaos"], "b": b["chaos"]},
            {"metric": "Uselessness", "a": a["uselessness"], "b": b["uselessness"]},
            {"metric": "Breakage Level", "a": a["breakage"], "b": b["breakage"]},
        ],
    }
