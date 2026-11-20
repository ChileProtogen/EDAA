import math
import os
import random


def save_points(path, points):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for x, y in points:
            f.write(f"{x:.6f},{y:.6f}\n")


def gen_uniform(n, scale=1000.0, rng=None):
    rng = rng or random.Random(42)
    return [[rng.uniform(0, scale), rng.uniform(0, scale)] for _ in range(n)]


def gen_circle(n, radius=500.0, cx=500.0, cy=500.0, jitter=0.0, rng=None):
    rng = rng or random.Random(43)
    pts = []
    for i in range(n):
        angle = (2.0 * math.pi * i) / n
        r = radius + (rng.uniform(-jitter, jitter) if jitter > 0 else 0.0)
        pts.append([cx + r * math.cos(angle), cy + r * math.sin(angle)])
    return pts


def gen_clusters(n, num_clusters=6, spread=25.0, scale=1000.0, rng=None):
    rng = rng or random.Random(44)
    centers = [[rng.uniform(100, scale - 100), rng.uniform(100, scale - 100)] for _ in range(num_clusters)]
    pts = []
    for i in range(n):
        c = centers[i % num_clusters]
        pts.append([c[0] + rng.gauss(0, spread), c[1] + rng.gauss(0, spread)])
    return pts


def gen_collinear(n, scale=1000.0, rng=None):
    rng = rng or random.Random(45)
    pts = []
    # Recta base con muchos puntos colineales
    line_count = int(n * 0.6)
    for _ in range(line_count):
        t = rng.uniform(0.05, 0.95)
        x = t * scale
        y = 0.5 * x + 100.0
        pts.append([x, y])

    # Resto de puntos distribuidos alrededor
    for _ in range(n - line_count):
        pts.append([rng.uniform(0, scale), rng.uniform(0, scale)])
    return pts


def main():
    out_dir = "datasets"
    datasets = {
        "uniforme_2000.txt": gen_uniform(2000),
        "circulo_1500.txt": gen_circle(1500, jitter=0.0),
        "clusters_3000.txt": gen_clusters(3000),
        "colineales_1500.txt": gen_collinear(1500),
        "grande_50000.txt": gen_uniform(50000, rng=random.Random(46)),
    }

    for name, pts in datasets.items():
        path = os.path.join(out_dir, name)
        save_points(path, pts)
        print(f"Generado {path} ({len(pts)} puntos)")


if __name__ == "__main__":
    main()