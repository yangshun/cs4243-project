import numpy as np
from math import *
import cv2.cv as cv
import cv2 as cv2
from helper import *
from surface import Surface


# For this project, our world coordinate is defined as following
#   x-axis      left -> right, on the ground surface
#   y-axis      pointing into the image, on the ground surface
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

        self.orientation = np.array([[1.0, 0.0, 0.0],   # camera's horizontal axis
                                     [0.0, 0.0, -1.0],  # camera's vertical axis
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
            (float, float): the 2D-coordinate of the image point with respect to the center
            of the camera

        """
        dist = scene_point - self.position
        d = np.dot(dist, self.optical_axis())
        if d == 0:
            # to avoid explosion!!!
            d = np.finfo(np.float32).eps

        u = self.u0 + self.focal * np.dot(dist, self.horizontal_axis()) * self.bu / d
        v = self.v0 + self.focal * np.dot(dist, self.vertical_axis()) * self.bv / d
        return box_coord(u), box_coord(v)

    def clipping_surface(self, surface):
        top_left_dist = self.distance_to_image_plane(surface.top_left_corner3d())
        top_right_dist = self.distance_to_image_plane(surface.top_right_corner3d())
        bottom_right_dist = self.distance_to_image_plane(surface.bottom_right_corner3d())
        bottom_left_dist = self.distance_to_image_plane(surface.bottom_left_corner3d())

        distances = [top_left_dist, top_right_dist, bottom_right_dist, bottom_left_dist]

        num_of_positive_distances = len(filter(lambda dist: dist > 0, distances))
        if num_of_positive_distances == 0:
            # The surface is completely behind the camera
            return None

        if num_of_positive_distances == 4:
            # The surface is completely in front of the camera
            return surface.image

        # The surface is partially in front and we need to clip the surface.
        # For simplicity, we assume that the surface go out of view in a
        # "nice" manner. That means we can slice the visible part as a rectangle
        # not any other polygon.
        height, width, _ = surface.image.shape
        x1, x2 = self._find_cut_region(top_left_dist, top_right_dist, width)
        y1, y2 = self._find_cut_region(top_left_dist, bottom_left_dist, height)

        if x1 == x2 or y1 == y2:
            return None

        return surface.image[y1:y2, x1:x2]

    def _find_cut_region(self, left_dist, right_dist, length):
        """
        :param left_dist: the distance from the leftmost point to the image-plane
        :param right_dist: the distance from the rightmost point to the image-plane
        :param length: length from the leftmost to rightmost point
        :return (left, right): the range from which the image should be clipped
        """
        if left_dist * right_dist >= 0:
            return 0, length

        cut_position = abs(left_dist) / (abs(left_dist) + abs(right_dist)) * length

        if left_dist < 0:
            return cut_position, length
        return 0, cut_position

    def distance_to_image_plane(self, point):
        distance_wrt_camera = point - self.position
        distance_wrt_image_plane = np.dot(distance_wrt_camera, self.optical_axis())
        return distance_wrt_image_plane

    def project_surface(self, surface):
        camera_position_wrt_surface = self.position - surface.edge_points3d[0]
        if np.dot(surface.normal, camera_position_wrt_surface) <= 0:
            # camera is behind the surface
            # return None, None
            return None

        projected_points = []
        for point3D in surface.edge_points3d:
            projected_point_wrt_center = self.point_projection(point3D)
            projected_point = (projected_point_wrt_center[0] + self.half_width,
                               projected_point_wrt_center[1] + self.half_height)
            projected_points.append(projected_point)

        projected_points = np.float32(projected_points)
        transform_matrix = cv2.getPerspectiveTransform(surface.edge_points2d, projected_points)

        surface_image = self.clipping_surface(surface)
        if surface_image is None:
            # The entire surface is out of view!
            return None

        projected_image = cv2.warpPerspective(surface_image, transform_matrix, (self.width, self.height))

        # image_depth = self.__get_projected_image_depth(projected_image, surface)

        # return projected_image, image_depth
        return projected_image

    def project_surfaces(self, surfaces):
        result_image = np.zeros((self.height, self.width, 3), np.uint8)
        result_depth = np.ones((self.height, self.width)) * np.inf

        for surface in surfaces:
            projected_image = self.project_surface(surface)
            # projected_image, image_depth = self.project_surface(surface)
            if projected_image is not None:
                result_image = cv2.bitwise_or(result_image, projected_image)
                # result_image, result_depth = self.__overlay_images(result_image, result_depth,
                #                                                    projected_image, image_depth)
        return result_image

    def project_polyhedron(self, polyhedron):
        return self.project_surfaces(polyhedron.surfaces)

    def project_space(self, space):
        surfaces = []
        for model in space.models:
            surfaces.extend(model.surfaces)
        return self.project_surfaces(surfaces)

    def __get_projected_image_depth(self, projected_image, surface):
        """
        Let p is a point on the surface. We're using the 1st point on the surface
            n is the normal vector of the surface
            d is the vector pointing in the direction from the camera to the pixel on the image
        Then the depth of the image pixel is the distance from the camera to the actual point
        on the surface. This depth is calculated as
            depth = (p . n) / (d . n)
        where . is the dot product of 2 vectors

        Note: all vectors are w.r.t. the camera's coordinate system.
        """
        image_depth = np.ones((self.height, self.width)) * np.inf
        p = self.orientation.dot(surface.edge_points3d[0] - self.position)
        n = self.orientation.dot(surface.normal)
        t = p.dot(n)

        for i in xrange(self.height):
            for j in xrange(self.width):
                if not np.allclose(projected_image[i, j], 0):
                    d = np.array([j - self.half_width, i - self.half_height, self.focal])
                    d /= np.linalg.norm(d)
                    image_depth[i, j] = t / d.dot(n)

        return image_depth

    def __overlay_images(self, image1, image_depth1, image2, image_depth2):
        height, width, _ = image1.shape
        for i in xrange(height):
            for j in xrange(width):
                if image_depth2[i, j] < image_depth1[i, j]:
                    image_depth1[i, j] = image_depth2[i, j]
                    image1[i, j] = image2[i, j]

        return image1, image_depth1


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


def generate_video(width, height, frames, file_name, path='./app/static/video'):
    print 'generating video'
    fps = 15
    cap_size = (width, height)
    fourcc = cv.CV_FOURCC('a', 'v', 'c', '1')  # Apple's version of the MPEG4 http://www.fourcc.org/codecs.php
    file_path = '%s/%s.mp4' % (path, file_name)
    writer = cv2.VideoWriter(file_path, fourcc, fps, cap_size, True)

    for x in range(len(frames)):
        writer.write(frames[x])
    writer.release()
    print 'video generated'
    return '/static/video/%s.mp4' % (file_name)
