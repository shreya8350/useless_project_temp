"""Uselessness Score™ calculation."""

from backend.utils.helpers import clamp, safe_divide


def interpret_uselessness(score: float) -> str:
    if score <= 20:
        return "Barely useless"
    if score <= 40:
        return "Mildly useless"
    if score <= 60:
        return "Properly useless"
    if score <= 80:
        return "Extremely useless"
    return "Scientifically unnecessary"


def calculate_uselessness(
    line_stats: dict,
    colors: dict,
    intersections: dict,
    pixels: dict,
    curves: dict,
    regions: dict,
    image_area: int,
) -> dict:
    line_density = min(line_stats.get("line_density", 0) / 50, 1.0)
    color_diversity = min(len(colors) / 8, 1.0)
    orientations = [
        line_stats.get("horizontal", 0),
        line_stats.get("vertical", 0),
        line_stats.get("diagonal", 0),
        line_stats.get("curved", 0),
        line_stats.get("irregular", 0),
    ]
    total_lines = max(line_stats.get("total", 1), 1)
    orient_probs = [o / total_lines for o in orientations if o > 0]
    orientation_entropy = -sum(p * __import__("math").log(p + 1e-9) for p in orient_probs)
    orientation_diversity = min(orientation_entropy / 1.6, 1.0)

    intersection_density = min(intersections.get("total", 0) / max(total_lines, 1), 1.0)
    damage_complexity = min(pixels.get("damage_percentage", 0) / 50, 1.0)
    curvature = min(curves.get("average_curvature", 0), 1.0)
    cluster_complexity = min(pixels.get("cluster_count", 0) / 100, 1.0)

    region_damage = [r["damage_percentage"] for r in regions.values()]
    spatial_irregularity = 0.0
    if region_damage:
        mean_d = sum(region_damage) / len(region_damage)
        spatial_irregularity = min(
            sum(abs(d - mean_d) for d in region_damage) / (len(region_damage) * 50),
            1.0,
        )

    components = {
        "line_complexity": round(line_density * 20, 2),
        "color_diversity": round(color_diversity * 15, 2),
        "orientation_diversity": round(orientation_diversity * 15, 2),
        "intersection_complexity": round(intersection_density * 15, 2),
        "damage_complexity": round(damage_complexity * 15, 2),
        "curvature": round(curvature * 10, 2),
        "cluster_complexity": round(cluster_complexity * 5, 2),
        "spatial_irregularity": round(spatial_irregularity * 5, 2),
    }

    raw = sum(components.values())
    score = clamp(raw, 0, 100)

    return {
        "score": round(score, 1),
        "interpretation": interpret_uselessness(score),
        "components": components,
        "formula": "Weighted sum of line complexity, color diversity, orientation diversity, "
                   "intersection complexity, damage complexity, curvature, cluster complexity, spatial irregularity.",
    }
