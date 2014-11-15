from flask import render_template
from app import *
import cv2
import numpy as np
from math import *

from camera import Camera, generate_video
from surface import Surface, Polyhedron, Space


CAMPUS_IMAGE_PATH = STATIC_PATH + '/campus'


WIDTH = 741
HEIGHT = 304
DEPTH = 2095

IMAGE_CORNERS = {
    'center': np.float32([(0, 0), (741, 0), (741, 304), (0, 304)]),
    'right': np.float32([(0, 300), (503, 0), (503, 646), (0, 605)]),
    'left': np.float32([(0, 0), (391, 361), (391, 659), (0, 689)]),
    'top': np.float32([(0, 0), (1566, 0), (1062, 301), (326, 301)]),
    'bottom': np.float32([(380, 0), (1132, 6), (1629, 50), (0, 32)])
}

CORNERS_2D = {
    'center': np.float32([(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)]),
    'right': np.float32([(0, 0), (DEPTH, 0), (DEPTH, HEIGHT), (0, HEIGHT)]),
    'left': np.float32([(0, 0), (DEPTH, 0), (DEPTH, HEIGHT), (0, HEIGHT)]),
    'top': np.float32([(0, 0), (WIDTH, 0), (WIDTH, DEPTH), (0, DEPTH)]),
    'bottom': np.float32([(0, 0), (WIDTH, 0), (WIDTH, DEPTH), (0, DEPTH)])
}

DIMENSIONS = {
    'center': (WIDTH, HEIGHT),
    'right': (DEPTH, HEIGHT),
    'left': (DEPTH, HEIGHT),
    'top': (WIDTH, DEPTH),
    'bottom': (WIDTH, DEPTH)
}

CORNERS_3D = {
    'center': np.array([(-WIDTH/2.0, 0, HEIGHT), (WIDTH/2.0, 0, HEIGHT), (WIDTH/2.0, 0, 0), (-WIDTH/2.0, 0, 0)]),
    'right': np.array([(WIDTH/2.0, 0, HEIGHT), (WIDTH/2.0, -DEPTH, HEIGHT), (WIDTH/2.0, -DEPTH, 0), (WIDTH/2.0, 0, 0)]),
    'left': np.array([(-WIDTH/2.0, -DEPTH, HEIGHT), (-WIDTH/2.0, 0, HEIGHT), (-WIDTH/2.0, 0, 0), (-WIDTH/2.0, -DEPTH, 0)]),
    'top': np.array([(-WIDTH/2.0, -DEPTH, HEIGHT), (WIDTH/2.0, -DEPTH, HEIGHT), (WIDTH/2.0, 0, HEIGHT), (-WIDTH/2.0, 0, HEIGHT)]),
    'bottom': np.array([(-WIDTH/2.0, 0, 0), (WIDTH/2.0, 0, 0), (WIDTH/2.0, -DEPTH, 0), (-WIDTH/2.0, -DEPTH, 0)]),
}

@app.route('/campus')
def campus():
    space = Space()

    image_names = ['center', 'right', 'left', 'top', 'bottom']

    for image_name in image_names:
        image = cv2.imread(CAMPUS_IMAGE_PATH + '/' + image_name + '.png', cv2.CV_LOAD_IMAGE_COLOR)
        surface = Surface(image, CORNERS_3D[image_name], CORNERS_2D[image_name])
        space.add_model(Polyhedron([surface]))

    camera = Camera(DEPTH, width=1566, height=646)
    camera_path = generate_path()
    camera_orientation = generate_camera_orientation()

    frames = []
    for camera_pos, camera_orientation in zip(camera_path, camera_orientation):
        camera.position = camera_pos
        camera.orientation = camera_orientation
        frame = camera.project_space(space)
        frames.append(frame)

    generate_video(camera.width, camera.height, frames, 'video')

    return render_template('video.html', name='CS4244')


num_of_points = 50


def generate_path():
    points = []
    for i in range(1, num_of_points + 1):
        # points.append((0.0, -DEPTH, HEIGHT/2.0))
        points.append((-250 + i*10, -1500 + i*20, 30))
    return np.array(points)


def generate_camera_orientation():
    orientations = []
    for i in range(90 - num_of_points/2, 90 + num_of_points/2):
    # for i in range(0, 180, 180 // num_of_points):
        angle = i / 180.0 * pi
        # angle = pi / 2 + 0.001
        # print "in degree ", i, "in radian ", angle
        orientations.append(np.array([[sin(angle), -cos(angle), 0], [0, 0, -1], [cos(angle), sin(angle), 0]]))
    return orientations


@app.route('/fix_campus/<image_name>')
def fix_image(image_name):
    image = cv2.imread(CAMPUS_IMAGE_PATH + '/' + image_name + '_origin.png')
    transform_matrix = cv2.getPerspectiveTransform(IMAGE_CORNERS[image_name], CORNERS_2D[image_name])
    projected_image = cv2.warpPerspective(image, transform_matrix, DIMENSIONS[image_name])

    cv2.imwrite(CAMPUS_IMAGE_PATH + '/' + image_name + '.png', projected_image)

    return render_template('campus.html', image_name=image_name)

