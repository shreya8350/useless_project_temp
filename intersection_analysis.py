"""Line intersection detection and analysis."""

from typing import Any

import numpy as np

from backend.utils.helpers import normalize_angle


def _line_intersection(l1: dict, l2: dict, tol: float = 8.0) -> tuple[float, float] | None:
    x1, y1, x2, y2 = l1["x1"], l1["y1"], l1["x2"], l1["y2"]
    x3, y3, x4, y4 = l2["x1"], l2["y1"], l2["x2"], l2["y2"]

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-6:
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    def on_segment(xa, ya, xb, yb, xp, yp):
        return (min(xa, xb) - tol <= xp <= max(xa, xb) + tol and
                min(ya, yb) - tol <= yp <= max(ya, yb) + tol)

    if on_segment(x1, y1, x2, y2, px, py) and on_segment(x3, y3, x4, y4, px, py):
        return (px, py)
    return None


def analyze_intersections(lines: list[dict], width: int, height: int) -> dict[str, Any]:
    intersections_map: dict[tuple, list[int]] = {}
    pairs = []

    straight_lines = [l for l in lines if l.get("orientation") not in ("curved", "irregular") or not l.get("is_contour")]

    for i in range(len(straight_lines)):
        for j in range(i + 1, len(straight_lines)):
            pt = _line_intersection(straight_lines[i], straight_lines[j])
            if pt is None:
                continue
            key = (round(pt[0], 1), round(pt[1], 1))
            if key not in intersections_map:
                intersections_map[key] = []
            if straight_lines[i]["id"] not in intersections_map[key]:
                intersections_map[key].append(straight_lines[i]["id"])
            if straight_lines[j]["id"] not in intersections_map[key]:
                intersections_map[key].append(straight_lines[j]["id"])
            pairs.append((straight_lines[i]["id"], straight_lines[j]["id"], pt))

    intersection_points = []
    for (x, y), line_ids in intersections_map.items():
        angles = []
        for lid in line_ids:
            line = next(l for l in lines if l["id"] == lid)
            angles.append(line["angle"])
        angle_between = 0.0
        if len(angles) >= 2:
            angle_between = abs(angles[0] - angles[1])
            angle_between = min(angle_between, 180 - angle_between)

        intersection_points.append({
            "x": round(x, 2),
            "y": round(y, 2),
            "line_ids": line_ids,
            "line_count": len(line_ids),
            "angle_between": round(angle_between, 2),
        })

    for line in lines:
        count = sum(1 for ip in intersection_points if line["id"] in ip["line_ids"])
        line["intersections"] = count

    two_line = sum(1 for ip in intersection_points if ip["line_count"] == 2)
    multi_line = sum(1 for ip in intersection_points if ip["line_count"] > 2)

    return {
        "total": len(intersection_points),
        "two_line_intersections": two_line,
        "multi_line_intersections": multi_line,
        "points": intersection_points,
        "message": f"{len(intersection_points)} unnecessary intersections detected.",
    }


def detect_parallel_groups(lines: list[dict], angle_tol: float = 5, spacing_tol: float = 20) -> dict[str, Any]:
    straight = [l for l in lines if l["orientation"] in ("horizontal", "vertical", "diagonal")]
    groups = []
    used = set()

    for i, li in enumerate(straight):
        if li["id"] in used:
            continue
        group = [li["id"]]
        used.add(li["id"])
        for lj in straight[i + 1:]:
            if lj["id"] in used:
                continue
            angle_diff = abs(li["angle"] - lj["angle"])
            angle_diff = min(angle_diff, 180 - angle_diff)
            if angle_diff > angle_tol:
                continue
            mx_i = (li["x1"] + li["x2"]) / 2
            my_i = (li["y1"] + li["y2"]) / 2
            mx_j = (lj["x1"] + lj["x2"]) / 2
            my_j = (lj["y1"] + lj["y2"]) / 2
            spacing = np.hypot(mx_i - mx_j, my_i - my_j)
            if spacing < spacing_tol * 5:
                group.append(lj["id"])
                used.add(lj["id"])
        if len(group) >= 2:
            groups.append(group)

    spacings = []
    for group in groups:
        if len(group) >= 2:
            lines_in_group = [l for l in straight if l["id"] in group]
            for a in range(len(lines_in_group)):
                for b in range(a + 1, len(lines_in_group)):
                    la, lb = lines_in_group[a], lines_in_group[b]
                    spacings.append(np.hypot(
                        (la["x1"] + la["x2"]) / 2 - (lb["x1"] + lb["x2"]) / 2,
                        (la["y1"] + la["y2"]) / 2 - (lb["y1"] + lb["y2"]) / 2,
                    ))

    largest_group = max((len(g) for g in groups), default=0)
    return {
        "parallel_group_count": len(groups),
        "group_sizes": [len(g) for g in groups],
        "average_spacing": round(float(np.mean(spacings)), 2) if spacings else 0,
        "most_common_spacing": round(float(np.median(spacings)), 2) if spacings else 0,
        "most_organized_damage": f"{largest_group} lines appear to have coordinated their direction." if largest_group >= 2 else "No coordinated damage detected.",
        "largest_group_size": largest_group,
    }
