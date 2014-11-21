from unittest import TestCase
import numpy as np
import cv2 as cv2
from app.surface import Surface
from app.camera import Camera


SIZE = 100.0


class TestCamera(TestCase):
    def setUp(self):
        self.camera = Camera(50, width=200, height=200)
        self.camera.position = np.array([0, -20, 0])

        self.image = cv2.imread('../static/cube/front.png', cv2.CV_LOAD_IMAGE_COLOR)
        self.edge_2dpoints = edge_2dpoints = np.array([(0, 0), (200, 0), (200, 200), (0, 200)])

    def tearDown(self):
        pass

    # def testSurfaceProjection_leftPerpendicularSurface_shouldNotProject(self):
    #     edge_3dpoints = np.array([(0, 1, 1), (0, 0, 1), (0, 0, 0), (0, 1, 0)])
    #     edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
    #     surface = Surface(None, edge_3dpoints, edge_2dpoints)
    #
    #     projected_image, _ = self.camera.project_surface(surface)
    #     self.assertIsNone(projected_image)
    #
    # def testSurfaceProjection_rightPerpendicularSurface_shouldNotProject(self):
    #     edge_3dpoints = np.array([(1, 0, 1), (1, 1, 1), (1, 1, 0), (1, 0, 0)])
    #     edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
    #     surface = Surface(None, edge_3dpoints, edge_2dpoints)
    #
    #     projected_image, _ = self.camera.project_surface(surface)
    #     self.assertIsNone(projected_image)
    #
    # def testSurfaceProjection_backParallelSurface_shouldNotProject(self):
    #     edge_3dpoints = np.array([(1, 1, 1), (0, 1, 1), (0, 1, 0), (1, 1, 0)])
    #     edge_2dpoints = np.array([(0, 0), (0, 0), (0, 0), (0, 0)])
    #     surface = Surface(None, edge_3dpoints, edge_2dpoints)
    #
    #     projected_image, _ = self.camera.project_surface(surface)
    #     self.assertIsNone(projected_image)
    #
    # def testProjectSurfaceDepth(self):
    #     image = cv2.imread('../static/cube/front.png', cv2.CV_LOAD_IMAGE_COLOR)
    #     edge_3dpoints = np.array([(-5, 0, 5), (5, 0, 5), (5, 0, -5), (-5, 0, -5)])
    #     edge_2dpoints = np.array([(0, 0), (200, 0), (200, 200), (0, 200)])
    #     surface = Surface(image, edge_3dpoints, edge_2dpoints)
    #
    #     projected_image, image_depth = self.camera.project_surface(surface)
    #
    #     expected_image_depth = np.array([[np.inf, np.inf, np.inf, np.inf, np.inf],
    #                                      [np.inf, 12.24744871, 11.30388331, 11.30388331, np.inf],
    #                                      [np.inf, 11.30388331, 10.27402334, 10.27402334, np.inf],
    #                                      [np.inf, 11.30388331, 10.27402334, 10.27402334, np.inf],
    #                                      [np.inf, np.inf, np.inf, np.inf, np.inf]])
    #
    #     self.assertTrue(np.allclose(image_depth, expected_image_depth))

    def testProjectionSurface_perpendicularSurface(self):
        # front coordinate
        # edge_3dpoints = np.array([(-SIZE/2, 0, SIZE/2), (SIZE/2, 0, SIZE/2), (SIZE/2, 0, -SIZE/2), (-SIZE/2, 0, -SIZE/2)])

        # left surface
        edge_3dpoints = np.array([(-SIZE/2, -SIZE/2, SIZE/2), (-SIZE/2, SIZE/2, SIZE/2),
                                  (-SIZE/2, SIZE/2, -SIZE/2), (-SIZE/2, -SIZE/2, -SIZE/2)])

        surface = Surface(self.image, edge_3dpoints, self.edge_2dpoints)

        projected_image = self.camera.project_surface(surface)
        cv2.imwrite('../static/cube/test.png', projected_image)

    def testDistanceToImagePlane_positiveDistance(self):
        point = np.array((3, 4, 5))
        dist = self.camera.distance_to_image_plane(point)

        self.assertAlmostEqual(dist, 24)

    def testDistanceToImagePlane_zeroDistance(self):
        point = np.array((3, -20, 5))
        dist = self.camera.distance_to_image_plane(point)

        self.assertAlmostEqual(dist, 0)

    def testDistanceToImagePlane_negativeDistance(self):
        point = np.array((3, -100, 5))
        dist = self.camera.distance_to_image_plane(point)

        self.assertAlmostEqual(dist, -80)

    def testClippingSurface_inFront_noClipping(self):
        edge_3dpoints = np.array([(-SIZE/2, -SIZE/2, SIZE/2), (-SIZE/2, SIZE/2, SIZE/2),
                                  (-SIZE/2, SIZE/2, -SIZE/2), (-SIZE/2, -SIZE/2, -SIZE/2)])
        surface = Surface(self.image, edge_3dpoints, self.edge_2dpoints)

        self.camera.position = np.array([0, -51, 0])
        clipped_surface = self.camera.clipping_surface(surface)
        clipped_height, clipped_width, _ = clipped_surface.image.shape
        self.assertAlmostEqual(clipped_height, 200)
        self.assertAlmostEqual(clipped_width, 200)

    def testClippingSurface_behind_clippedTotally(self):
        edge_3dpoints = np.array([(-SIZE/2, -SIZE/2, SIZE/2), (-SIZE/2, SIZE/2, SIZE/2),
                                  (-SIZE/2, SIZE/2, -SIZE/2), (-SIZE/2, -SIZE/2, -SIZE/2)])
        surface = Surface(self.image, edge_3dpoints, self.edge_2dpoints)

        self.camera.position = np.array([0, 50, 0])
        clipped_surface = self.camera.clipping_surface(surface)

        self.assertIsNone(clipped_surface)

    def testClippingSurface_partially_clipped(self):
        edge_3dpoints = np.array([(-SIZE/2, -SIZE/2, SIZE/2), (-SIZE/2, SIZE/2, SIZE/2),
                                  (-SIZE/2, SIZE/2, -SIZE/2), (-SIZE/2, -SIZE/2, -SIZE/2)])
        surface = Surface(self.image, edge_3dpoints, self.edge_2dpoints)

        self.camera.position = np.array([0, 0, 0])
        clipped_surface = self.camera.clipping_surface(surface)
        clipped_height, clipped_width, _ = clipped_surface.image.shape
        self.assertAlmostEqual(clipped_height, 200)
        self.assertAlmostEqual(clipped_width, 100)
