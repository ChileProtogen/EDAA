import sys
import matplotlib.pyplot as plt
from jarvismarch import jarvis_march

# EJEMPLO DE USO: python .\visual_jarvis.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos.

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


def plot_jarvis(points, title_extra=""):
    hull = jarvis_march(points) if len(points) >= 3 else []

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
        closed = list(hull) + [hull[0]]
        ax.fill(
            [p[0] for p in closed],
            [p[1] for p in closed],
            color="darkorange",
            alpha=0.15,
            zorder=1,
        )
        ax.plot(
            [p[0] for p in closed],
            [p[1] for p in closed],
            color="darkorange",
            linewidth=2,
            label="Convex Hull (Jarvis March)",
            zorder=3,
        )
        ax.scatter(
            [p[0] for p in hull],
            [p[1] for p in hull],
            color="darkorange",
            s=70,
            zorder=4,
        )
        ax.set_title(f"Jarvis March - {len(hull)} vertices de {len(points)} puntos{title_extra}")
    else:
        ax.set_title(f"Jarvis March - Sin convex hull ({len(points)} puntos){title_extra}")

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
        pts = [[0, 3], [2, 2], [1, 1], [2, 1], [3, 0], [0, 0], [3, 3]]
        extra = " [ejemplo]"
    plot_jarvis(pts, extra)