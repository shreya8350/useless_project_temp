"""Symmetry score calculation."""

import cv2
import numpy as np

from backend.utils.helpers import clamp, safe_divide


def calculate_symmetry(damage_mask: np.ndarray) -> dict:
    h, w = damage_mask.shape
    mask = (damage_mask > 0).astype(np.uint8)

    left = mask[:, : w // 2]
    right = cv2.flip(mask[:, w - w // 2 :], 1)
    min_w = min(left.shape[1], right.shape[1])
    h_sym = safe_divide(np.sum(left[:, :min_w] == right[:, :min_w]), left[:, :min_w].size) * 100

    top = mask[: h // 2, :]
    bottom = cv2.flip(mask[h - h // 2 :, :], 0)
    min_h = min(top.shape[0], bottom.shape[0])
    v_sym = safe_divide(np.sum(top[:min_h, :] == bottom[:min_h, :]), top[:min_h, :].size) * 100

    flipped_h = cv2.flip(mask, 1)
    flipped_v = cv2.flip(mask, 0)
    flipped_both = cv2.flip(mask, -1)

    horizontal_sym = safe_divide(np.sum(mask == flipped_h), mask.size) * 100
    vertical_sym = safe_divide(np.sum(mask == flipped_v), mask.size) * 100
    central_sym = safe_divide(np.sum(mask == flipped_both), mask.size) * 100

    overall = clamp((h_sym + v_sym + horizontal_sym + vertical_sym + central_sym) / 5, 0, 100)

    return {
        "score": round(overall, 1),
        "left_vs_right": round(h_sym, 1),
        "top_vs_bottom": round(v_sym, 1),
        "horizontal_symmetry": round(horizontal_sym, 1),
        "vertical_symmetry": round(vertical_sym, 1),
        "central_symmetry": round(central_sym, 1),
    }


def calculate_breakage_level(pixels: dict, line_stats: dict, colors: dict, chaos: dict) -> dict:
    damage = min(pixels.get("damage_percentage", 0) / 40, 1.0)
    line_factor = min(line_stats.get("total", 0) / 150, 1.0)
    cluster_factor = min(pixels.get("cluster_count", 0) / 80, 1.0)
    color_factor = min(len(colors) / 6, 1.0)
    pattern_factor = min(chaos.get("score", 0) / 100, 1.0)

    raw = (damage * 3 + line_factor * 2 + cluster_factor * 1.5 + color_factor + pattern_factor * 1.5) / 9 * 10
    level = max(1, min(10, round(raw)))

    descriptions = {
        1: "Barely broken",
        2: "Slightly suspicious",
        3: "Something happened",
        4: "Definitely damaged",
        5: "Concerning",
        6: "Very concerning",
        7: "Technically struggling",
        8: "Extremely broken",
        9: "Almost abstract art",
        10: "Congratulations",
    }

    return {
        "level": int(level),
        "max": 10,
        "description": descriptions[int(level)],
        "disclaimer": "Custom experimental metric based on image-derived visual anomalies.",
    }
