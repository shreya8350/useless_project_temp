"""Display DNA™ fingerprint generation."""

import hashlib

from backend.utils.helpers import generate_display_dna_id


def generate_display_dna(
    colors: dict,
    line_stats: dict,
    pixels: dict,
    intersections: dict,
    curves: dict,
    uselessness: dict,
) -> dict:
    features = {
        "color_keys": sorted(colors.keys()),
        "color_weights": [round(colors[k]["area_percentage"], 1) for k in sorted(colors.keys())],
        "orientations": [
            line_stats.get("horizontal", 0),
            line_stats.get("vertical", 0),
            line_stats.get("diagonal", 0),
            line_stats.get("curved", 0),
        ],
        "damage": pixels.get("damage_percentage", 0),
        "intersections": intersections.get("total", 0),
        "curvature": curves.get("average_curvature", 0),
        "uselessness": uselessness.get("score", 0),
    }

    dna_id = generate_display_dna_id(features)

    # Generate barcode-like pattern from hash
    digest = hashlib.sha256(str(features).encode()).hexdigest()
    bars = []
    for i in range(0, min(len(digest), 64), 2):
        val = int(digest[i : i + 2], 16)
        bars.append({"height": (val % 80) + 20, "color": f"#{digest[i:i+6] if i+6 <= len(digest) else digest[:6]}"})

    return {
        "id": dna_id,
        "features": features,
        "barcode": bars,
    }


def build_line_social_network(lines: list[dict], intersections: list[dict]) -> dict:
    nodes = [{"id": l["id"], "label": f"L{l['id']}", "connections": 0} for l in lines]
    edges = []
    edge_set = set()

    for ip in intersections:
        ids = ip["line_ids"]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = min(ids[i], ids[j]), max(ids[i], ids[j])
                if (a, b) not in edge_set:
                    edge_set.add((a, b))
                    edges.append({"source": a, "target": b, "type": "intersection"})

    for i, li in enumerate(lines):
        for lj in lines[i + 1:]:
            if li["id"] > lj["id"]:
                li, lj = lj, li
            if lj["nearest_line_distance"] < 15:
                key = (li["id"], lj["id"])
                if key not in edge_set:
                    edge_set.add(key)
                    edges.append({"source": li["id"], "target": lj["id"], "type": "proximity"})
            angle_diff = abs(li["angle"] - lj["angle"])
            angle_diff = min(angle_diff, 180 - angle_diff)
            if angle_diff < 5 and lj["nearest_line_distance"] < 50:
                key = (li["id"], lj["id"])
                if key not in edge_set:
                    edge_set.add(key)
                    edges.append({"source": li["id"], "target": lj["id"], "type": "parallel"})

    connection_counts = {l["id"]: 0 for l in lines}
    for e in edges:
        connection_counts[e["source"]] = connection_counts.get(e["source"], 0) + 1
        connection_counts[e["target"]] = connection_counts.get(e["target"], 0) + 1

    for n in nodes:
        n["connections"] = connection_counts.get(n["id"], 0)

    most_connected = max(nodes, key=lambda n: n["connections"]) if nodes else None
    most_isolated = min(nodes, key=lambda n: n["connections"]) if nodes else None

    # Simple community count via connected components
    adj: dict[int, set] = {l["id"]: set() for l in lines}
    for e in edges:
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])

    visited = set()
    communities = 0
    for lid in adj:
        if lid in visited:
            continue
        stack = [lid]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            stack.extend(adj[node] - visited)
        communities += 1

    largest_group = max(connection_counts.values()) if connection_counts else 0

    return {
        "title": "THE SOCIAL LIFE OF BROKEN PIXELS",
        "nodes": nodes,
        "edges": edges,
        "most_connected_line": most_connected["id"] if most_connected else None,
        "most_isolated_line": most_isolated["id"] if most_isolated else None,
        "largest_connected_group": largest_group,
        "community_count": communities,
    }
