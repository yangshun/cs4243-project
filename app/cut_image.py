from flask import render_template
from app import *
import cv2
import numpy as np
from reconstructor import Reconstructor
from texture_extractor import TextureExtractor
from surface import Line2D


IMAGE_PATH = STATIC_PATH + '/test'


# data = [
#     (
#         "FrontGate",
#         [ (700, 750), (830, 750), (830, 870), (700, 870)],
#         [ 140, 140, 140, 140 ]
#     ),
#     (
#         "FrontCooridor-Right",
#         [ (830, 790), (970, 780), (970, 875), (830, 870)],
#         [ 140, 140, 140, 140 ]
#     ),
#     (
#         "FarRightBuilding-FrontFace",
#         [ (1170, 700), (1235, 680), (1240, 885), (1170, 875)],
#         [ 90, 80, 80, 90 ]
#     ),
#     (
#         "RightTree-Tall",
#         [ (1390, 450), (1480, 800), (1400, 900), (1300, 800)],
#         [ 84, 83, 82, 83 ]
#     )
# ]

# data = [
#     (
#         "center",
#         [(590, 510), (1130, 510), (1130, 875), (590, 875)],
#         [140, 140, 140, 140]
#     ),
#     (
#         "right",
#         [(1130, 510), (1632, 370), (1632, 920), (1130, 875)],
#         [140, 0, 0, 140]
#     ),
# ]


@app.route('/cut_image')
def cut_image():

    image = cv2.imread(STATIC_PATH + '/img/project.jpg', cv2.CV_LOAD_IMAGE_COLOR)

    extractor = TextureExtractor(image)

    # Create a reconstructor to convert 3D coordinate of 2D points
    reconstructor = Reconstructor(image.shape, 28370, 0.041)

    inner_top_left = (390, 579)
    inner_bottom_right = (1130, 882)
    vanishing_point = (684, 846)
    height, width, _ = image.shape
    depth = 140

    data = generate_corners_data(width, height, depth, inner_top_left, inner_bottom_right, vanishing_point)

    for texture_name, corners, depths in data:

        # Extract textures to files
        texture = extractor.extractTexture(corners)
        cv2.imwrite(IMAGE_PATH + '/' + texture_name + ".png", texture)

        for i in range(len(corners)):
            position3D = reconstructor.calculate3DCoordinate(corners[i], depths[i])
            print position3D

    return render_template('campus.html', image_name="campus")


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

