"""Display Repairability Index calculation."""

from backend.utils.helpers import clamp


def calculate_repairability(
    pixels: dict,
    line_stats: dict,
    breakage_level: int,
    intersections: dict,
) -> dict:
    damage = float(pixels.get("damage_percentage", 0))
    total_lines = int(line_stats.get("total", 0))
    intersection_count = int(intersections.get("total", 0))

    # Calculate deterministic repairability percentage (0.0% to 99.9%)
    penalty = (damage * 1.25) + (breakage_level * 5.0) + (total_lines * 0.2) + (intersection_count * 0.25)
    percentage = round(clamp(100.0 - penalty, 0.0, 99.9), 1)

    if percentage >= 75.0:
        status = "High Possibility"
        color = "#10b981"  # Green
        verdict = "Minor visual glitch detected. High probability of fix via ribbon cable reconnect or stuck pixel cycle."
        recommendation = "Attempt soft-reset or ribbon cable re-seating before replacing hardware."
    elif percentage >= 40.0:
        status = "Moderate Possibility"
        color = "#f59e0b"  # Yellow/Orange
        verdict = "Moderate structural damage detected. Panel replacement or digitizer repair likely required."
        recommendation = "Consult a certified technician for display glass & digitizer assembly replacement."
    else:
        status = "Terminal / Abysmal"
        color = "#ef4444"  # Red
        verdict = "Terminal display destruction. Possibility of simple repair is mathematically abysmal."
        recommendation = "Recycle the display and start shopping for a replacement screen."

    glass_fracture_risk = round(min(100.0, damage * 1.8 + line_stats.get("curved", 0) * 8.0), 1)
    digitizer_integrity = round(max(0.0, 100.0 - (damage * 1.1 + intersection_count * 0.8)), 1)
    lcd_bleed_risk = round(min(100.0, pixels.get("large_clusters", 0) * 15.0 + damage * 0.9), 1)

    return {
        "percentage": percentage,
        "status": status,
        "color": color,
        "verdict": verdict,
        "recommendation": recommendation,
        "glass_fracture_risk": glass_fracture_risk,
        "digitizer_integrity": digitizer_integrity,
        "lcd_bleed_risk": lcd_bleed_risk,
    }
