from app import *
import cv2
import numpy as np
from reconstructor import Reconstructor
from texture_extractor import TextureExtractor
from surface import Surface, Line2D


IMAGE_PATH = STATIC_PATH + '/img'
SLICED_IMAGE_PATH = IMAGE_PATH + '/sliced'



WIDTH = 741
HEIGHT = 304
DEPTH = 2095

CORNERS_3D = {
    'center': np.array([(-WIDTH/2.0, 0, HEIGHT), (WIDTH/2.0, 0, HEIGHT), (WIDTH/2.0, 0, 0), (-WIDTH/2.0, 0, 0)]),
    'right': np.array([(WIDTH/2.0, 0, HEIGHT), (WIDTH/2.0, -DEPTH, HEIGHT), (WIDTH/2.0, -DEPTH, 0), (WIDTH/2.0, 0, 0)]),
    'left': np.array([(-WIDTH/2.0, -DEPTH, HEIGHT), (-WIDTH/2.0, 0, HEIGHT), (-WIDTH/2.0, 0, 0), (-WIDTH/2.0, -DEPTH, 0)]),
    'top': np.array([(-WIDTH/2.0, -DEPTH, HEIGHT), (WIDTH/2.0, -DEPTH, HEIGHT), (WIDTH/2.0, 0, HEIGHT), (-WIDTH/2.0, 0, HEIGHT)]),
    'bottom': np.array([(-WIDTH/2.0, 0, 0), (WIDTH/2.0, 0, 0), (WIDTH/2.0, -DEPTH, 0), (-WIDTH/2.0, -DEPTH, 0)]),
}


def cut_image(image_name, camera_info, space_dimension, inner_box, vanishing_point):

    original_image = cv2.imread(IMAGE_PATH + '/' + image_name, cv2.CV_LOAD_IMAGE_COLOR)

    extractor = TextureExtractor(original_image)

    # Create a reconstructor to convert 3D coordinate of 2D points
    reconstructor = Reconstructor(original_image.shape, camera_info['resolution'], camera_info['focal_length'])

    inner_top_left, inner_bottom_right = inner_box
    image_height, image_width, _ = original_image.shape
    space_width, space_height, space_depth = space_dimension

    data = generate_corners_data(image_width, image_height, space_depth, inner_top_left, inner_bottom_right,
                                 vanishing_point)

    surfaces = []
    for texture_name, corners, depths in data:

        # Extract textures to files
        texture = extractor.extractTexture(corners)
        cv2.imwrite(SLICED_IMAGE_PATH + '/' + texture_name + ".png", texture)

        # Calculate 3D corners
        print texture_name
        corners3d = []
        for i in range(len(corners)):
            position3D = reconstructor.calculate3DCoordinate(corners[i], depths[i])

            print position3D

        corners3d = CORNERS_3D[texture_name]

        # Calculate 2D corners. Just the 4 corners of the image rectangle
        texture_height, texture_width, _ = texture.shape
        corners2d = np.float32([(0, 0), (texture_width, 0), (texture_width, texture_height), (0, texture_height)])

        surface = Surface(texture, corners3d, corners2d)
        surfaces.append(surface)

    return surfaces


# This method assumes that when extrapolating the inner box, the line cuts the 2 side edges of the image
# not the top and the bottom boundaries.
def generate_corners_data(width, height, depth, inner_top_left, inner_bottom_right, vanishing_point):
    inner_top_right = (inner_bottom_right[0], inner_top_left[1])
    inner_bottom_left = (inner_top_left[0], inner_bottom_right[1])

    top_left_line = Line2D(inner_top_left, vanishing_point)
    outer_top_left = (0, max(top_left_line.get_y_from_x(0), 0))
    top_right_line = Line2D(inner_top_right, vanishing_point)
    outer_top_right = (width, max(top_right_line.get_y_from_x(width), 0))
    bottom_right_line = Line2D(inner_bottom_right, vanishing_point)
    outer_bottom_right = (width, min(bottom_right_line.get_y_from_x(width), height))
    bottom_left_line = Line2D(inner_bottom_left, vanishing_point)
    outer_bottom_left = (0, min(bottom_left_line.get_y_from_x(0), height))

    center = (
        "center",
        [inner_top_left, inner_top_right, inner_bottom_right, inner_bottom_left],
        [depth, depth, depth, depth]
    )

    right = (
        "right",
        [inner_top_right, outer_top_right, outer_bottom_right, inner_bottom_right],
        [depth, 0, 0, depth]
    )

    left = (
        "left",
        [outer_top_left, inner_top_left, inner_bottom_left, outer_bottom_left],
        [0, depth, depth, 0]
    )

    top = (
        "top",
        [outer_top_left, outer_top_right, inner_top_right, inner_top_left],
        [0, 0, depth, depth]
    )

    bottom = (
        "bottom",
        [inner_bottom_left, inner_bottom_right, outer_bottom_right, outer_bottom_left],
        [depth, depth, 0, 0]
    )

    return [center, right, left, top, bottom]

