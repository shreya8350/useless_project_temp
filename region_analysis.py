"""3x3 grid region analysis."""

from typing import Any

import numpy as np

from backend.utils.helpers import safe_divide


REGION_NAMES = [
    "top-left", "top-center", "top-right",
    "mid-left", "center", "mid-right",
    "bot-left", "bot-center", "bot-right",
]


def _region_bounds(name: str, w: int, h: int) -> tuple[int, int, int, int]:
    col = REGION_NAMES.index(name) % 3
    row = REGION_NAMES.index(name) // 3
    x1 = col * w // 3
    x2 = (col + 1) * w // 3
    y1 = row * h // 3
    y2 = (row + 1) * h // 3
    return x1, y1, x2, y2


def analyze_regions(
    lines: list[dict],
    damage_mask: np.ndarray,
    intersections: list[dict],
    clusters: list[dict],
    width: int,
    height: int,
) -> dict[str, Any]:
    regions = {}

    for name in REGION_NAMES:
        x1, y1, x2, y2 = _region_bounds(name, width, height)
        region_lines = [l for l in lines if l.get("region") == name]
        region_mask = damage_mask[y1:y2, x1:x2]
        damage_pct = safe_divide(int(np.sum(region_mask > 0)), region_mask.size) * 100

        colors = [l["color"] for l in region_lines]
        dominant_color = max(set(colors), key=colors.count) if colors else "none"

        region_intersections = sum(
            1 for ip in intersections
            if x1 <= ip["x"] < x2 and y1 <= ip["y"] < y2
        )
        region_clusters = sum(
            1 for c in clusters
            if x1 <= c["centroid_x"] < x2 and y1 <= c["centroid_y"] < y2
        )

        lengths = [l["length"] for l in region_lines]
        widths = [l["width"] for l in region_lines]

        complexity = (
            len(region_lines) * 2 +
            damage_pct +
            region_intersections * 3 +
            region_clusters
        )

        regions[name] = {
            "line_count": len(region_lines),
            "damage_percentage": round(damage_pct, 2),
            "dominant_color": dominant_color,
            "average_line_width": round(safe_divide(sum(widths), len(widths)), 2),
            "average_line_length": round(safe_divide(sum(lengths), len(lengths)), 2),
            "intersection_count": region_intersections,
            "pixel_cluster_count": region_clusters,
            "complexity_score": round(complexity, 2),
        }

    return regions
