import math
from functools import cmp_to_key

# Clase que representa un punto en 2D
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Método para revisar la igualdad entre dos puntos.
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# Función para encontrar la orientación de tres puntos (a, b, c)
# Retorna -1 si es horario, 1 si es antihorario, y 0 si son colineales
def orientation(a, b, c):
    val = (a.x * (b.y - c.y)) + \
          (b.x * (c.y - a.y)) + \
          (c.x * (a.y - b.y))
    if val < 0:
        return -1  # Horario
    elif val > 0:
        return 1   # Antihorario
    return 0       # Colineal

# Función para calcular la distancia al cuadrado entre dos puntos
def distSq(a, b):
    return (a.x - b.x)**2 + (a.y - b.y)**2

# Función para encontrar el convex hull a partir de una lista de puntos 2D
def findConvexHull(points):
    n = len(points)

    # Convex hull es imposible con menos de 3 puntos
    if n < 3:
        return [[-1]]

    
    a = [Point(p[0], p[1]) for p in points]

    # Encontrar el punto con la coordenada y más baja (y en caso de empate, la x más baja)
    p0 = min(a, key=lambda p: (p.y, p.x))

    
    def compare(p1, p2):
        o = orientation(p0, p1, p2)
        if o == 0:
            return distSq(p0, p1) - distSq(p0, p2)
        return -1 if o < 0 else 1

    
    a_sorted = sorted(a, key=cmp_to_key(compare))

    # Remover puntos colineales, dejando solo el más lejano
    m = 1
    for i in range(1, len(a_sorted)):
        while i < len(a_sorted) - 1 and \
              orientation(p0, a_sorted[i], a_sorted[i+1]) == 0:
            i += 1
        a_sorted[m] = a_sorted[i]
        m += 1

    
    if m < 3:
        return [[-1]]

    
    st = [a_sorted[0], a_sorted[1]]

    
    for i in range(2, m):
        while len(st) > 1 and \
              orientation(st[-2], st[-1], a_sorted[i]) >= 0:
            st.pop()
        st.append(a_sorted[i])

    
    if len(st) < 3:
        return [[-1]]

    
    return [[int(p.x), int(p.y)] for p in st]

# Test case
points = [
    [0, 0], [1, -4], [-1, -5], [-5, -3], [-3, -1],
    [-1, -3], [-2, -2], [-1, -1], [-2, -1], [-1, 1]
]

hull = findConvexHull(points)


if len(hull) == 1 and hull[0][0] == -1:
    print(-1)
else:
    for point in hull:
        print(f"{point[0]}, {point[1]}")