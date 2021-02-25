import cv2
import numpy as np
from math import sqrt

TOLERANCE = 0.5
INFINITY = 1 / TOLERANCE
HOMOGRAPHY_MARGIN_RATIO = 1.2


class Rectify:
    def __init__(self, images_rectify, image_rectify, contours_rectify):
        self.images = images_rectify
        self.image = image_rectify
        self.contours = contours_rectify
        self.tiles = []
        self.orientations = []
        self.grid_list = []
        self.grid_order = []


def rectify_image(contours, img_src, resized_tile_size):
    """Rectify the image vis-a-vis the contours so in the output image, contours are squares aligned horizontally and
    vertically"""

    images_rectify = []
    image_rectify = []
    contours_rectify = []

    for index_contour, contour in enumerate(contours):
        upper_leftmost_point = np.array([img_src.shape[1], img_src.shape[0]])
        upper_leftmost_point_index = 0
        for index_point, point in enumerate(contour):
            if point[0] + point[1] < upper_leftmost_point[0] + upper_leftmost_point[1]:
                upper_leftmost_point = point
                upper_leftmost_point_index = index_point

        # Compute the maximum distance between 2 points in contours_copy[0]
        dst_min = img_src.shape[0]
        point_iter = list([x, y] for x in range(4) for y in range(x, 4) if (x != y))
        for iter_point_a, iter_point_b in point_iter:
            distance = sqrt((contour[iter_point_a][0] - contour[iter_point_b][0]) ** 2
                            + (contour[iter_point_a][1] - contour[iter_point_b][1]) ** 2)
            if distance < dst_min:
                dst_min = distance
        dst_min /= HOMOGRAPHY_MARGIN_RATIO

        if dst_min < resized_tile_size:
            continue

        min_x = min(contour, key=lambda x: x[0])[0]
        max_x = max(contour, key=lambda x: x[0])[0]
        min_y = min(contour, key=lambda x: x[1])[1]
        max_y = max(contour, key=lambda x: x[1])[1]
        temp_image = img_src[min_y:max_y, min_x:max_x]

        # Compute the geometrical transformation
        img_src_dst_points = square_from_point(upper_leftmost_point, dst_min, upper_leftmost_point_index)
        upper_leftmost_point = [upper_leftmost_point[0]-min_x, upper_leftmost_point[1]-min_y]
        dst_points = square_from_point(upper_leftmost_point, dst_min, upper_leftmost_point_index)
        crop_contour = np.array([[contour[0][0]-min_x, contour[0][1]-min_y],
                                 [contour[1][0]-min_x, contour[1][1]-min_y],
                                 [contour[2][0]-min_x, contour[2][1]-min_y],
                                 [contour[3][0]-min_x, contour[3][1]-min_y]])

        h, status = cv2.findHomography(crop_contour, dst_points)
        temp_image = cv2.warpPerspective(temp_image, h, (temp_image.shape[1], temp_image.shape[0]))

        if index_contour == 0:
            h_first_contour, _ = cv2.findHomography(np.array(contour), img_src_dst_points)
            image_rectify = cv2.warpPerspective(img_src, h_first_contour, (img_src.shape[1], img_src.shape[0]))

        try:
            contours_rectify.append(convert_contour(contour, h_first_contour))
        except:
            continue

        converted_contour = convert_contour(crop_contour, h)
        temp_image = temp_image[converted_contour[0][1]:converted_contour[2][1], converted_contour[0][0]:converted_contour[2][0]]

        images_rectify.append(temp_image)

    rectified_object = Rectify(images_rectify, image_rectify, contours_rectify)

    return rectified_object


def get_abs_slope(point_a, point_b):
    """Get the abolute value of the slope between 2 points"""
    if point_a[0] - point_b[0]:
        slope = abs((point_a[1] - point_b[1]) / (point_a[0] - point_b[0]))
    else:
        slope = INFINITY
    if slope > INFINITY:
        slope = INFINITY
    return slope


def square_from_point(point, distance, index=0):
    """Make a square of area distance^2 from the up_left point"""
    output_point = np.array([point,
                             [point[0], point[1] + distance],
                             [point[0] + distance, point[1] + distance],
                             [point[0] + distance, point[1]]])
    output_point = np.roll(output_point, 2*index)
    return output_point


def convert_contour(contour, trans_mat):
    """Convert a contour of point using a 3x3 transformation matrix and sort them clockwise starting from top right"""
    temp_contour = []
    output_contour = []
    for i in range(len(contour)):
        x = int((trans_mat[0][0] * contour[i][0] + trans_mat[0][1] * contour[i][1] + trans_mat[0][2]) /
                (trans_mat[2][0] * contour[i][0] + trans_mat[2][1] * contour[i][1] + trans_mat[2][2]))
        y = int((trans_mat[1][0] * contour[i][0] + trans_mat[1][1] * contour[i][1] + trans_mat[1][2]) /
                (trans_mat[2][0] * contour[i][0] + trans_mat[2][1] * contour[i][1] + trans_mat[2][2]))
        if x < 0: x = 0
        if y < 0: y = 0
        temp_contour.append([x, y])
    output_contour.append(min(temp_contour, key=lambda point: point[0] + point[1]))
    output_contour.append(min(temp_contour, key=lambda point: -point[0] + point[1]))
    output_contour.append(min(temp_contour, key=lambda point: -point[0] - point[1]))
    output_contour.append(min(temp_contour, key=lambda point: point[0] - point[1]))
    return output_contour