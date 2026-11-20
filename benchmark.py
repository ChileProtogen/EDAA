import csv
import glob
import os
import statistics
import time

from convex_hull import findConvexHull, readPoints
from jarvismarch import jarvis_march
from monotone_chain import monotone_chain

# Evita que Fuerza Bruta (O(n^3)) bloquee el benchmark en datasets grandes
MAX_BRUTE_FORCE_N = 1500
REPEATS = 5


def measure(func, points, repeats=REPEATS):
    times_ms = []
    hull_len = None

    for _ in range(repeats):
        # Copia defensiva por si algún algoritmo muta su lista interna
        data_copy = [[p[0], p[1]] for p in points]
        t0 = time.perf_counter()
        res = func(data_copy)
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000.0)
        hull_len = len(res) if res is not None else 0

    mean_ms = statistics.mean(times_ms)
    stdev_ms = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
    return mean_ms, stdev_ms, hull_len


def run_benchmarks(dataset_paths, output_csv="resultados_benchmark.csv"):
    algorithms = [
        ("Fuerza Bruta", findConvexHull, MAX_BRUTE_FORCE_N),
        ("Jarvis March", jarvis_march, None),
        ("Monotone Chain", monotone_chain, None),
    ]

    rows = []

    for path in sorted(dataset_paths):
        points = readPoints(path)
        n = len(points)
        ds_name = os.path.basename(path)
        print(f"\n=== Dataset: {ds_name} (N = {n}) ===")

        for alg_name, func, max_n in algorithms:
            if max_n is not None and n > max_n:
                print(f"  - {alg_name:<15}: omitido (N={n} > límite {max_n} para O(N^3))")
                rows.append({
                    "dataset": ds_name,
                    "n_puntos": n,
                    "algoritmo": alg_name,
                    "repeticiones": 0,
                    "tiempo_promedio_ms": "",
                    "desv_std_ms": "",
                    "vertices_hull": "",
                    "nota": f"Omitido por superar N={max_n}",
                })
                continue

            mean_ms, std_ms, hull_len = measure(func, points)
            print(
                f"  - {alg_name:<15}: {mean_ms:10.3f} ms (±{std_ms:7.3f} ms) | hull={hull_len} vértices"
            )
            rows.append({
                "dataset": ds_name,
                "n_puntos": n,
                "algoritmo": alg_name,
                "repeticiones": REPEATS,
                "tiempo_promedio_ms": round(mean_ms, 4),
                "desv_std_ms": round(std_ms, 4),
                "vertices_hull": hull_len,
                "nota": "OK",
            })

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "dataset",
            "n_puntos",
            "algoritmo",
            "repeticiones",
            "tiempo_promedio_ms",
            "desv_std_ms",
            "vertices_hull",
            "nota",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResultados guardados en {output_csv}")


if __name__ == "__main__":
    files = glob.glob(os.path.join("datasets", "*.txt"))
    if os.path.exists("puntos_100.txt"):
        files.append("puntos_100.txt")
    run_benchmarks(files)