from monotone_chain import cross, monotone_chain

# EJEMPLO DE USO: python .\incremental_monotone_chain.py .\puntos_100.txt para el archivo puntos_100.txt, se puede con otros sets de puntos.
# En este se pueden agregar puntos incrementalmente y se actualiza el convex hull en tiempo real.
# Funciona añadirlos en consola y clickeando con el mouse.

def insert_point_incremental(hull, p):
    """
    Actualiza un convex hull (ordenado en sentido antihorario) al insertar
    un nuevo punto p, reutilizando la envolvente previamente calculada.

    Retorna una tupla: (nuevo_hull, hubo_cambio).
    - Si p esta dentro o sobre el borde del hull actual, devuelve (hull, False).
    - Si p esta fuera, actualiza solo el arco visible y devuelve (nuevo_hull, True).
    """
    pt = [float(p[0]), float(p[1])]

    if pt in hull:
        return hull, False

    if len(hull) < 3:
        updated = monotone_chain(hull + [pt])
        return updated, (updated != hull)

    h = len(hull)
    # Una arista hull[i] -> hull[(i+1)%h] es visible desde pt si pt queda
    # a la derecha de la arista orientada (producto cruzado < 0 en orden CCW).
    visible = [cross(hull[i], hull[(i + 1) % h], pt) < 0 for i in range(h)]

    # Caso 1: ninguna arista es visible -> pt es interior o colineal al borde
    if not any(visible):
        return hull, False

    # Caso borde: todas las aristas visibles (fallback seguro)
    if all(visible):
        updated = monotone_chain(hull + [pt])
        return updated, (updated != hull)

    # Encontrar vertices tangentes:
    # - start_idx: arista entrante no visible y saliente visible
    # - end_idx: arista entrante visible y saliente no visible
    start_idx = None
    end_idx = None
    for i in range(h):
        prev_vis = visible[(i - 1) % h]
        curr_vis = visible[i]
        if not prev_vis and curr_vis:
            start_idx = i
        if prev_vis and not curr_vis:
            end_idx = i

    if start_idx is None or end_idx is None:
        updated = monotone_chain(hull + [pt])
        return updated, (updated != hull)

    # Reconstruir el hull conservando el arco no visible desde end_idx hasta start_idx
    new_hull = []
    idx = end_idx
    while True:
        new_hull.append(hull[idx])
        if idx == start_idx:
            break
        idx = (idx + 1) % h
    new_hull.append(pt)

    # Eliminar posibles puntos colineales exactos en las uniones
    cleaned = []
    m = len(new_hull)
    for i in range(m):
        a = new_hull[(i - 1) % m]
        b = new_hull[i]
        c = new_hull[(i + 1) % m]
        if cross(a, b, c) != 0:
            cleaned.append(b)

    final_hull = cleaned if len(cleaned) >= 3 else new_hull
    return final_hull, True