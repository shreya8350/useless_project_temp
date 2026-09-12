"""Useless Awards™ calculation."""

from collections import Counter

from backend.utils.helpers import safe_divide


def calculate_awards(lines: list[dict], colors: dict, regions: dict, line_stats: dict) -> list[dict]:
    if not lines:
        return []

    longest = max(lines, key=lambda l: l["length"])
    thickest = max(lines, key=lambda l: l["width"])
    thinnest = min(lines, key=lambda l: l["width"])
    loneliest = max(lines, key=lambda l: l["nearest_line_distance"])
    most_social = max(lines, key=lambda l: l["intersections"])

    dramatic_color = max(colors.items(), key=lambda x: x[1]["area_percentage"])[0] if colors else "none"

    angles = [l["angle"] for l in lines if l["orientation"] in ("horizontal", "vertical", "diagonal")]
    popular_angle = Counter(angles).most_common(1)[0][0] if angles else 0

    most_damaged_zone = max(regions.items(), key=lambda x: x[1]["damage_percentage"])[0] if regions else "center"
    most_chaotic = max(regions.items(), key=lambda x: x[1]["complexity_score"])[0] if regions else "center"

    return [
        {"title": "LONGEST LINE", "emoji": "🏆", "winner": f"Line #{longest['id']}", "value": f"{longest['length']:.1f}px"},
        {"title": "THICKEST LINE", "emoji": "🏆", "winner": f"Line #{thickest['id']}", "value": f"{thickest['width']:.1f}px"},
        {"title": "THINNEST LINE", "emoji": "🏆", "winner": f"Line #{thinnest['id']}", "value": f"{thinnest['width']:.1f}px"},
        {"title": "LONELIEST LINE", "emoji": "🏆", "winner": f"Line #{loneliest['id']}", "value": f"{loneliest['nearest_line_distance']:.1f}px from nearest"},
        {"title": "MOST SOCIAL LINE", "emoji": "🏆", "winner": f"Line #{most_social['id']}", "value": f"{most_social['intersections']} intersections"},
        {"title": "MOST DRAMATIC COLOR", "emoji": "🏆", "winner": dramatic_color.title(), "value": f"{colors.get(dramatic_color, {}).get('area_percentage', 0):.1f}% of damaged area"},
        {"title": "MOST POPULAR ANGLE", "emoji": "🏆", "winner": f"{popular_angle:.1f}°", "value": f"{angles.count(popular_angle)} lines"},
        {"title": "MOST DAMAGED ZONE", "emoji": "🏆", "winner": most_damaged_zone.replace("-", " ").title(), "value": f"{regions[most_damaged_zone]['damage_percentage']:.1f}% damage"},
        {"title": "MOST CHAOTIC REGION", "emoji": "🏆", "winner": most_chaotic.replace("-", " ").title(), "value": f"Complexity {regions[most_chaotic]['complexity_score']:.1f}"},
    ]


def generate_fun_facts(lines: list[dict], colors: dict, regions: dict, line_stats: dict, pixels: dict) -> list[str]:
    facts = []
    if not lines:
        facts.append("No lines detected. Your display is suspiciously well-behaved.")
        return facts

    avg_len = line_stats.get("average_length", 1)
    longest = line_stats.get("longest", 0)
    if avg_len > 0:
        facts.append(f"Your longest line is {longest / avg_len:.1f}× longer than the average line.")

    if colors:
        top_color = max(colors.items(), key=lambda x: x[1]["area_percentage"])
        facts.append(f"{top_color[0].title()} occupies {top_color[1]['area_percentage']:.1f}% of the detected damaged-line area.")

    loneliest = max(lines, key=lambda l: l["nearest_line_distance"])
    if loneliest["nearest_line_distance"] > 100:
        facts.append(f"Line #{loneliest['id']} appears to be socially isolated.")

    if regions:
        sorted_regions = sorted(regions.items(), key=lambda x: -x[1]["damage_percentage"])
        top, bottom = sorted_regions[0], sorted_regions[-1]
        if bottom[1]["damage_percentage"] > 0:
            ratio = top[1]["damage_percentage"] / bottom[1]["damage_percentage"]
            facts.append(
                f"The {top[0].replace('-', ' ')} region contains {ratio:.1f}× more detected abnormalities than the {bottom[0].replace('-', ' ')}."
            )

    facts.append(f"Estimated {pixels.get('estimated_abnormal_pixels', 0):,} visually abnormal pixels identified.")
    return facts
