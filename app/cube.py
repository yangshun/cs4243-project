from flask import render_template
from app import *
import cv2.cv as cv
import cv2
import numpy as np
from math import *


from camera import Camera, Quaternion, generate_video
from surface import Surface, Polyhedron, Space


# The world origin is chosen to be at the center of the cube.
# Let the cube size be w. The bottom left corner of the
# front surface of the cube is (-w/2, -w/2, -w/2)
#
#        p8 ---- p7
#       /|      /|
#     p4 +--- p3 |
#     |  |    |  |
#     |  p5 --+- p6
#     | /     | /
#     p1 ---- p2

CUBE_SIZE = 100.0
IMAGE_SIZE = 200
CAMERA_DIST = 250
CUBE_IMAGE_PATH = STATIC_PATH + '/cube'

@app.route('/cube')
def cube():
    space = Space()
    space.add_model(build_cube(CUBE_SIZE, offset_x=-CUBE_SIZE/2, offset_y=-CUBE_SIZE/2, offset_z=-CUBE_SIZE/2))
    space.add_model(build_cube(CUBE_SIZE/2, offset_x=CUBE_SIZE, offset_y=0, offset_z=0))
    space.add_model(build_cube(CUBE_SIZE/4, offset_x=-CUBE_SIZE, offset_y=-CUBE_SIZE, offset_z=-CUBE_SIZE/2))

    camera = Camera(200.0, width=640, height=480)
    camera_path, camera_orientation = generate_path_and_orientation()
    # camera_path, camera_orientation = generate_path_and_orientation_from_higher_up()

    frames = []
    for camera_pos, camera_orientation in zip(camera_path, camera_orientation):
        camera.position = camera_pos
        camera.orientation = camera_orientation
        frame = camera.space_projection(space)
        frames.append(frame)

    generate_video(640, 480, frames, 'cube')

    return render_template('cube.html')


def build_cube(size, offset_x=0.0, offset_y=0.0, offset_z=0.0):
    front_img = cv2.imread(CUBE_IMAGE_PATH + '/front.png', cv2.CV_LOAD_IMAGE_COLOR)
    left_img = cv2.imread(CUBE_IMAGE_PATH + '/left.png', cv2.CV_LOAD_IMAGE_COLOR)
    right_img = cv2.imread(CUBE_IMAGE_PATH + '/right.png', cv2.CV_LOAD_IMAGE_COLOR)
    top_img = cv2.imread(CUBE_IMAGE_PATH + '/top.png', cv2.CV_LOAD_IMAGE_COLOR)
    bottom_img = cv2.imread(CUBE_IMAGE_PATH + '/bottom.png', cv2.CV_LOAD_IMAGE_COLOR)
    back_img = cv2.imread(CUBE_IMAGE_PATH + '/back.png', cv2.CV_LOAD_IMAGE_COLOR)
    p1 = [offset_x, offset_y, offset_z]
    p2 = [offset_x + size, offset_y, offset_z]
    p3 = [offset_x + size, offset_y, offset_z + size]
    p4 = [offset_x, offset_y, offset_z + size]
    p5 = [offset_x, offset_y + size, offset_z]
    p6 = [offset_x + size, offset_y + size, offset_z]
    p7 = [offset_x + size, offset_y + size, offset_z + size]
    p8 = [offset_x, offset_y + size, offset_z + size]
    img_2d_corners = np.array([(0, 0), (IMAGE_SIZE, 0), (IMAGE_SIZE, IMAGE_SIZE), (0, IMAGE_SIZE)])
    front_surface = Surface(front_img, np.array([p4, p3, p2, p1]), img_2d_corners)
    left_surface = Surface(left_img, np.array([p8, p4, p1, p5]), img_2d_corners)
    right_surface = Surface(right_img, np.array([p3, p7, p6, p2]), img_2d_corners)
    top_surface = Surface(top_img, np.array([p8, p7, p3, p4]), img_2d_corners)
    bottom_surface = Surface(bottom_img, np.array([p1, p2, p6, p5]), img_2d_corners)
    back_surface = Surface(back_img, np.array([p7, p8, p5, p6]), img_2d_corners)

    return Polyhedron([front_surface, left_surface, right_surface,
                       top_surface, bottom_surface, back_surface])


step = 5  # smaller is better
rotation_angle = pi * step / 180


def generate_path_and_orientation():
    pos_rot_quat = Quaternion.rotation_quaternion(np.array([0.0, 0.0, 1.0]), rotation_angle)
    conj_pos_rot_quat = pos_rot_quat.conjugate()
    pos_quat = Quaternion.convert_from_vector(np.array([0.0, -CAMERA_DIST, 0.0]))

    camera_rot_quat = Quaternion.rotation_quaternion(np.array([0.0, 0.0, 1.0]), rotation_angle)
    camera_rot_mat = camera_rot_quat.to_rotation_matrix()
    orientation = np.array([[1.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, -1.0, 0.0]])

    path = [pos_quat.to_vector()]
    orientations = [orientation]

    for i in range(1, int(360 / step) + 1):
        pos_quat = pos_rot_quat * pos_quat * conj_pos_rot_quat
        path.append(pos_quat.to_vector())

        orientation = np.asarray(np.dot(camera_rot_mat, orientation))
        orientations.append(orientation)

    return path, orientations


# from higher up!
def generate_path_and_orientation_from_higher_up():
    pos_rot_quat = Quaternion.rotation_quaternion(np.array([0.0, 0.0, 1.0]), rotation_angle)
    conj_pos_rot_quat = pos_rot_quat.conjugate()
    pos_quat = Quaternion.convert_from_vector(np.array([0.0, -CAMERA_DIST, 0.0]))

    camera_rot_quat = Quaternion.rotation_quaternion(np.array([0.0, 0.0, 1.0]), rotation_angle)
    camera_rot_mat = camera_rot_quat.to_rotation_matrix()
    orientation = np.array([[1.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, -1.0, 0.0]])

    path = [pos_quat.to_vector()]
    orientations = [orientation]

    for i in range(1, int(360 / step) + 1):
        pos_quat = pos_rot_quat * pos_quat * conj_pos_rot_quat
        path.append(pos_quat.to_vector())

        orientation = np.asarray(np.dot(camera_rot_mat, orientation))
        orientations.append(orientation)

    return path, orientations
