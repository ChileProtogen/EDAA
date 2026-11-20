def jarvis_march(points):
    """
    Calcula el Convex Hull usando Jarvis March (Gift Wrapping).
    :param points: Lista de tuplas o listas con coordenadas (x, y).
    :ojs: Retorna la lista de puntos que forman la envolvente convexa en orden antihorario.
    """
    n = len(points)
    if n < 3:
        return points  # Se necesitan al menos 3 puntos para formar un polígono

    # 1. Encontrar el punto inicial (el más a la izquierda; en empate, el de menor y)
    start = min(points, key=lambda p: (p[0], p[1]))
    
    hull = []
    current = start
    
    while True:
        hull.append(current)
        next_target = points[0]
        if next_target == current:
            next_target = points[1]
            
        for candidate in points:
            if candidate == current:
                continue
            
            # Producto cruzado para determinar la orientación del vector (current -> next_target) y (current -> candidate)
            cross = (next_target[0] - current[0]) * (candidate[1] - current[1]) - \
                    (next_target[1] - current[1]) * (candidate[0] - current[0])
            
            # Si 'candidate' está más a la izquierda (giro antihorario), o si son colineales
            # pero 'candidate' está más lejos, actualizamos nuestro siguiente objetivo.
            if cross > 0 or (cross == 0 and dist_sq(current, candidate) > dist_sq(current, next_target)):
                next_target = candidate
                
        current = next_target
        
        # Si volvemos al punto inicial, completamos el ciclo del hull
        if current == start:
            break
            
    return hull

def dist_sq(p1, p2):
    """Calcula la distancia al cuadrado entre dos puntos para evitar raíces cuadradas innecesarias."""
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

# --- Ejemplo de uso ---
if __name__ == "__main__":
    dataset = [(0, 3), (2, 2), (1, 1), (2, 1), (3, 0), (0, 0), (3, 3)]
    resultado = jarvis_march(dataset)
    print("Convex Hull con Jarvis March:", resultado)