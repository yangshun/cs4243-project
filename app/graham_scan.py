# Graham Scan - Tom Switzer <thomas.switzer@gmail.com>

TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)


def isCW(p, q, r):
    return cmp((q[0] - p[0]) * (r[1] - p[1]) - (r[0] - p[0]) * (q[1] - p[1]), 0)


def _keepLeft(hull, r):
    while len(hull) > 1 and isCW(hull[-2], hull[-1], r) != TURN_LEFT:
            hull.pop()
    if not len(hull) or hull[-1] != r:
        hull.append(r)
    return hull


def calculateConvexHull(points):
    """Returns points on convex hull of an array of points in CCW order."""
    points = sorted(points)
    l = reduce(_keepLeft, points, [])
    u = reduce(_keepLeft, reversed(points), [])
    return l.extend(u[i] for i in xrange(1, len(u) - 1)) or l