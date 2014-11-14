from unittest import TestCase
import numpy as np

from app.surface import Surface


class TestSurface(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_normal_vector(self):
        edge_3dpoints = np.array([(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        surface = Surface(None, edge_3dpoints, edge_2dpoints)

        expected_normal_unit = np.array([0, 0, 1])

        self.assertTrue(np.array_equal(surface.normal, expected_normal_unit))
