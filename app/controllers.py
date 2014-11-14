
from flask import render_template
from app import app
import cv2.cv as cv
import cv2
import numpy as np
from math import *

from camera import Camera, generate_video
from surface import Surface


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/video')
def video():
    width = 741
    height = 304
    depth = 2095

    # center
    image1 = cv2.imread('./app/static/center.png', cv2.CV_LOAD_IMAGE_COLOR)
    image1_points_3d = np.array([(0, depth, 0), (width, depth, 0), (width, depth, height), (0, depth, height)])
    image1_points_2d = np.array([(0, 0), (width, 0), (width, height), (0, height)])
    plane1 = Surface(image1, image1_points_3d, image1_points_2d)

    # left
    image2 = cv2.imread('./app/static/left.png', cv2.CV_LOAD_IMAGE_COLOR)
    image2_points_3d = np.array([(1, 1, 1), (1, depth, 1), (1, depth, height), (1, depth, height)])
    image2_points_2d = np.array([(0, 0), (391, 0), (391, 689), (0, 689)])
    plane2 = Surface(image2, image2_points_3d, image2_points_2d)

    # right
    image3 = cv2.imread('./app/static/right.png', cv2.CV_LOAD_IMAGE_COLOR)
    image3_points_3d = np.array([(width, depth, 0), (width, 0, 0), (width, 0, height), (width, depth, height)])
    # image3_points_2d = np.array([(0, 41), (503, 0), (503, 646), (0, 348)])
    image3_points_2d = np.array([(0, 0), (503, 0), (503, 646), (0, 646)])
    plane3 = Surface(image3, image3_points_3d, image3_points_2d)

    # top
    image4 = cv2.imread('./app/static/top.png', cv2.CV_LOAD_IMAGE_COLOR)
    image4_points_3d = np.array([(0, depth, height), (width, depth, height), (width, 0, height), (0, 0, height)])
    image4_points_2d = np.array([(0, 0), (1566, 0), (1566, 301), (0, 301)])
    plane4 = Surface(image4, image4_points_3d, image4_points_2d)

    # ground
    image5 = cv2.imread('./app/static/bottom.png', cv2.CV_LOAD_IMAGE_COLOR)
    image5_points_3d = np.array([(0, 0, 0), (width, 0, 0), (width, depth, 0), (0, depth, 0)])
    image5_points_2d = np.array([(0, 0), (1629, 0), (1629, 50), (0, 50)])
    plane5 = Surface(image5, image5_points_3d, image5_points_2d)



    camera = Camera(depth / 2.0)
    camera_path = generate_path()
    camera_orientation = generate_camera_orientation()

    frames = []
    for camera_pos, camera_orientation in zip(camera_path, camera_orientation):
        camera.position = camera_pos
        camera.orientation = camera_orientation
        projected_image1 = camera.project_surface(plane1)
        projected_image2 = camera.project_surface(plane2)
        projected_image3 = camera.project_surface(plane3)
        projected_image4 = camera.project_surface(plane4)
        projected_image5 = camera.project_surface(plane5)
        frame = cv2.addWeighted(projected_image1, 0.5, projected_image3, 0.5, 0.0)
        #frame = cv2.addWeighted(frame, 0.5, projected_image4, 0.5, 0.0)
        #frame = cv2.addWeighted(frame, 0.5, projected_image5, 0.5, 0.0)

        frames.append(frame)

    generate_video(width, height, frames, 'video')

    return render_template('video.html', name='CS4342')


num_of_points = 50


def generate_path():
    points = []
    for i in range(1, num_of_points + 1):
        points.append((300+ i*2, i*4, 0))
    return np.array(points)


def generate_camera_orientation():
    orientations = []
    for i in range(90 - num_of_points/2, 90 + num_of_points/2):
    # for i in range(41, 91):
        angle = i / 180.0 * pi
        #print "in degree ", i, "in radian ", angle
        orientations.append([[sin(angle), -cos(angle), 0], [0, 0, 1], [cos(angle), sin(angle), 0]])
    return orientations

