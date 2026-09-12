"""Display Chaos Index™ calculation."""

from backend.utils.helpers import clamp


def calculate_chaos(
    line_stats: dict,
    colors: dict,
    intersections: dict,
    curves: dict,
    pixels: dict,
    regions: dict,
) -> dict:
    line_density = min(line_stats.get("line_density", 0) / 40, 1.0)
    total_lines = max(line_stats.get("total", 1), 1)
    orientations = [
        line_stats.get("horizontal", 0),
        line_stats.get("vertical", 0),
        line_stats.get("diagonal", 0),
        line_stats.get("curved", 0),
        line_stats.get("irregular", 0),
    ]
    orient_probs = [o / total_lines for o in orientations if o > 0]
    import math
    orient_entropy = -sum(p * math.log(p + 1e-9) for p in orient_probs) if orient_probs else 0
    orientation_diversity = min(orient_entropy / 1.6, 1.0)
    color_diversity = min(len(colors) / 7, 1.0)
    intersection_factor = min(intersections.get("total", 0) / max(total_lines * 0.5, 1), 1.0)
    curvature_factor = min(curves.get("average_curvature", 0), 1.0)

    region_damage = [r["damage_percentage"] for r in regions.values()]
    if region_damage:
        max_d = max(region_damage)
        min_d = min(region_damage)
        concentration = 1.0 - min((max_d - min_d) / 50, 1.0)
    else:
        concentration = 0.5

    randomness = min(line_stats.get("angle_variance", 0) / 2000, 1.0)

    score = clamp(
        line_density * 18 +
        orientation_diversity * 18 +
        color_diversity * 14 +
        intersection_factor * 16 +
        curvature_factor * 12 +
        concentration * 12 +
        randomness * 10,
        0, 100,
    )

    return {
        "score": round(score, 1),
        "components": {
            "line_density": round(line_density * 18, 2),
            "orientation_diversity": round(orientation_diversity * 18, 2),
            "color_diversity": round(color_diversity * 14, 2),
            "intersections": round(intersection_factor * 16, 2),
            "curvature": round(curvature_factor * 12, 2),
            "damage_concentration": round(concentration * 12, 2),
            "spatial_randomness": round(randomness * 10, 2),
        },
    }
