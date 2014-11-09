import numpy as np
import cv2.cv as cv
import cv2 as cv2
import plane


# For this project, our world coordinate is defined as following
#   x-axis      left -> right, on the ground surface
#   y-axis      pointing inward the image, on the ground surface
#   z-axis      pointing upward to the sky


class Camera(object):
    def __init__(self, focal, **kwargs):
        self.focal = focal
        self.width = kwargs['width'] if 'width' in kwargs else 741
        self.height = kwargs['height'] if 'height' in kwargs else 304
        self.u0 = kwargs['u0'] if 'u0' in kwargs else 0.0  # image center horizontal offset
        self.v0 = kwargs['v0'] if 'v0' in kwargs else 0.0  # image center vertical offset
        self.bu = kwargs['bu'] if 'bu' in kwargs else 1.0  # pixel scaling factor in horizontal direction
        self.bv = kwargs['bv'] if 'bv' in kwargs else 1.0  # pixel scaling factor in vertical direction
        self.position = np.array([0.0, 0.0, 0.0])  # starting at the world coordinate system's origin
        self.orientation = np.array([[1.0, 0.0, 0.0],   # camera's horizontal axis
                                     [0.0, 0.0, 1.0],   # camera's vertical axis
                                     [0.0, 1.0, 0.0]])  # camera's optical axis

    def horizontal_axis(self):
        return self.orientation[0]

    def vertical_axis(self):
        return self.orientation[1]

    def optical_axis(self):
        return self.orientation[2]

    def point_projection(self, scene_point):
        """
        Project a scene point onto the camera's image plane using perspective projection.

        :param
            scene_point (np.array of shape (3,)): the 3D-coordinate of the scene point
        :return
            (float, float): the 2D-coordinate of the image point

        """
        d = scene_point - self.position

        u = self.u0 + self.focal * np.dot(d, self.horizontal_axis()) * self.bu / np.dot(d, self.optical_axis())
        v = self.v0 + self.focal * np.dot(d, self.vertical_axis()) * self.bv / np.dot(d, self.optical_axis())
        return u, v

    def plane_projection(self, plane):
        projected_points = []
        for point3D in plane.edge_points3d:
            projected_point = self.point_projection(point3D)
            projected_points.append(projected_point)

        projected_points = np.float32(projected_points)
        transform_matrix = cv2.getPerspectiveTransform(plane.edge_points2d, projected_points)
        return cv2.warpPerspective(plane.image, transform_matrix, (self.width, self.height))
