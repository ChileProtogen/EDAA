import math
from functools import cmp_to_key

# Class to represent a point
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Method to check equality of two points
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# Function to find orientation of the triplet (a, b, c)
# Returns -1 if clockwise, 1 if counter-clockwise, 0 if collinear
def orientation(a, b, c):
    val = (a.x * (b.y - c.y)) + \
          (b.x * (c.y - a.y)) + \
          (c.x * (a.y - b.y))
    if val < 0:
        return -1  # Clockwise
    elif val > 0:
        return 1   # Counter-clockwise
    return 0       # Collinear

# Function to calculate the squared distance between two points
def distSq(a, b):
    return (a.x - b.x)**2 + (a.y - b.y)**2

# Function to find the convex hull from a list of 2D points
def findConvexHull(points):
    n = len(points)

    # Convex hull is not possible if there are fewer than 3 points
    if n < 3:
        return [[-1]]

    # Convert list of coordinates to Point objects
    a = [Point(p[0], p[1]) for p in points]

    # Find the point with the lowest y-coordinate (and leftmost in case of tie)
    p0 = min(a, key=lambda p: (p.y, p.x))

    # Sort points based on polar angle with p0 as reference
    def compare(p1, p2):
        o = orientation(p0, p1, p2)
        if o == 0:
            return distSq(p0, p1) - distSq(p0, p2)
        return -1 if o < 0 else 1

    # Sort using custom comparator
    a_sorted = sorted(a, key=cmp_to_key(compare))

    # Remove collinear points (keep farthest)
    m = 1
    for i in range(1, len(a_sorted)):
        while i < len(a_sorted) - 1 and \
              orientation(p0, a_sorted[i], a_sorted[i+1]) == 0:
            i += 1
        a_sorted[m] = a_sorted[i]
        m += 1

    # Convex hull is not possible with fewer than 3 unique points
    if m < 3:
        return [[-1]]

    # Initialize stack with first two points
    st = [a_sorted[0], a_sorted[1]]

    # Process the remaining points
    for i in range(2, m):
        while len(st) > 1 and \
              orientation(st[-2], st[-1], a_sorted[i]) >= 0:
            st.pop()
        st.append(a_sorted[i])

    # Final check for valid hull
    if len(st) < 3:
        return [[-1]]

    # Convert points back to list of [x, y]
    return [[int(p.x), int(p.y)] for p in st]

# Test case
points = [
    [0, 0], [1, -4], [-1, -5], [-5, -3], [-3, -1],
    [-1, -3], [-2, -2], [-1, -1], [-2, -1], [-1, 1]
]
# Compute the convex hull
hull = findConvexHull(points)

# Output the result
if len(hull) == 1 and hull[0][0] == -1:
    print(-1)
else:
    for point in hull:
        print(f"{point[0]}, {point[1]}")