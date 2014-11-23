
import cv2
import numpy as np
import math

from app.reconstructor import Reconstructor
from app.graham_scan import *


class TextureExtractor(object):
    """Texture Extractor is used to extract a quad on an image and fatten it to be a rectangle texture"""

    def __init__(self, image, resolution=None, focus=None):
        """
        Instantiate a TextureExtractor and bind to an image
        @param:
            image: the image to bind into
            resolution: (Optional) the resolution of the image (pixels per meter)
            focus: (Optional) the focal length of the camera when taking the image (meters)
        """
        self.image = image
        self.reconstructor = None
        if resolution is not None and focus is not None:
            self.reconstructor = Reconstructor(image.shape, resolution, focus)

    def extractTexture(self, corners):
        """
        Extract the texture enclosed by a quad on the image
        @param:
            corners: an array of 4 points, each is a tuple (x,y,d) where (x,y) is
            position of the corner on the image, d is the distance from the camera
            to the real-world corner
        @return:
            the texture extracted.
        """

        # Make sure the there are 4 points in the CCW order
        # Assertion comes after Graham Scan because the scan can remove some points
        corners = calculateConvexHull(corners)
        assert (len(corners) == 4)

        # Sort corners to the clock wise order, starting with top-left
        corners = self.__sortCorners (corners)

        # Reconstruct the 3D position of the corners to calculate the optimal width and height
        cornerPositions = [(0, 0, 0)] * 4
        if self.reconstructor is not None:
            for i in range(4):
                cornerPositions[i] = self.reconstructor.calculate3DCoordinate (corners[i], corners[i][2])
                corners[i] = [corners[i][0], corners[i][1]]
        else:
            for i in range(4):
                corners[i] = [corners[i][0], corners[i][1]]
                cornerPositions[i] = [corners[i][0], corners[i][1], 0]

        width = max(self.distanceBetweenPoints(cornerPositions[0], cornerPositions[1]),
                    self.distanceBetweenPoints(cornerPositions[2], cornerPositions[3]))
        height = max(self.distanceBetweenPoints(cornerPositions[0], cornerPositions[3]),
                     self.distanceBetweenPoints(cornerPositions[1], cornerPositions[2]))

        if self.reconstructor is not None:
            print width, height
            width /= self.reconstructor.resolution
            height /= self.reconstructor.resolution
            print width, height

        # Create the texture and apply transformation to the quad
        texture = np.empty((width, height))
        textureCorners = np.array([(0, 0), (width, 0), (width, height), (0, height)], np.float32)
        corners = np.array(corners, np.float32)
        transformMatrix = cv2.getPerspectiveTransform(corners, textureCorners)
        texture = cv2.warpPerspective(self.image, transformMatrix, texture.shape)

        return texture

    def __sortCorners(self, corners):
        """
        Sort the corners, return them in the order:
        top-left, top-right, bottom-right, bottom-left
        """

        # Calculate the center point by averaging the corners
        center = [0, 0]
        for corner in corners:
            center[0] += corner[0]
            center[1] += corner[1]
        center[0] /= len(corners)
        center[1] /= len(corners)

        # Define the corners position by comparing with the center
        # Corners having lower y => top corners
        # Corners having lower x => left corners
        bottom = []
        top = []
        for corner in corners:
            if corner[1] < center[1]:
                top.append(corner)
            else:
                bottom.append(corner)
        topLeft = top[0]
        topRight = top[1]
        if top[0][0] > top[1][0]:
           topLeft = top[1]
           topRight = top[0]
        bottomLeft = bottom[0]
        bottomRight = bottom[1]
        if bottom[0][0] > bottom[1][0]:
           bottomLeft = bottom[1]
           bottomRight = bottom[0]

        # Return the result
        return [topLeft, topRight, bottomRight, bottomLeft]

    def distanceBetweenPoints(self, p1, p2):
        n = min(len(p1), len(p2))

        sqrSum = 0
        for i in range(3):
            sqrSum += (p1[i] - p2[i]) ** 2

        return math.sqrt(sqrSum)
