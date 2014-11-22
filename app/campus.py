from flask import render_template, request
import json
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

@app.route('/generate_video', methods=['POST'])
def campus():
    data = json.loads(request.data)

    space = Space()

    image_names = ['center', 'right', 'left', 'top', 'bottom']

    for image_name in image_names:
        image = cv2.imread(CAMPUS_IMAGE_PATH + '/' + image_name + '.png', cv2.CV_LOAD_IMAGE_COLOR)
        surface = Surface(image, CORNERS_3D[image_name], CORNERS_2D[image_name])
        space.add_model(Polyhedron([surface]))

    camera_width = 970
    camera_height = 400
    BEZIER_PATH_ORDER = 3
    camera = Camera(DEPTH/2, width=camera_width, height=camera_height)
    camera_path = generate_bezier_path(data['camera_path'], BEZIER_PATH_ORDER)
    camera_looking_forward = data['camera_looking_forward']

    camera_orientation = generate_camera_orientation(camera_path, camera_looking_forward)
    if not camera_looking_forward:
        camera_path, camera_orientation = smoothen_camera(camera_path[3:], camera_orientation[3:])
        
    frames = []
    for camera_pos, camera_orientation in zip(camera_path, camera_orientation):
        camera.position = camera_pos
        camera.orientation = camera_orientation
        frame = camera.project_space(space)
        frames.append(frame)

    file_name = data['file_name']
    file_path = generate_video(camera.width, camera.height, frames, file_name)

    return json.dumps({ 'status': 'success', 
                        'video': {'name': file_name, 'width': camera_width, 'height': camera_height, 'src': file_path}
                    })


def generate_path(path_points2d):
    points = []

    for point2d in path_points2d:
        point3d = (point2d['x'], point2d['y'], point2d['z'])
        points.append(point3d)

    return points


def generate_camera_orientation(camera_path, look_forward):
    # Camera's horizontal axis is world's x-axis
    # Camera's vertical axis is the opposite of the world's z-axis
    # Camera's optical axis is the world's y-axis
    orientations = []
    if look_forward:
        for i in range(len(camera_path)):
            orientations.append(np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]))
    else:
        for i in range(1, len(camera_path)):
            optical_vector = np.array([camera_path[i][0] - camera_path[i-1][0], camera_path[i][1] - camera_path[i-1][1], 0])
            if np.linalg.norm(optical_vector) > 0:
                optical_vector_norm = optical_vector / np.linalg.norm(optical_vector)
            else:
                optical_vector_norm = optical_vector
            angle_rad = atan2(optical_vector_norm[1], optical_vector_norm[0])
            angle_deg = ceil(angle_rad/pi * 180)
            orientations.append(angle_deg)
            if i == len(camera_path) - 1:
                orientations.append(angle_deg)
    return orientations

def smoothen_camera(camera_path, camera_angles):
    final_path_points, final_camera_angles = [], []
    vertical_vector = np.array([0, 0, -1])
    for i in range(1, len(camera_angles)):
        step = 1 if camera_angles[i] > camera_angles[i-1] else -1
        number_of_interpolations = camera_angles[i-1] - camera_angles[i]
        for angle_deg in range(int(camera_angles[i-1]), int(camera_angles[i]), step):
            optical_vector = np.array([cos(float(angle_deg)/180 * pi), sin(float(angle_deg)/180 * pi), 0])
            horizontal_vector = np.cross(vertical_vector, optical_vector)
            final_camera_angles.append(np.array([horizontal_vector, vertical_vector, optical_vector]))
            final_path_points.append(camera_path[i])
    return final_path_points, final_camera_angles

NUM_LINE_SEGMENTS = 256

def generate_bezier_path(points_list, order):
    num_bezier_sets = (len(points_list) - 1) / order
    prev_p2 = {}
    path_points = []
    for i in range(num_bezier_sets):
        p0 = points_list[i * order]
        if i != 0:
            diff_x = p0['x'] - prev_p2['x']
            diff_y = p0['y'] - prev_p2['y']
            diff_z = p0['z'] - prev_p2['z']
            p1 = {}
            p1['x'] = p0['x'] + diff_x
            p1['y'] = p0['y'] + diff_y
            p1['z'] = points_list[i * order + 1]['z']
        else:
            p1 = points_list[i * order + 1]
        p2 = points_list[i * order + 2]
        p3 = points_list[i * order + 3]
        segment_chunk_length = NUM_LINE_SEGMENTS / 3
        for j in range(NUM_LINE_SEGMENTS + 1):
            t = float(j) / NUM_LINE_SEGMENTS
            x = ((1-t)**3)*p0['x'] + 3*((1-t)**2)*t*p1['x'] + 3*(1-t)*(t**2)*p2['x'] + (t**3)*p3['x']
            y = ((1-t)**3)*p0['y'] + 3*((1-t)**2)*t*p1['y'] + 3*(1-t)*(t**2)*p2['y'] + (t**3)*p3['y']
            if 0 <= j < segment_chunk_length:
                z = (p1['z']-p0['z']) * (float(j%segment_chunk_length)/segment_chunk_length) + p0['z']
            elif segment_chunk_length <= j < 2*segment_chunk_length:
                z = (p2['z']-p1['z']) * (float(j%segment_chunk_length)/segment_chunk_length) + p1['z']
            elif 2*segment_chunk_length <= j:
                z = (p3['z']-p2['z']) * (float(j%segment_chunk_length)/segment_chunk_length) + p2['z']
            path_points.append((x, y, z))
        prev_p2 = p2
    return path_points

#################
# OLD CODE!!!!
#################
num_of_points = 50


def old_generate_path():
    points = []
    for i in range(1, num_of_points + 1):
        # points.append((0.0, -DEPTH, HEIGHT/2.0))
        points.append((-250 + i*10, -1500 + i*20, 30))
    return np.array(points)


def old_generate_camera_orientation():
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

