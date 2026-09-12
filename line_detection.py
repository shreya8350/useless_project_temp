"""High-precision screen line detection and measurement pipeline."""

from typing import Any
import cv2
import numpy as np

from backend.cv.color_analysis import sample_line_color
from backend.utils.helpers import classify_orientation, normalize_angle, region_from_point, safe_divide


def _measure_line_width(gray: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> float:
    length = np.hypot(x2 - x1, y2 - y1)
    if length < 1:
        return 1.0

    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = (x2 - x1) / length, (y2 - y1) / length
    px, py = -dy, dx

    widths = []
    for dist in range(-15, 16):
        sx = int(mx + px * dist)
        sy = int(my + py * dist)
        if 0 <= sy < gray.shape[0] and 0 <= sx < gray.shape[1]:
            val = gray[sy, sx]
            if val < 200:
                widths.append(abs(dist))

    if not widths:
        return 2.0
    return max(1.0, min(np.percentile(widths, 75) * 2, 20.0))


def _merge_similar_lines(lines: list[tuple], angle_thresh: float = 8, dist_thresh: float = 25) -> list[tuple]:
    if not lines:
        return []
    merged = []
    used = [False] * len(lines)

    for i, l1 in enumerate(lines):
        if used[i]:
            continue
        x1, y1, x2, y2 = l1
        group = [l1]
        used[i] = True
        a1 = normalize_angle(np.degrees(np.arctan2(y2 - y1, x2 - x1)))

        for j, l2 in enumerate(lines):
            if used[j] or i == j:
                continue
            x3, y3, x4, y4 = l2
            a2 = normalize_angle(np.degrees(np.arctan2(y4 - y3, x4 - x3)))
            if abs(a1 - a2) > angle_thresh and abs(a1 - a2) < (180 - angle_thresh):
                continue
            mid_dist = np.hypot((x1 + x2) / 2 - (x3 + x4) / 2, (y1 + y2) / 2 - (y3 + y4) / 2)
            if mid_dist < dist_thresh:
                group.append(l2)
                used[j] = True

        all_pts = [(g[0], g[1]) for g in group] + [(g[2], g[3]) for g in group]
        pts = np.array(all_pts)
        if len(pts) >= 2:
            res = cv2.fitLine(pts.astype(np.float32), cv2.DIST_L2, 0, 0.01, 0.01)
            vx, vy, cx, cy = [float(np.ravel(v)[0]) for v in res]
            projections = [(p[0] - cx) * vx + (p[1] - cy) * vy for p in pts]
            t_min, t_max = float(min(projections)), float(max(projections))
            nx1 = int(cx + t_min * vx)
            ny1 = int(cy + t_min * vy)
            nx2 = int(cx + t_max * vx)
            ny2 = int(cy + t_max * vy)
            merged.append((nx1, ny1, nx2, ny2))
        else:
            merged.append(l1)

    return merged


def detect_saturated_screen_lines(processed: np.ndarray, hsv: np.ndarray) -> list[tuple]:
    """Detect bright, saturated screen damage lines (green OLED line of death, pink/magenta, cyan, etc.)."""
    h, w = processed.shape[:2]
    min_length = int(max(h, w) * 0.35)  # Must span at least 35% of screen — keeps only prominent lines

    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]

    # Saturated screen colors — tighter thresholds to avoid faint background hues
    sat_mask = (s_channel >= 80) & (v_channel >= 100)
    bright_mask = (v_channel >= 230) & (s_channel < 30)  # Intense laser-like white lines only

    damage_mask = (sat_mask | bright_mask).astype(np.uint8) * 255

    # Directional morphology to link line segments
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 19))
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (19, 1))

    linked_v = cv2.morphologyEx(damage_mask, cv2.MORPH_CLOSE, kernel_v)
    linked_h = cv2.morphologyEx(damage_mask, cv2.MORPH_CLOSE, kernel_h)
    linked = cv2.bitwise_or(linked_v, linked_h)

    raw = cv2.HoughLinesP(
        linked,
        rho=1,
        theta=np.pi / 180,
        threshold=80,          # raised from 35 — require more votes
        minLineLength=min_length,
        maxLineGap=15,         # tighter gap — don't bridge distant segments
    )

    if raw is None:
        return []

    lines = [tuple(map(int, np.array(l).flatten())) for l in raw]
    lines = [l for l in lines if len(l) == 4]
    return _merge_similar_lines(lines, angle_thresh=4, dist_thresh=15)


def detect_hough_lines_fallback(processed: np.ndarray, gray: np.ndarray) -> list[tuple]:
    """Fallback detector — only the most visible continuous lines survive."""
    h, w = gray.shape[:2]
    min_length = int(max(h, w) * 0.40)  # Must cross at least 40% of the screen

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 120, 240, apertureSize=3)  # higher thresholds = fewer, stronger edges

    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 9))
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    v_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_v)
    h_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_h)
    enhanced = cv2.bitwise_or(v_lines, h_lines)

    raw = cv2.HoughLinesP(
        enhanced,
        rho=1,
        theta=np.pi / 180,
        threshold=100,         # raised from 55 — needs strong evidence
        minLineLength=min_length,
        maxLineGap=10,         # almost no gap allowed
    )
    if raw is None:
        return []

    lines = [tuple(map(int, np.array(l).flatten())) for l in raw]
    lines = [l for l in lines if len(l) == 4]
    return _merge_similar_lines(lines, angle_thresh=3, dist_thresh=12)


def build_line_records(
    processed: np.ndarray,
    gray: np.ndarray,
    hsv: np.ndarray,
    hough_lines: list[tuple],
) -> list[dict]:
    h, w = gray.shape[:2]
    cx, cy = w / 2, h / 2
    diagonal = np.hypot(w, h)
    records = []
    line_id = 1

    for x1, y1, x2, y2 in hough_lines:
        length = float(np.hypot(x2 - x1, y2 - y1))
        if length < 15:
            continue
        angle = normalize_angle(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        width = _measure_line_width(gray, x1, y1, x2, y2)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        color = sample_line_color(processed, hsv, x1, y1, x2, y2)
        brightness = float(np.mean([gray[min(max(y1, 0), h - 1), min(max(x1, 0), w - 1)],
                                    gray[min(max(y2, 0), h - 1), min(max(x2, 0), w - 1)]]))

        records.append({
            "id": line_id,
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "length": round(length, 2),
            "width": round(width, 2),
            "angle": round(angle, 2),
            "orientation": classify_orientation(angle, 1.0),
            "color": color,
            "brightness": round(brightness, 2),
            "intensity": round(255 - brightness, 2),
            "straightness": 1.0,
            "screen_percentage": round(length / diagonal * 100, 4),
            "distance_from_center": round(np.hypot(mx - cx, my - cy), 2),
            "region": region_from_point(mx, my, w, h),
            "intersections": 0,
            "nearest_line_distance": 999.0,
            "is_contour": False,
        })
        line_id += 1

    _compute_line_proximity(records)
    return records


def _compute_line_proximity(lines: list[dict]) -> None:
    for i, li in enumerate(lines):
        mx_i = (li["x1"] + li["x2"]) / 2
        my_i = (li["y1"] + li["y2"]) / 2
        min_dist = float("inf")
        for j, lj in enumerate(lines):
            if i == j:
                continue
            mx_j = (lj["x1"] + lj["x2"]) / 2
            my_j = (lj["y1"] + lj["y2"]) / 2
            d = np.hypot(mx_i - mx_j, my_i - my_j)
            min_dist = min(min_dist, d)
        li["nearest_line_distance"] = round(min_dist if min_dist != float("inf") else 999.0, 2)


def compute_line_statistics(lines: list[dict], image_shape: tuple[int, int]) -> dict[str, Any]:
    h, w = image_shape
    if not lines:
        return {
            "total": 0, "horizontal": 0, "vertical": 0, "diagonal": 0,
            "curved": 0, "irregular": 0, "longest": 0, "shortest": 0,
            "thickest": 0, "thinnest": 0, "average_length": 0, "average_width": 0,
            "median_width": 0, "average_angle": 0, "angle_variance": 0, "line_density": 0,
        }

    orientations = [l["orientation"] for l in lines]
    lengths = [l["length"] for l in lines]
    widths = [l["width"] for l in lines]
    angles = [l["angle"] for l in lines]
    area = h * w

    return {
        "total": len(lines),
        "horizontal": orientations.count("horizontal"),
        "vertical": orientations.count("vertical"),
        "diagonal": orientations.count("diagonal"),
        "curved": orientations.count("curved"),
        "irregular": orientations.count("irregular"),
        "longest": round(max(lengths), 2),
        "shortest": round(min(lengths), 2),
        "thickest": round(max(widths), 2),
        "thinnest": round(min(widths), 2),
        "average_length": round(np.mean(lengths), 2),
        "average_width": round(np.mean(widths), 2),
        "median_width": round(float(np.median(widths)), 2),
        "average_angle": round(float(np.mean(angles)), 2),
        "angle_variance": round(float(np.var(angles)), 2),
        "line_density": round(sum(lengths) / area * 10000, 4),
    }


def detect_lines(processed: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> tuple[list[dict], dict]:
    # 1. Try High-Precision Saturated Screen Line Detector first (OLED green lines, pink lines, cyan lines)
    sat_lines = detect_saturated_screen_lines(processed, hsv)
    if sat_lines:
        lines = build_line_records(processed, gray, hsv, sat_lines)
    else:
        # 2. Fallback with strict noise suppression
        hough = detect_hough_lines_fallback(processed, gray)
        lines = build_line_records(processed, gray, hsv, hough)

    stats = compute_line_statistics(lines, gray.shape)
    return lines, stats
