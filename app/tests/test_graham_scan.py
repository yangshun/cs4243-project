from unittest import TestCase
from app.graham_scan import *


class TestGrahamScan(TestCase):
    def test_CCW(self):
        p = (1, 2)
        q = (2, 3)
        r = (3, 4)
        self.assertTrue(isCW(p, q, r) == 0)
        p = (-1, 2)
        q = (-2, 3)
        r = (-3, 4)
        self.assertTrue(isCW(p, q, r) == 0)
        p = (-11, 2)
        q = (-22, 3)
        r = (-33, 4)
        self.assertTrue(isCW(p, q, r) == 0)

        p = (0, 0)
        self.assertTrue(isCW(p, p, p) == 0)

        p = (0, 0)
        q = (1, 0)
        self.assertTrue(isCW(p, p, q) == 0)
        p = (0, 0)
        q = (1, 0)
        self.assertTrue(isCW(p, q, p) == 0)
        p = (0, 0)
        q = (1, 0)
        self.assertTrue(isCW(q, p, p) == 0)

        p = (-1, 2)
        q = (2, 3)
        r = (3, 4)
        self.assertTrue(isCW(p, q, r) == 1)
        p = (0, 0)
        q = (-1, 0)
        r = (0, -4)
        self.assertTrue(isCW(p, q, r) == 1)

        p = (1, 0)
        p = (5, 2)
        r = (-1, 3)
        self.assertTrue(isCW(p, q, r) == -1)
        p = (0, 0)
        p = (1, 0)
        r = (-1, 1)
        self.assertTrue(isCW(p, q, r) == -1)

    def test_GrahamScan(self):
        points = [(1, 2), (5, 2), (-1, 4)]
        points = calculateConvexHull(points)
        self.__assertConvexHull(points)
        self.assertEqual(len(points), 3)

        points = [(5, 2), (-1, 4), (1, 2), (4, -2)]
        points = calculateConvexHull(points)
        self.__assertConvexHull(points)
        self.assertEqual(len(points), 3)

        points = [(5, 2), (-1, 4), (4, -2), (1, 2), (0, 0), (-2, -5)]
        points = calculateConvexHull(points)
        self.__assertConvexHull(points)
        self.assertEqual(len(points), 4)

    def __assertConvexHull(self, points):
        """
        Assert whether the points listed are in CW order
        """
        for i in range(0, len(points) - 2):
            p = points[i]
            q = points[i + 1]
            r = points[i + 2]
            self.assertTrue(isCW(p, q, r) == 1)
