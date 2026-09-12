"""Display personality classification."""

from backend.utils.helpers import safe_divide


PERSONALITIES = {
    "THE BARCODE": "Mostly vertical lines dominating the visual field.",
    "THE RAINBOW": "High color diversity across detected anomalies.",
    "THE SPIDER": "Many intersections and curved structures.",
    "THE GRID": "Strong horizontal and vertical patterns.",
    "THE CHAOS MONSTER": "Extremely high complexity across all metrics.",
    "THE MINIMALIST": "Low detected visual abnormality.",
    "THE ABSTRACT ARTIST": "Highly irregular and curved patterns.",
}


def classify_personality(
    line_stats: dict,
    colors: dict,
    intersections: dict,
    curves: dict,
    pixels: dict,
    chaos: dict,
) -> dict:
    total = max(line_stats.get("total", 0), 1)
    v_pct = line_stats.get("vertical", 0) / total
    h_pct = line_stats.get("horizontal", 0) / total
    curved_pct = (line_stats.get("curved", 0) + line_stats.get("irregular", 0)) / total
    color_count = len(colors)
    damage = pixels.get("damage_percentage", 0)
    intersection_count = intersections.get("total", 0)
    chaos_score = chaos.get("score", 0)

    scores = {
        "THE BARCODE": v_pct * 100 + (10 if v_pct > 0.5 else 0),
        "THE RAINBOW": color_count * 12 + (20 if color_count >= 5 else 0),
        "THE SPIDER": intersection_count * 2 + curves.get("count", 0) * 3,
        "THE GRID": (h_pct + v_pct) * 50,
        "THE CHAOS MONSTER": chaos_score,
        "THE MINIMALIST": max(0, 80 - damage * 3 - line_stats.get("total", 0) * 0.5),
        "THE ABSTRACT ARTIST": curved_pct * 80 + line_stats.get("irregular", 0) * 2,
    }

    winner = max(scores, key=scores.get)

    return {
        "type": winner,
        "name": winner,
        "title": winner,
        "description": PERSONALITIES[winner],
        "scores": {k: round(v, 2) for k, v in scores.items()},
    }
