"""Generate clean, high-precision annotated overlay images."""

import base64
import cv2
import numpy as np


def encode_image_base64(image: np.ndarray, fmt: str = ".png") -> str:
    _, buffer = cv2.imencode(fmt, image)
    return base64.b64encode(buffer).decode("utf-8")


COLOR_NAME_TO_BGR = {
    "red": (50, 50, 255),
    "green": (50, 255, 100),
    "blue": (255, 150, 50),
    "cyan": (255, 255, 0),
    "magenta": (255, 0, 255),
    "purple": (255, 50, 200),
    "yellow": (0, 230, 255),
    "orange": (30, 160, 255),
    "white": (255, 255, 255),
    "black": (50, 50, 50),
    "gray": (180, 180, 180),
    "other": (50, 255, 100),
}


def create_annotated_overlay(
    processed: np.ndarray,
    lines: list[dict],
    intersections: list[dict],
    highlight_line_id: int | None = None,
) -> np.ndarray:
    overlay = processed.copy()

    # Draw detected true screen lines cleanly in their exact visual color
    for line in lines:
        color_name = str(line.get("color", "green")).lower()
        bgr_color = COLOR_NAME_TO_BGR.get(color_name, (50, 255, 100))
        thickness = max(2, min(int(line.get("width", 3)), 6))

        if highlight_line_id and line["id"] == highlight_line_id:
            # Highlight selected line with a bright neon outline
            cv2.line(overlay, (line["x1"], line["y1"]), (line["x2"], line["y2"]), (0, 255, 255), thickness + 4, cv2.LINE_AA)
            bgr_color = (255, 255, 255)

        # Draw clean line over the image
        cv2.line(overlay, (line["x1"], line["y1"]), (line["x2"], line["y2"]), bgr_color, thickness, cv2.LINE_AA)

    # Draw intersection points ONLY if genuine multiple lines intersect
    for ip in intersections:
        if ip.get("line_count", 0) >= 2:
            x, y = int(ip["x"]), int(ip["y"])
            cv2.circle(overlay, (x, y), 5, (0, 0, 255), -1, cv2.LINE_AA)

    return overlay


def create_damage_overlay(processed: np.ndarray, damage_mask: np.ndarray) -> np.ndarray:
    heat = cv2.applyColorMap(damage_mask, cv2.COLORMAP_JET)
    return cv2.addWeighted(processed, 0.7, heat, 0.3, 0)
