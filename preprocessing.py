"""Image preprocessing for display forensics."""

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


MAX_ANALYSIS_DIM = 1280


@dataclass
class PreprocessedImage:
    original: np.ndarray
    processed: np.ndarray
    display_region: tuple[int, int, int, int]  # x, y, w, h
    scale_factor: float
    gray: np.ndarray
    hsv: np.ndarray
    lab: np.ndarray


def load_image_from_bytes(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image. File may be corrupted.")
    return image


def resize_for_analysis(image: np.ndarray, max_dim: int = MAX_ANALYSIS_DIM) -> tuple[np.ndarray, float]:
    h, w = image.shape[:2]
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image, scale


def detect_display_region(image: np.ndarray) -> tuple[int, int, int, int]:
    """Estimate display rectangle using edges and largest contour."""
    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 40, 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return 0, 0, w, h

    best = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(best)
    if area < 0.1 * h * w:
        return 0, 0, w, h

    x, y, bw, bh = cv2.boundingRect(best)
    pad_x = int(bw * 0.02)
    pad_y = int(bh * 0.02)
    x = max(0, x - pad_x)
    y = max(0, y - pad_y)
    bw = min(w - x, bw + 2 * pad_x)
    bh = min(h - y, bh + 2 * pad_y)
    return x, y, bw, bh


def apply_crop(image: np.ndarray, crop: Optional[dict]) -> np.ndarray:
    if not crop:
        return image
    h, w = image.shape[:2]
    x = int(crop.get("x", 0))
    y = int(crop.get("y", 0))
    cw = int(crop.get("width", w))
    ch = int(crop.get("height", h))
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))
    cw = max(1, min(cw, w - x))
    ch = max(1, min(ch, h - y))
    return image[y : y + ch, x : x + cw]


def perspective_correct(image: np.ndarray) -> np.ndarray:
    """Attempt mild perspective correction if a quadrilateral display is found."""
    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image

    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 0.15 * h * w:
        return image

    peri = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.02 * peri, True)
    if len(approx) != 4:
        return image

    pts = approx.reshape(4, 2).astype(np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]
    src = np.array([tl, tr, br, bl], dtype=np.float32)

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_w = int(max(width_a, width_b))
    max_h = int(max(height_a, height_b))
    if max_w < 50 or max_h < 50:
        return image

    dst = np.array([[0, 0], [max_w - 1, 0], [max_w - 1, max_h - 1], [0, max_h - 1]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(image, matrix, (max_w, max_h))


def denoise_and_normalize(image: np.ndarray) -> np.ndarray:
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 6, 6, 7, 21)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    merged = cv2.merge([l, a, b])
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def preprocess_image(
    data: bytes,
    crop: Optional[dict] = None,
    apply_perspective: bool = True,
) -> PreprocessedImage:
    original = load_image_from_bytes(data)
    if original.shape[0] < 32 or original.shape[1] < 32:
        raise ValueError("Image too small for analysis. Minimum 32×32 pixels required.")

    working = original.copy()
    working = apply_crop(working, crop)
    if apply_perspective:
        working = perspective_correct(working)

    resized, scale = resize_for_analysis(working)
    display_region = detect_display_region(resized)
    x, y, rw, rh = display_region
    cropped = resized[y : y + rh, x : x + rw]
    processed = denoise_and_normalize(cropped)

    gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)

    return PreprocessedImage(
        original=original,
        processed=processed,
        display_region=(0, 0, processed.shape[1], processed.shape[0]),
        scale_factor=scale,
        gray=gray,
        hsv=hsv,
        lab=lab,
    )
