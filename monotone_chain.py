def cross(o, a, b):
    """Producto cruzado de los vectores (o -> a) y (o -> b).
    > 0: giro antihorario (izquierda)
    < 0: giro horario (derecha)
    = 0: colineales
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def monotone_chain(points):
    """Calcula el Convex Hull en 2D usando el algoritmo Monotone Chain (Andrew).
    Retorna los vértices de la envolvente en orden antihorario (sin repetir el inicio).
    """
    # Eliminar duplicados y ordenar por (x, y)
    pts = sorted({(float(p[0]), float(p[1])) for p in points})
    n = len(pts)

    if n <= 1:
        return [[x, y] for x, y in pts]

    # Construir envolvente inferior
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Construir envolvente superior (recorriendo de derecha a izquierda)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Se omiten los últimos puntos de cada mitad porque coinciden con el inicio de la otra
    hull = lower[:-1] + upper[:-1]
    return [[x, y] for x, y in hull]


if __name__ == "__main__":
    sample = [[0, 3], [2, 2], [1, 1], [2, 1], [3, 0], [0, 0], [3, 3], [1.5, 1.5]]
    print("Monotone Chain hull:", monotone_chain(sample))