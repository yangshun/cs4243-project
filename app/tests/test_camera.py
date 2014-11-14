from unittest import TestCase
import numpy as np
import cv2 as cv2
import cv2.cv as cv
from app.surface import Surface
from app.camera import Camera


class TestCamera(TestCase):
    def setUp(self):
        self.camera = Camera(3, width=5, height=5)
        self.camera.position = np.array([0, -10, 0])

    def tearDown(self):
        pass

    def testSurfaceProjection_leftPerpendicularSurface_shouldNotProject(self):
        edge_3dpoints = np.array([(0, 1, 1), (0, 0, 1), (0, 0, 0), (0, 1, 0)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        surface = Surface(None, edge_3dpoints, edge_2dpoints)

        projected_image, _ = self.camera.project_surface(surface)
        self.assertIsNone(projected_image)

    def testSurfaceProjection_rightPerpendicularSurface_shouldNotProject(self):
        edge_3dpoints = np.array([(1, 0, 1), (1, 1, 1), (1, 1, 0), (1, 0, 0)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        surface = Surface(None, edge_3dpoints, edge_2dpoints)

        projected_image, _ = self.camera.project_surface(surface)
        self.assertIsNone(projected_image)

    def testSurfaceProjection_backParallelSurface_shouldNotProject(self):
        edge_3dpoints = np.array([(1, 1, 1), (0, 1, 1), (0, 1, 0), (1, 1, 0)])
        edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
        surface = Surface(None, edge_3dpoints, edge_2dpoints)

        projected_image, _ = self.camera.project_surface(surface)
        self.assertIsNone(projected_image)

    def testProjectSurfave(self):
        image = cv2.imread('../static/cube/front.png', cv2.CV_LOAD_IMAGE_COLOR)
        edge_3dpoints = np.array([(-5, 0, 5), (5, 0, 5), (5, 0, -5), (-5, 0, -5)])
        edge_2dpoints = np.array([(0, 0), (200, 0), (200, 200), (0, 200)])
        surface = Surface(image, edge_3dpoints, edge_2dpoints)

        projected_image, image_depth = self.camera.project_surface(surface)

        expected_image_depth = np.array([[np.inf, np.inf, np.inf, np.inf, np.inf],
                                         [np.inf, 12.24744871, 11.30388331, 11.30388331, np.inf],
                                         [np.inf, 11.30388331, 10.27402334, 10.27402334, np.inf],
                                         [np.inf, 11.30388331, 10.27402334, 10.27402334, np.inf],
                                         [np.inf, np.inf, np.inf, np.inf, np.inf]])

        self.assertTrue(np.allclose(image_depth, expected_image_depth))