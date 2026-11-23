import sys
import matplotlib.pyplot as plt
from monotone_chain import monotone_chain

# EJEMPLO DE USO: python .\visual_monotone.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos.

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


def plot_monotone(points, title_extra=""):
    hull = monotone_chain(points) if len(points) >= 3 else []

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
            color="tomato",
            alpha=0.15,
            zorder=1,
        )
        ax.plot(
            [p[0] for p in closed],
            [p[1] for p in closed],
            color="tomato",
            linewidth=2,
            label="Convex Hull (Monotone Chain)",
            zorder=3,
        )
        ax.scatter(
            [p[0] for p in hull],
            [p[1] for p in hull],
            color="tomato",
            s=70,
            zorder=4,
        )
        ax.set_title(f"Monotone Chain - {len(hull)} vertices de {len(points)} puntos{title_extra}")
    else:
        ax.set_title(f"Monotone Chain - Sin convex hull ({len(points)} puntos){title_extra}")

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
        pts = [[0, 3], [2, 2], [1, 1], [2, 1], [3, 0], [0, 0], [3, 3], [1.5, 1.5]]
        extra = " [ejemplo]"
    plot_monotone(pts, extra)