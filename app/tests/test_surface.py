from unittest import TestCase
import numpy as np

from app.surface import Surface


# The test surface is parallel to the x-y plane (a horizontal plane)
# and intercept the z-axis at 1. It's facing up (the normal vector
# is pointing in +z direction.
class TestSurface(TestCase):
    def setUp(self):
        edge_3dpoints = np.array([(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        self.surface = Surface(None, edge_3dpoints, edge_2dpoints)

    def testNormalVector(self):
        expected_normal_unit = np.array([0, 0, 1])

        self.assertTrue(np.array_equal(self.surface.normal, expected_normal_unit))

    def testDistanceToPoint_positiveDistance(self):
        point = np.array([2, 3, 5])
        dist = self.surface.distance_to_point(point)

        self.assertAlmostEqual(dist, 4)

    def testDistanceToPoint_zeroDistance(self):
        point = np.array([100, -100, 1])
        dist = self.surface.distance_to_point(point)

        self.assertAlmostEqual(dist, 0)

    def testDistanceToPoint_negativeDistance(self):
        point = np.array([2, 4, -5])
        dist = self.surface.distance_to_point(point)

        self.assertAlmostEqual(dist, -6)
