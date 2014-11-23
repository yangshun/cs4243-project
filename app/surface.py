import numpy as np


class Surface(object):
    def __init__(self, image, edge_points3d, edge_points2d):
        """
        Constructor for a surface defined by a texture image and
        4 boundary points. Choose the first point as the origin
        of the surface's coordinate system.

        :param image: image array
        :param edge_points3d: array of 3d coordinates of 4 corner points in clockwise direction
        :param edge_points2d: array of 2d coordinates of 4 corner points in clockwise direction
        """
        assert len(edge_points3d) == 4 and len(edge_points2d) == 4

        self.image = image
        self.edge_points3d = edge_points3d
        self.edge_points2d = np.float32(edge_points2d)  # This is required for using cv2's getPerspectiveTransform
        self.normal = self._get_normal_vector()

    def top_left_corner3d(self):
        return self.edge_points3d[0]

    def top_right_corner3d(self):
        return self.edge_points3d[1]

    def bottom_right_corner3d(self):
        return self.edge_points3d[2]

    def bottom_left_corner3d(self):
        return self.edge_points3d[3]

    def distance_to_point(self, point):
        point_to_surface = point - self.top_left_corner3d()
        distance_to_surface = self.normal.dot(point_to_surface)
        return distance_to_surface

    def _get_normal_vector(self):
        """
        :return: the normal vector of the surface. It determined the front side
        of the surface and it's not necessarily a unit vector
        """
        p0 = self.edge_points3d[0]
        p1 = self.edge_points3d[1]
        p3 = self.edge_points3d[3]
        v1 = p3 - p0
        v2 = p1 - p0
        normal = np.cross(v1, v2)
        norm = np.linalg.norm(normal)
        return normal / norm


class Polyhedron(object):
    def __init__(self, surfaces):
        self.surfaces = surfaces


class Space(object):
    def __init__(self, models=None):
        self.models = models or []

    def add_model(self, model):
        assert isinstance(model, Polyhedron)
        self.models.append(model)


class Line2D(object):
    def __init__(self, point1, point2):
        """
        Using the line equation a*x + b*y + c = 0 with b >= 0
        :param point1: starting point
        :param point2: ending point
        :return: a Line object
        """
        assert len(point1) == 2 and len(point2) == 2

        self.a = point2[1] - point1[1]
        self.b = point1[0] - point2[0]
        self.c = point1[1] * point2[0] - point1[0] * point2[1]

        if self.b < 0:
            self.a = -self.a
            self.b = -self.b
            self.c = -self.c

    def is_point_on_left(self, point):
        return self.a * point[0] + self.b * point[1] + self.c > 0

    def is_point_on_right(self, point):
        return self.a * point[0] + self.b * point[1] + self.c < 0

    def is_point_on_line(self, point):
        return self.a * point[0] + self.b * point[1] + self.c == 0

    def get_y_from_x(self, x):
        if self.b == 0:
            return 0.0

        return 1.0 * (-self.c - self.a * x) / self.b

    def get_x_from_y(self, y):
        if self.a == 0:
            return 0.0

        return 1.0 * (-self.c - self.b * y) / self.a
