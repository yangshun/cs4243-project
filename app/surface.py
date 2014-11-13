import numpy as np


class Surface(object):
    def __init__(self, image, edge_points3d, edge_points2d):
        self.image = image
        self.edge_points3d = edge_points3d
        self.edge_points2d = np.float32(edge_points2d)  # This is required for using cv2's getPerspectiveTransform


class Polyhedron(object):
    def __init__(self, surfaces):
        self.surfaces = surfaces
