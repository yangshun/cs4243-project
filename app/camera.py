import numpy as np
from math import *
import cv2.cv as cv
import cv2 as cv2


# For this project, our world coordinate is defined as following
#   x-axis      left -> right, on the ground surface
#   y-axis      pointing inward the image, on the ground surface
#   z-axis      pointing upward to the sky


class Camera(object):
    def __init__(self, focal, **kwargs):
        self.focal = focal
        self.width = kwargs['width'] if 'width' in kwargs else 741
        self.half_width = self.width / 2.0
        self.height = kwargs['height'] if 'height' in kwargs else 304
        self.half_height = self.height / 2.0
        self.u0 = kwargs['u0'] if 'u0' in kwargs else 0.0  # image center horizontal offset
        self.v0 = kwargs['v0'] if 'v0' in kwargs else 0.0  # image center vertical offset
        self.bu = kwargs['bu'] if 'bu' in kwargs else 1.0  # pixel scaling factor in horizontal direction
        self.bv = kwargs['bv'] if 'bv' in kwargs else 1.0  # pixel scaling factor in vertical direction
        self.position = np.array([0.0, 0.0, 0.0])  # starting at the world coordinate system's origin

        # 1st column is the camera's horizontal axis
        # 2nd column is the camera's vertical axis
        # 3rd column is the camera's optical axis
        self.orientation = np.array([[1.0, 0.0, 0.0],
                                     [0.0, 0.0, 1.0],
                                     [0.0, -1.0, 0.0]])

    def horizontal_axis(self):
        return self.orientation[:, 0]

    def vertical_axis(self):
        return self.orientation[:, 1]

    def optical_axis(self):
        return self.orientation[:, 2]

    def point_projection(self, scene_point):
        """
        Project a scene point onto the camera's image plane using perspective projection.

        :param
            scene_point (np.array of shape (3,)): the 3D-coordinate of the scene point
        :return
            (float, float): the 2D-coordinate of the image point with respect to the center
            of the camera

        """
        d = scene_point - self.position

        u = self.u0 + self.focal * np.dot(d, self.horizontal_axis()) * self.bu / np.dot(d, self.optical_axis())
        v = self.v0 + self.focal * np.dot(d, self.vertical_axis()) * self.bv / np.dot(d, self.optical_axis())
        return u, v

    def surface_projection(self, surface):
        camera_position_wrt_surface = self.position - surface.edge_points3d[0]
        if np.dot(surface.normal, camera_position_wrt_surface) <= 0:
            return None

        projected_points = []
        for point3D in surface.edge_points3d:
            projected_point_wrt_center = self.point_projection(point3D)
            projected_point = (projected_point_wrt_center[0] + self.half_width,
                               projected_point_wrt_center[1] + self.half_height)
            projected_points.append(projected_point)

        projected_points = np.float32(projected_points)
        transform_matrix = cv2.getPerspectiveTransform(surface.edge_points2d, projected_points)
        return cv2.warpPerspective(surface.image, transform_matrix, (self.width, self.height))

    def polyhedron_projection(self, polyhedron):
        if len(polyhedron.surfaces) == 0:
            return None

        result_image = np.zeros((self.height, self.width, 3), np.uint8)
        for surface in polyhedron.surfaces:
            projected_image = self.surface_projection(surface)
            if projected_image is not None:
                # result_image = cv2.addWeighted(result_image, 0.5, projected_image, 0.5, 0.0)
                result_image = cv2.bitwise_or(result_image, projected_image)
        return result_image


class Quaternion(object):
    def __init__(self, scalar, vector):
        self.scalar = scalar
        self.vector = vector

    @staticmethod
    def rotation_quaternion(rotation_axis, angle):
        half_angle = angle / 2.0
        norm = np.linalg.norm(rotation_axis)
        rotation_unit_axis = rotation_axis / norm
        scalar = cos(half_angle)
        vector = np.array([sin(half_angle) * rotation_unit_axis[0],
                           sin(half_angle) * rotation_unit_axis[1],
                           sin(half_angle) * rotation_unit_axis[2]])

        return Quaternion(scalar, vector)

    @staticmethod
    def convert_from_vector(vector):
        return Quaternion(0, vector)

    def conjugate(self):
        return Quaternion(self.scalar, -self.vector)

    def to_vector(self):
        assert abs(self.scalar) < 0.0000001, "The scalar part of the quaternion is not zero, %d" % self.scalar
        return self.vector

    def to_rotation_matrix(self):
        q0 = self.scalar
        q1 = self.vector[0]
        q2 = self.vector[1]
        q3 = self.vector[2]
        r11 = q0**2 + q1**2 - q2**2 - q3**2
        r12 = 2 * (q1*q2 - q0*q3)
        r13 = 2 * (q1*q3 + q0*q2)
        r21 = 2 * (q1*q2 + q0*q3)
        r22 = q0**2 + q2**2 - q1**2 - q3**2
        r23 = 2 * (q2*q3 - q0*q1)
        r31 = 2 * (q1*q3 - q0*q2)
        r32 = 2 * (q2*q3 + q0*q1)
        r33 = q0**2 + q3**2 - q1**2 - q2**2
        return np.matrix([[r11, r12, r13],
                          [r21, r22, r23],
                          [r31, r32, r33]])

    def __mul__(self, other):
        try:
            s1, v1 = self.scalar, self.vector
            s2, v2 = other.scalar, other.vector
            s = s1 * s2 - np.dot(v1, v2)
            v = s1 * v2 + s2 * v1 + np.cross(v1, v2)
            return Quaternion(s, v)
        except:
            raise TypeError("Cannot multiply non-quaternion object.")


def generate_video(width, height, frames, file_name, file_path='./app/static'):
    fps = 15
    cap_size = (width, height)
    fourcc = cv.CV_FOURCC('a', 'v', 'c', '1')  # Apple's version of the MPEG4 http://www.fourcc.org/codecs.php
    writer = cv2.VideoWriter('%s/%s.mp4' % (file_path, file_name), fourcc, fps, cap_size, True)

    for x in range(len(frames)):
        writer.write(frames[x])
    writer.release()
    print 'video generated'
