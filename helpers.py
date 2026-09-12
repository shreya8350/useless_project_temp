"""Shared utility helpers for the forensics pipeline."""

import hashlib
import json
import uuid
from typing import Any

import numpy as np


def generate_analysis_id() -> str:
    return str(uuid.uuid4())


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return float(max(low, min(high, value)))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator


def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-180 range for line orientation."""
    angle = angle % 180
    if angle < 0:
        angle += 180
    return angle


def classify_orientation(angle: float, straightness: float = 1.0) -> str:
    if straightness < 0.7:
        return "curved"
    if straightness < 0.85:
        return "irregular"

    angle = normalize_angle(angle)
    if angle <= 15 or angle >= 165:
        return "horizontal"
    if 75 <= angle <= 105:
        return "vertical"
    return "diagonal"


def region_from_point(x: float, y: float, width: int, height: int) -> str:
    col = 0 if x < width / 3 else (1 if x < 2 * width / 3 else 2)
    row = 0 if y < height / 3 else (1 if y < 2 * height / 3 else 2)
    names = [
        ["top-left", "top-center", "top-right"],
        ["mid-left", "center", "mid-right"],
        ["bot-left", "bot-center", "bot-right"],
    ]
    return names[row][col]


def to_serializable(obj: Any) -> Any:
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]
    return obj


def generate_display_dna_id(features: dict) -> str:
    payload = json.dumps(features, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode()).hexdigest()[:8].upper()
    return f"DPF-{digest[:4]}-{digest[4:8]}"


def histogram_bins(values: list[float], bins: int = 20) -> dict:
    if not values:
        return {"bins": [], "counts": []}
    arr = np.array(values, dtype=float)
    counts, edges = np.histogram(arr, bins=bins)
    centers = ((edges[:-1] + edges[1:]) / 2).tolist()
    return {"bins": [round(c, 2) for c in centers], "counts": counts.tolist()}


def angle_bucket(angle: float) -> str:
    angle = normalize_angle(angle)
    if angle == 0 or angle >= 179.5:
        return "0°"
    if angle <= 15:
        return "1–15°"
    if angle <= 30:
        return "15–30°"
    if angle <= 45:
        return "30–45°"
    if angle <= 60:
        return "45–60°"
    if angle <= 75:
        return "60–75°"
    if angle <= 89:
        return "75–89°"
    return "90°"
