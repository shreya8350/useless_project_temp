"""Abnormal pixel and cluster detection."""

from typing import Any

import cv2
import numpy as np

from backend.cv.color_analysis import classify_pixel_color
from backend.utils.helpers import safe_divide


def build_damage_mask(gray: np.ndarray, lines: list[dict]) -> np.ndarray:
    h, w = gray.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    diff = cv2.absdiff(gray, blurred)
    _, abnormal = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)

    edges = cv2.Canny(blurred, 30, 90)
    mask = cv2.bitwise_or(abnormal, edges)

    for line in lines:
        cv2.line(mask, (line["x1"], line["y1"]), (line["x2"], line["y2"]), 255, max(int(line["width"]), 2))

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.dilate(mask, kernel, iterations=1)
    return mask


def detect_pixel_clusters(gray: np.ndarray, hsv: np.ndarray, damage_mask: np.ndarray) -> dict[str, Any]:
    h, w = gray.shape
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(damage_mask, connectivity=8)

    clusters = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 2:
            continue
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]
        cx, cy = centroids[i]

        region_mask = (labels == i).astype(np.uint8)
        mean_hsv = cv2.mean(hsv, mask=region_mask)[:3]
        color = classify_pixel_color(np.array(mean_hsv))

        if area == 1:
            cluster_type = "isolated"
        elif area < 20:
            cluster_type = "small"
        elif area < 100:
            cluster_type = "medium"
        else:
            cluster_type = "large"

        aspect = max(bw, bh) / (min(bw, bh) + 1)
        if aspect > 4:
            shape = "line-shaped"
        elif aspect < 1.5 and area > 20:
            shape = "block-shaped"
        elif cluster_type == "large":
            shape = "irregular"
        else:
            shape = "irregular"

        clusters.append({
            "id": i,
            "area": int(area),
            "x": int(x), "y": int(y),
            "width": int(bw), "height": int(bh),
            "centroid_x": round(float(cx), 2),
            "centroid_y": round(float(cy), 2),
            "color": color,
            "type": cluster_type,
            "shape": shape,
        })

    type_counts = {"isolated": 0, "small": 0, "medium": 0, "large": 0}
    for c in clusters:
        type_counts[c["type"]] += 1

    areas = [c["area"] for c in clusters]
    total_abnormal = int(np.sum(damage_mask > 0))
    total_pixels = h * w

    return {
        "estimated_abnormal_pixels": total_abnormal,
        "cluster_count": len(clusters),
        "clusters": clusters,
        "largest_cluster": max(areas) if areas else 0,
        "smallest_cluster": min(areas) if areas else 0,
        "average_cluster_size": round(safe_divide(sum(areas), len(areas)), 2),
        "cluster_density": round(safe_divide(len(clusters), total_pixels) * 10000, 4),
        "type_distribution": type_counts,
        "damage_percentage": round(safe_divide(total_abnormal, total_pixels) * 100, 2),
        "unaffected_percentage": round(100 - safe_divide(total_abnormal, total_pixels) * 100, 2),
        "damage_mask": damage_mask,
    }


def compute_intensity_histogram(gray: np.ndarray, damage_mask: np.ndarray, bins: int = 30) -> dict:
    pixels = gray[damage_mask > 0]
    if len(pixels) == 0:
        return {"bins": list(range(0, 256, 256 // bins)), "counts": [0] * bins}
    counts, edges = np.histogram(pixels, bins=bins, range=(0, 256))
    centers = ((edges[:-1] + edges[1:]) / 2).astype(int).tolist()
    return {"bins": centers, "counts": counts.tolist()}
