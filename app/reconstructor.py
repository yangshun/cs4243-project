import math
import numpy as np


class Reconstructor (object):
    """
    Reconstructor is used to derive the 3D position of every pixel
    in an arbitrary image, providing the depth of that pixel.
    """

    def __init__(self, size, resolution, focus):
        """
        Instantiate a Reconstructor and bind to a camera's setting
        @param:
            size: the tuple (Height, Width) denotes the image size
            resolution: the resolution of the image (pixels per meter)
            focus: the focus length of the camera taken this image (meters)
        """
        self.size = size
        self.resolution = float(resolution)
        self.focus = float(focus)

    def calculate3DCoordinate(self, pixel, depth):
        """
        Calculate the 3D Coordinate of a pixel on the image, providing
        the estimated depth of the pixel.
        @param:
            pixel: a tuple (x,y) denoting the pixel on the image. Note that
        (0,0) is the top left corner of the image. x is row number and y is
        column number.
            depth: the z value of the pixel. z = focus is the virtual plane
        of the camera. z = 0 is the plane containing the camera.
        @return:
            the 3D coordinate of the pixel in a tuple (x',y',depth). Note that
        (0,0,0) is the camera's position.
        """

        # Convert the pixel from image coordinate to virtual plane coordinate
        pixel = self.convertToVirtualPlane(pixel)

        # Convert the pixel position unit from pixels to meters
        pixel = (pixel[0] / self.resolution, pixel[1] / self.resolution)

        # The pixel must lie on the virtual plane, hence its world coordinate
        # must be (x, y, f). Calculate the real point (x', y', depth) by
        # using similar triangles
        ratio = depth / self.focus
        return pixel[0]*ratio, pixel[1]*ratio, depth

    def convertToVirtualPlane(self, pixel):
        """
        Convert the pixel from image coordinate to virtual plane coordinate
        @param:
            pixel: a tuple (x,y) denoting the pixel on the image. Note that
        (0,0) is the top left corner of the image. x is row number and y is
        column number.
        @return:
            the virtual plane coordinate of the pixel. (0,0) is the center
        of the image while x axis is pointing right and y axis is pointing
        up
        """
        
        # Rotate the coordinate by 90 degrees CCW => Rotate the point 90 degrees CW
        x = pixel[1]
        y = -pixel[0]
        # Translate the coordinate along (W/2, -H/2)
        x -= self.size[1] / 2
        y += self.size[0] / 2

        return x, y
