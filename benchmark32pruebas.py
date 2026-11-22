import csv
import math
import os
import random
import statistics
import time
import tracemalloc

from graham_scan import findConvexHull as graham_scan
from jarvismarch import jarvis_march
from monotone_chain import monotone_chain

# ==========================================
# CONFIGURACIÓN EXPERIMENTAL
# ==========================================
RUNS = 5          # Repeticiones por prueba para calcular media y sigma
WARMUP = 1        # Ejecución previa de calentamiento
SEED = 42

SIZES = [100, 500, 1000, 2500, 5000, 10000, 20000, 35000]
DISTRIBUTIONS = ["Uniforme", "Circulo", "Clusters", "Colineal"]  # 4 x 8 = 32 pruebas


# ==========================================
# ESTRUCTURA DE ESTADÍSTICAS (Media, Sigma, Mediana, CV)
# ==========================================
def calculate_stats(times_ms):
    n = len(times_ms)
    mean = sum(times_ms) / n
    sq_sum = sum((t - mean) ** 2 for t in times_ms)
    stdev = math.sqrt(sq_sum / (n - 1)) if n > 1 else 0.0
    median = statistics.median(times_ms)
    cv_pct = (stdev / mean * 100.0) if mean > 0 else 0.0
    return {
        "mean": mean,
        "stdev": stdev,
        "median": median,
        "min": min(times_ms),
        "max": max(times_ms),
        "cv_pct": cv_pct,
    }


# ==========================================
# GENERADORES DE DATASETS (Usando enteros para compatibilidad exacta con Graham Scan)
# ==========================================
def generate_dataset(dist_name, n, rng):
    scale = 100000

    if dist_name == "Uniforme":
        pts = {(rng.randint(0, scale), rng.randint(0, scale)) for _ in range(n)}
        while len(pts) < n:
            pts.add((rng.randint(0, scale), rng.randint(0, scale)))
        return [[x, y] for x, y in pts]

    if dist_name == "Circulo":
        cx, cy, r = 50000, 50000, 45000
        pts = set()
        steps = n * 2
        for i in range(steps):
            if len(pts) >= n:
                break
            ang = (2.0 * math.pi * i) / steps
            x = int(round(cx + r * math.cos(ang)))
            y = int(round(cy + r * math.sin(ang)))
            pts.add((x, y))
        return [[x, y] for x, y in pts]

    if dist_name == "Clusters":
        num_clusters = 6
        centers = [
            (rng.randint(15000, scale - 15000), rng.randint(15000, scale - 15000))
            for _ in range(num_clusters)
        ]
        pts = set()
        i = 0
        while len(pts) < n:
            cx, cy = centers[i % num_clusters]
            x = int(round(rng.gauss(cx, 2500)))
            y = int(round(rng.gauss(cy, 2500)))
            pts.add((x, y))
            i += 1
        return [[x, y] for x, y in pts]

    if dist_name == "Colineal":
        pts = set()
        target_line = int(n * 0.6)
        while len(pts) < target_line:
            t = rng.randint(100, 49000)
            pts.add((t * 2, t + 10000))
        while len(pts) < n:
            pts.add((rng.randint(0, scale), rng.randint(0, scale)))
        return [[x, y] for x, y in pts]

    raise ValueError(f"Distribución desconocida: {dist_name}")


# ==========================================
# MEDICIÓN DE ALGORITMO
# ==========================================
def measure_algorithm(func, points, runs=RUNS, warmup=WARMUP):
    for _ in range(warmup):
        func([[p[0], p[1]] for p in points])

    times_ms = []
    hull_vertices = 0
    peak_mem_kb = 0.0

    for r in range(runs):
        data_copy = [[p[0], p[1]] for p in points]

        if r == 0:
            tracemalloc.start()

        t0 = time.perf_counter()
        res = func(data_copy)
        t1 = time.perf_counter()

        if r == 0:
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_mem_kb = peak_bytes / 1024.0

        times_ms.append((t1 - t0) * 1000.0)
        if res and not (len(res) == 1 and res[0][0] == -1):
            hull_vertices = len(res)

    stats = calculate_stats(times_ms)
    stats["hull_h"] = hull_vertices
    stats["mem_kb"] = peak_mem_kb
    return stats


def fmt_stat(st):
    return f"{st['mean']:7.2f} +/- {st['stdev']:6.2f}"


# ==========================================
# EJECUCIÓN PRINCIPAL (32 PRUEBAS)
# ==========================================
def main():
    rng = random.Random(SEED)
    algorithms = [
        ("Monotone", monotone_chain),
        ("Graham", graham_scan),
        ("Jarvis", jarvis_march),
    ]

    print("=" * 126)
    print("                    EXPERIMENTAL BENCHMARK: 2D CONVEX HULL (32 TEST CASES, RUNS = 5)                   ")
    print("=" * 126)
    header = (
        f"{'ID':<4} {'Distribucion':<11} {'N':<7} {'h':<6} "
        f"{'Monotone (ms)':<21} {'Graham (ms)':<21} {'Jarvis (ms)':<21} "
        f"{'Mem M/G/J (KB)':<22}"
    )
    print(header)
    print("-" * 126)

    csv_rows = []
    test_id = 1

    for dist_name in DISTRIBUTIONS:
        for n in SIZES:
            points = generate_dataset(dist_name, n, rng)
            actual_n = len(points)

            results = {}
            for alg_name, func in algorithms:
                results[alg_name] = measure_algorithm(func, points)

            h_val = results["Monotone"]["hull_h"]
            mem_str = (
                f"{results['Monotone']['mem_kb']:.1f}/"
                f"{results['Graham']['mem_kb']:.1f}/"
                f"{results['Jarvis']['mem_kb']:.1f}"
            )

            print(
                f"{test_id:<4} {dist_name:<11} {actual_n:<7} {h_val:<6} "
                f"{fmt_stat(results['Monotone']):<21} "
                f"{fmt_stat(results['Graham']):<21} "
                f"{fmt_stat(results['Jarvis']):<21} "
                f"{mem_str:<22}"
            )

            for alg_name, _ in algorithms:
                st = results[alg_name]
                csv_rows.append({
                    "test_id": test_id,
                    "distribucion": dist_name,
                    "N": actual_n,
                    "h_vertices": st["hull_h"],
                    "algoritmo": alg_name,
                    "runs": RUNS,
                    "media_ms": round(st["mean"], 4),
                    "stdev_ms": round(st["stdev"], 4),
                    "mediana_ms": round(st["median"], 4),
                    "min_ms": round(st["min"], 4),
                    "max_ms": round(st["max"], 4),
                    "cv_porcentaje": round(st["cv_pct"], 2),
                    "memoria_pico_kb": round(st["mem_kb"], 2),
                })

            test_id += 1
        print("-" * 126)

    out_csv = "resultados_32_pruebas.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"\n[OK] 32 pruebas completadas. Resultados detallados exportados a '{out_csv}'.")


if __name__ == "__main__":
    main()