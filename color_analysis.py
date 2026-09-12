"""Color classification and statistics for detected features."""

from typing import Any
import cv2
import numpy as np

from backend.utils.helpers import safe_divide


def classify_pixel_color(hsv_pixel: np.ndarray) -> str:
    h, s, v = int(hsv_pixel[0]), int(hsv_pixel[1]), int(hsv_pixel[2])

    # Low saturation handling (white/gray/black)
    if s < 35:
        if v < 40:
            return "black"
        if v > 210:
            return "white"
        return "gray"

    # OpenCV Hue scale: 0 to 180 degrees
    if (0 <= h <= 10) or (170 <= h <= 180):
        return "red"
    if 11 <= h <= 25:
        return "orange"
    if 26 <= h <= 35:
        return "yellow"
    if 36 <= h <= 85:
        return "green"
    if 86 <= h <= 102:
        return "cyan"
    if 103 <= h <= 135:
        return "blue"
    if 136 <= h <= 155:
        return "purple"
    if 156 <= h <= 169:
        return "magenta"

    return "other"


def sample_line_color(image: np.ndarray, hsv: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> str:
    samples = []
    length = int(np.hypot(x2 - x1, y2 - y1))
    steps = max(length, 1)

    # Sample a 3x3 pixel neighbourhood along the line to capture the line core
    for t in np.linspace(0.05, 0.95, min(steps, 60)):
        cx = int(x1 + t * (x2 - x1))
        cy = int(y1 + t * (y2 - y1))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= ny < hsv.shape[0] and 0 <= nx < hsv.shape[1]:
                    samples.append(hsv[ny, nx])

    if not samples:
        return "gray"

    # Filter out dark background pixels (V < 35)
    valid = [p for p in samples if p[2] >= 35]
    if not valid:
        valid = samples

    # Sort by saturation (S) and brightness (V) to pick line core pixels
    valid.sort(key=lambda p: (int(p[1]) * 2 + int(p[2])), reverse=True)
    top_samples = valid[:max(1, len(valid) // 3)]

    # Compute median HSV of top saturated line core samples
    median_hsv = np.median(top_samples, axis=0)
    return classify_pixel_color(median_hsv)


def compute_color_statistics(lines: list[dict], image_shape: tuple[int, int]) -> dict[str, Any]:
    h, w = image_shape
    total_area = h * w
    colors: dict[str, dict] = {}

    for line in lines:
        color = line.get("color", "other")
        if color not in colors:
            colors[color] = {
                "line_count": 0,
                "total_length": 0.0,
                "lengths": [],
                "widths": [],
                "pixel_count": 0,
                "horizontal_count": 0,
                "vertical_count": 0,
                "diagonal_count": 0,
                "curved_count": 0,
            }
        c = colors[color]
        c["line_count"] += 1
        c["total_length"] += line["length"]
        c["lengths"].append(line["length"])
        c["widths"].append(line["width"])
        c["pixel_count"] += int(line["length"] * max(line["width"], 1))
        orient = line.get("orientation", "diagonal")
        c[f"{orient}_count"] = c.get(f"{orient}_count", 0) + 1

    result = {}
    for name, stats in colors.items():
        lengths = stats["lengths"]
        widths = stats["widths"]
        result[name] = {
            "line_count": stats["line_count"],
            "total_length": round(stats["total_length"], 2),
            "average_length": round(safe_divide(stats["total_length"], len(lengths)), 2),
            "maximum_length": round(max(lengths) if lengths else 0, 2),
            "minimum_length": round(min(lengths) if lengths else 0, 2),
            "average_width": round(safe_divide(sum(widths), len(widths)), 2),
            "maximum_width": round(max(widths) if widths else 0, 2),
            "minimum_width": round(min(widths) if widths else 0, 2),
            "pixel_count": stats["pixel_count"],
            "area_percentage": round(safe_divide(stats["pixel_count"], total_area) * 100, 2),
            "screen_percentage": round(safe_divide(stats["pixel_count"], total_area) * 100, 2),
            "horizontal_count": stats.get("horizontal_count", 0),
            "vertical_count": stats.get("vertical_count", 0),
            "diagonal_count": stats.get("diagonal_count", 0),
            "curved_count": stats.get("curved_count", 0),
        }

    return result


def build_color_distribution(colors: dict) -> list[dict]:
    total = sum(c["pixel_count"] for c in colors.values()) or 1
    return [
        {"name": name, "value": round(stats["pixel_count"] / total * 100, 2), "count": stats["line_count"]}
        for name, stats in sorted(colors.items(), key=lambda x: -x[1]["pixel_count"])
    ]
