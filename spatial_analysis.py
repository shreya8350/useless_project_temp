"""Spatial analysis, heatmaps, and HV comparison."""

from typing import Any

import cv2
import numpy as np

from backend.utils.helpers import angle_bucket, histogram_bins, safe_divide


def generate_heatmaps(
    damage_mask: np.ndarray,
    lines: list[dict],
    intersections: list[dict],
    clusters: list[dict],
    grid_size: int = 32,
) -> dict[str, list[list[float]]]:
    h, w = damage_mask.shape
    gh = max(h // grid_size, 1)
    gw = max(w // grid_size, 1)

    def downsample(data: np.ndarray) -> list[list[float]]:
        resized = cv2.resize(data.astype(np.float32), (grid_size, grid_size), interpolation=cv2.INTER_AREA)
        return np.round(resized, 4).tolist()

    damage_heat = damage_mask.astype(np.float32) / 255.0

    line_density = np.zeros((h, w), dtype=np.float32)
    for line in lines:
        cv2.line(line_density, (line["x1"], line["y1"]), (line["x2"], line["y2"]),
                 float(line["length"]), max(int(line["width"]), 1))
    if line_density.max() > 0:
        line_density /= line_density.max()

    intersection_heat = np.zeros((h, w), dtype=np.float32)
    for ip in intersections:
        x, y = int(ip["x"]), int(ip["y"])
        if 0 <= y < h and 0 <= x < w:
            cv2.circle(intersection_heat, (x, y), 15, float(ip["line_count"]), -1)
    if intersection_heat.max() > 0:
        intersection_heat /= intersection_heat.max()

    cluster_heat = np.zeros((h, w), dtype=np.float32)
    for c in clusters:
        cx, cy = int(c["centroid_x"]), int(c["centroid_y"])
        cv2.circle(cluster_heat, (cx, cy), max(int(np.sqrt(c["area"])), 3), float(c["area"]), -1)
    if cluster_heat.max() > 0:
        cluster_heat /= cluster_heat.max()

    return {
        "damage": downsample(damage_heat),
        "line_density": downsample(line_density),
        "intersections": downsample(intersection_heat),
        "pixel_clusters": downsample(cluster_heat),
        "grid_size": grid_size,
    }


def horizontal_vertical_analysis(lines: list[dict]) -> dict[str, Any]:
    h_lines = [l for l in lines if l["orientation"] == "horizontal"]
    v_lines = [l for l in lines if l["orientation"] == "vertical"]
    total = len(h_lines) + len(v_lines) or 1

    return {
        "horizontal_count": len(h_lines),
        "vertical_count": len(v_lines),
        "horizontal_total_length": round(sum(l["length"] for l in h_lines), 2),
        "vertical_total_length": round(sum(l["length"] for l in v_lines), 2),
        "horizontal_average_width": round(safe_divide(sum(l["width"] for l in h_lines), len(h_lines)), 2),
        "vertical_average_width": round(safe_divide(sum(l["width"] for l in v_lines), len(v_lines)), 2),
        "horizontal_percentage": round(len(h_lines) / total * 100, 2),
        "vertical_percentage": round(len(v_lines) / total * 100, 2),
        "ratio_display": f"{len(h_lines)} : {len(v_lines)}",
    }


def angle_analysis(lines: list[dict]) -> dict[str, Any]:
    straight = [l for l in lines if l["orientation"] in ("horizontal", "vertical", "diagonal")]
    angles = [l["angle"] for l in straight]
    if not angles:
        return {
            "buckets": {}, "most_common": 0, "least_common": 0,
            "average": 0, "variance": 0, "histogram": {"bins": [], "counts": []},
        }

    buckets: dict[str, int] = {}
    for a in angles:
        b = angle_bucket(a)
        buckets[b] = buckets.get(b, 0) + 1

    most_common = max(buckets, key=buckets.get)
    least_common = min(buckets, key=buckets.get)

    return {
        "buckets": buckets,
        "most_common": most_common,
        "least_common": least_common,
        "average": round(float(np.mean(angles)), 2),
        "variance": round(float(np.var(angles)), 2),
        "histogram": histogram_bins(angles, bins=18),
    }


def build_chart_data(lines: list[dict], colors: dict, regions: dict, pixels: dict, intersections: dict) -> dict[str, Any]:
    orientations = ["horizontal", "vertical", "diagonal", "curved", "irregular"]
    orient_counts = {o: sum(1 for l in lines if l["orientation"] == o) for o in orientations}

    color_names = list(colors.keys())
    cluster_types = pixels.get("type_distribution", {})

    top_longest = sorted(lines, key=lambda l: -l["length"])[:10]
    top_thickest = sorted(lines, key=lambda l: -l["width"])[:10]

    return {
        "orientation_pie": [{"name": o.replace("-", " ").title(), "value": c} for o, c in orient_counts.items() if c > 0],
        "color_pie": [{"name": k, "value": v["area_percentage"]} for k, v in colors.items()],
        "damage_pie": [
            {"name": "Detected Damaged Area", "value": pixels.get("damage_percentage", 0), "fill": "#ff4d4d"},
            {"name": "Remaining Area", "value": pixels.get("unaffected_percentage", 0), "fill": "#10b981"},
        ],
        "cluster_pie": [{"name": k.replace("-", " ").title(), "value": v} for k, v in cluster_types.items() if v > 0],
        "lines_by_color": [{"name": k, "value": v["line_count"]} for k, v in colors.items()],
        "length_by_color": [{"name": k, "value": v["total_length"]} for k, v in colors.items()],
        "damage_by_region": [{"name": k, "value": v["damage_percentage"]} for k, v in regions.items()],
        "lines_by_orientation": [{"name": o, "value": c} for o, c in orient_counts.items()],
        "cluster_size_distribution": [{"name": k, "value": v} for k, v in cluster_types.items()],
        "top_longest_lines": [{"name": f"Line #{l['id']}", "value": l["length"]} for l in top_longest],
        "top_thickest_lines": [{"name": f"Line #{l['id']}", "value": l["width"]} for l in top_thickest],
        "intersections_by_region": [{"name": k, "value": v["intersection_count"]} for k, v in regions.items()],
        "width_histogram": histogram_bins([l["width"] for l in lines], bins=20),
        "length_histogram": histogram_bins([l["length"] for l in lines], bins=20),
        "angle_histogram": histogram_bins([l["angle"] for l in lines], bins=18),
        "scatter_length_width": [{"x": l["length"], "y": l["width"], "id": l["id"]} for l in lines],
        "scatter_length_brightness": [{"x": l["length"], "y": l["brightness"], "id": l["id"]} for l in lines],
        "scatter_width_intensity": [{"x": l["width"], "y": l["intensity"], "id": l["id"]} for l in lines],
    }
