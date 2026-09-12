"""Curved line analysis."""

from typing import Any

import numpy as np

from backend.utils.helpers import safe_divide


def analyze_curves(lines: list[dict]) -> dict[str, Any]:
    curved = [l for l in lines if l["orientation"] in ("curved", "irregular") or l.get("is_contour")]
    results = []

    for line in curved:
        straightness = line.get("straightness", 0.5)
        if straightness > 0.85:
            curvature = 0.1
            classification = "slightly curved"
        elif straightness > 0.6:
            curvature = 0.4
            classification = "moderately curved"
        elif straightness > 0.3:
            curvature = 0.7
            classification = "highly curved"
        else:
            curvature = 0.9
            classification = "irregular"

        points = line.get("contour_points", [])
        turning_points = max(0, len(points) // 20 - 1) if points else 0

        results.append({
            "id": line["id"],
            "length": line["length"],
            "width": line["width"],
            "curvature": round(curvature, 2),
            "turning_points": turning_points,
            "direction": line["orientation"],
            "dominant_color": line["color"],
            "classification": classification,
        })

    avg_curvature = safe_divide(sum(r["curvature"] for r in results), len(results))

    return {
        "count": len(results),
        "curves": results,
        "average_curvature": round(avg_curvature, 2),
        "classifications": {
            "slightly_curved": sum(1 for r in results if r["classification"] == "slightly curved"),
            "moderately_curved": sum(1 for r in results if r["classification"] == "moderately curved"),
            "highly_curved": sum(1 for r in results if r["classification"] == "highly curved"),
            "irregular": sum(1 for r in results if r["classification"] == "irregular"),
        },
    }
