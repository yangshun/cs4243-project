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
