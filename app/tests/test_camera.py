from unittest import TestCase
import numpy as np
from app.surface import Surface
from app.camera import Camera


class TestCamera(TestCase):
    def setUp(self):
        self.camera = Camera(1)
        self.position = np.array([0, -10, 0])

    def tearDown(self):
        pass

    def testSurfaceProjection_leftPerpendicularSurface_shouldNotProject(self):
        edge_3dpoints = np.array([(0, 1, 1), (0, 0, 1), (0, 0, 0), (0, 1, 0)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        surface = Surface(None, edge_3dpoints, edge_2dpoints)

        self.assertIsNone(self.camera.project_surface(surface))

    def testSurfaceProjection_rightPerpendicularSurface_shouldNotProject(self):
        edge_3dpoints = np.array([(1, 0, 1), (1, 1, 1), (1, 1, 0), (1, 0, 0)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        surface = Surface(None, edge_3dpoints, edge_2dpoints)

        self.assertIsNone(self.camera.project_surface(surface))

    def testSurfaceProjection_backParallelSurface_shouldNotProject(self):
        edge_3dpoints = np.array([(1, 1, 1), (0, 1, 1), (0, 1, 0), (1, 1, 0)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        surface = Surface(None, edge_3dpoints, edge_2dpoints)

        self.assertIsNone(self.camera.project_surface(surface))