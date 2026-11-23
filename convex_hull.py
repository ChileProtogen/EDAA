import sys
import math
import matplotlib.pyplot as plt


# devuelve el producto cruz de los vectores a -> b y a -> c,
# positivo si c esta a la izquierda de a -> b, negativo si esta a la derecha
def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


# devuelve True si el punto a va antes que el punto b (compara x y luego y)
def isSmaller(a, b):
    return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1])


def findConvexHull(points):
    n = len(points)

    # un poligono necesita al menos 3 puntos
    if n < 3:
        return []

    # indices de los vertices del hull
    hull = set()

    # probamos cada par de puntos como posible arista
    for i in range(n):
        for j in range(i + 1, n):
            pos = 0
            neg = 0

            # lo y hi guardan los dos extremos sobre la recta que pasa por i y j
            lo = i
            hi = j
            if isSmaller(points[j], points[i]):
                lo = j
                hi = i

            # contamos los puntos a la izquierda y a la derecha de la recta
            for k in range(n):
                if k == i or k == j:
                    continue

                c = cross(points[i], points[j], points[k])
                if c > 0:
                    pos += 1
                elif c < 0:
                    neg += 1
                else:
                    # el punto esta sobre la recta, puede ser un extremo
                    if isSmaller(points[k], points[lo]):
                        lo = k
                    if isSmaller(points[hi], points[k]):
                        hi = k

            # hay puntos a ambos lados, la recta no es arista del hull
            if pos > 0 and neg > 0:
                continue

            # la recta es una arista, solo sus extremos son vertices
            hull.add(lo)
            hull.add(hi)

    # menos de 3 vertices significa que todos los puntos son colineales
    if len(hull) < 3:
        return []

    return [points[idx] for idx in hull]


# lee un archivo con una linea "x,y" por punto
def readPoints(path):
    points = []
    with open(path, "r", encoding="utf-8") as f:
        for num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                x, y = line.split(",")
                points.append([float(x), float(y)])
            except ValueError:
                print(f"Linea {num} ignorada (formato invalido): {line!r}")
    return points


# ordena los vertices del hull en sentido antihorario para poder dibujar el poligono
def orderCounterClockwise(hullPoints):
    cx = sum(p[0] for p in hullPoints) / len(hullPoints)
    cy = sum(p[1] for p in hullPoints) / len(hullPoints)
    return sorted(hullPoints, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def plotHull(points, hullPoints):
    fig, ax = plt.subplots(figsize=(8, 6))

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, color="steelblue", label="Puntos", zorder=2)

    if hullPoints:
        ordered = orderCounterClockwise(hullPoints)
        closed = ordered + [ordered[0]]
        hx = [p[0] for p in closed]
        hy = [p[1] for p in closed]
        ax.fill(hx, hy, color="tomato", alpha=0.15, zorder=1)
        ax.plot(hx, hy, color="tomato", linewidth=2, label="Convex hull", zorder=3)
        ax.scatter(hx[:-1], hy[:-1], color="tomato", s=70, zorder=4)
    else:
        ax.set_title("No hay convex hull (menos de 3 puntos o todos colineales)")

    ax.set_aspect("equal", adjustable="datalim")
    if hullPoints:
        ax.set_title(f"Convex hull: {len(hullPoints)} vertices de {len(points)} puntos")

    plt.show()


if __name__ == "__main__":
    
    path = sys.argv[1] if len(sys.argv) > 1 else "puntos_100.txt"

    points = readPoints(path)
    print(f"Se leyeron {len(points)} puntos de {path}")

    res = findConvexHull(points)
    res.sort()
    print("Vertices del convex hull:", res)

    plotHull(points, res)