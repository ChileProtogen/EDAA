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
RUNS = 32
WARMUP = 1
SEED = 42

DATASETS_DIR = "datasets"
HOUSING_PATH = os.path.join(DATASETS_DIR, "housing.csv")
CITIES_PATH = os.path.join(DATASETS_DIR, "cities15000.txt")
OUTPUT_CSV = "resultados_datasets_web.csv"

# Tamaños de muestra a evaluar por dataset + el dataset completo (None)
SAMPLE_SIZES = [500, 1000, 2500, 5000, 10000, None]


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


# =========================================================================
# CARGA Y LIMPIEZA DE DATASETS
# =========================================================================
def load_housing_xy(path):
    """Carga longitud (x) y latitud (y) desde housing.csv."""
    points = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"El archivo {path} está vacío o sin encabezados.")

        field_map = {name.strip().lower(): name for name in reader.fieldnames}
        lon_col = next(
            (field_map[k] for k in ("longitude", "lon", "lng", "x") if k in field_map),
            None,
        )
        lat_col = next(
            (field_map[k] for k in ("latitude", "lat", "y") if k in field_map),
            None,
        )

        if lon_col is None or lat_col is None:
            raise ValueError(
                f"No se encontraron columnas de coordenadas en {path}. Columnas: {reader.fieldnames}"
            )

        for row in reader:
            try:
                x = float(row[lon_col])
                y = float(row[lat_col])
                if math.isfinite(x) and math.isfinite(y):
                    points.append([x, y])
            except (TypeError, ValueError):
                continue

    return points


def load_cities15000_xy(path):
    """
    Carga longitud (x) y latitud (y) desde cities15000.txt (GeoNames TSV):
      col 4 = latitude, col 5 = longitude.
    """
    points = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            try:
                lat = float(parts[4])
                lon = float(parts[5])
                if math.isfinite(lat) and math.isfinite(lon):
                    points.append([lon, lat])
            except ValueError:
                continue

    return points


def deduplicate_points(points):
    """Elimina duplicados exactos preservando orden."""
    seen = set()
    unique = []
    for x, y in points:
        key = (float(x), float(y))
        if key not in seen:
            seen.add(key)
            unique.append([key[0], key[1]])
    return unique


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
        if res and not (len(res) == 1 and len(res[0]) == 1 and res[0][0] == -1):
            hull_vertices = len(res)

    stats = calculate_stats(times_ms)
    stats["hull_h"] = hull_vertices
    stats["mem_kb"] = peak_mem_kb
    return stats


def fmt_stat(st):
    return f"{st['mean']:7.2f} +/- {st['stdev']:6.2f}"


# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
def main():
    rng = random.Random(SEED)
    algorithms = [
        ("Monotone", monotone_chain),
        ("Graham", graham_scan),
        ("Jarvis", jarvis_march),
    ]

    raw_datasets = []
    if os.path.exists(HOUSING_PATH):
        raw_datasets.append(("housing.csv", deduplicate_points(load_housing_xy(HOUSING_PATH))))
    else:
        print(f"[AVISO] No se encontró {HOUSING_PATH}")

    if os.path.exists(CITIES_PATH):
        raw_datasets.append(("cities15000.txt", deduplicate_points(load_cities15000_xy(CITIES_PATH))))
    else:
        print(f"[AVISO] No se encontró {CITIES_PATH}")

    if not raw_datasets:
        print("No hay datasets disponibles en 'datasets/'.")
        return

    # Arma las pruebas (subconjuntos + dataset completo)
    test_cases = []
    for ds_name, full_pts in raw_datasets:
        for sz in SAMPLE_SIZES:
            if sz is None:
                test_cases.append((ds_name, "completo", full_pts))
            elif sz < len(full_pts):
                subset = rng.sample(full_pts, sz)
                test_cases.append((ds_name, f"muestra_{sz}", subset))

    print("=" * 132)
    print(f"              EXPERIMENTAL BENCHMARK: WEB DATASETS ({len(test_cases)} CASES, RUNS = {RUNS})              ")
    print("=" * 132)
    header = (
        f"{'ID':<4} {'Dataset':<16} {'Escenario':<13} {'N':<7} {'h':<6} "
        f"{'Monotone (ms)':<21} {'Graham (ms)':<21} {'Jarvis (ms)':<21} "
        f"{'Mem M/G/J (KB)':<22}"
    )
    print(header)
    print("-" * 132)

    csv_rows = []
    test_id = 1

    for ds_name, scenario, points in test_cases:
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
            f"{test_id:<4} {ds_name:<16} {scenario:<13} {actual_n:<7} {h_val:<6} "
            f"{fmt_stat(results['Monotone']):<21} "
            f"{fmt_stat(results['Graham']):<21} "
            f"{fmt_stat(results['Jarvis']):<21} "
            f"{mem_str:<22}"
        )

        for alg_name, _ in algorithms:
            st = results[alg_name]
            csv_rows.append({
                "test_id": test_id,
                "dataset": ds_name,
                "escenario": scenario,
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

    print("-" * 132)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"\n[OK] {len(test_cases)} pruebas completadas. Resultados exportados a '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()