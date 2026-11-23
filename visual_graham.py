import math
import sys
import matplotlib.pyplot as plt
from graham_scan import findConvexHull as graham_scan

# EJEMPLO DE USO: python .\visual_graham.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos.

def read_points(path):
    points = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.replace(";", ",").split(",")
            if len(parts) >= 2:
                points.append([float(parts[0]), float(parts[1])])
    return points


def order_ccw(hull_points):
    cx = sum(p[0] for p in hull_points) / len(hull_points)
    cy = sum(p[1] for p in hull_points) / len(hull_points)
    return sorted(hull_points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def plot_graham(points, title_extra=""):
    raw_hull = graham_scan(points) if len(points) >= 3 else []
    hull = []
    if raw_hull and not (len(raw_hull) == 1 and len(raw_hull[0]) == 1 and raw_hull[0][0] == -1):
        hull = order_ccw(raw_hull)

    fig, ax = plt.subplots(figsize=(8, 6))
    if points:
        ax.scatter(
            [p[0] for p in points],
            [p[1] for p in points],
            color="steelblue",
            label="Puntos",
            zorder=2,
        )

    if len(hull) >= 3:
        closed = hull + [hull[0]]
        ax.fill(
            [p[0] for p in closed],
            [p[1] for p in closed],
            color="seagreen",
            alpha=0.15,
            zorder=1,
        )
        ax.plot(
            [p[0] for p in closed],
            [p[1] for p in closed],
            color="seagreen",
            linewidth=2,
            label="Convex Hull (Graham Scan)",
            zorder=3,
        )
        ax.scatter(
            [p[0] for p in hull],
            [p[1] for p in hull],
            color="seagreen",
            s=70,
            zorder=4,
        )
        ax.set_title(f"Graham Scan - {len(hull)} vertices de {len(points)} puntos{title_extra}")
    else:
        ax.set_title(f"Graham Scan - Sin convex hull ({len(points)} puntos){title_extra}")

    ax.set_aspect("equal", adjustable="datalim")
    if points:
        ax.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pts = read_points(sys.argv[1])
        extra = f" [{sys.argv[1]}]"
    else:
        pts = [
            [0, 0], [1, -4], [-1, -5], [-5, -3], [-3, -1],
            [-1, -3], [-2, -2], [-1, -1], [-2, -1], [-1, 1],
        ]
        extra = " [ejemplo]"
    plot_graham(pts, extra)