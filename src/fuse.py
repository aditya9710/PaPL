import numpy as np

POS_X = 0
POS_Y = 1
THRESHOLD_COLLINEAR = 0.2
PROXIMITY_PIX = 10
INFINITY_SLOPE = 10
NUMBER_OF_CORNER = 4


def fuse_points_in_contours(contours):
    """Erase useless points (collinear or too close)"""
    new_contours = []
    for contour in contours:
        contour_fuse_point = fuse_duplicates_points(contour)

        index_contour = []
        new_contour = []

        if len(contour_fuse_point) > NUMBER_OF_CORNER:
            for index in range(len(contour_fuse_point)):
                if index == (len(contour_fuse_point) - 2):
                    index_temp1 = 0
                    index_temp2 = index + 1
                elif index == (len(contour_fuse_point) - 1):
                    index_temp1 = 1
                    index_temp2 = 0
                else:
                    index_temp1 = index + 2
                    index_temp2 = index + 1
                pt1 = contour_fuse_point[index]
                pt2 = contour_fuse_point[index_temp2]
                pt3 = contour_fuse_point[index_temp1]
                if collinear(pt1, pt2, pt3):
                    index_contour.append(index + 1)

            for index, point in enumerate(contour_fuse_point):
                if any(index == x for x in index_contour):
                    pass
                else:
                    new_contour.append(contour_fuse_point[index])
            if len(new_contour) == NUMBER_OF_CORNER:
                new_contours.append([new_contour[0][0], new_contour[1][0], new_contour[2][0], new_contour[3][0]])
        elif len(contour_fuse_point) == NUMBER_OF_CORNER:
            new_contours.append([contour_fuse_point[0][0], contour_fuse_point[1][0], contour_fuse_point[2][0],
                                 contour_fuse_point[3][0]])

    return new_contours


def collinear(pt1, pt2, pt3):
    """Control if three points are collinear"""
    slope1 = get_slope_contour(pt1[0], pt2[0])
    slope2 = get_slope_contour(pt1[0], pt3[0])
    a = abs(slope1 - slope2)
    if a < THRESHOLD_COLLINEAR:
        return True
    else:
        return False


def fuse_duplicates_points(contour):
    """"Fuse two point too close"""
    index = 0
    temp_contour = []
    for point_to_add in contour:
        point_to_add = point_to_add[0].tolist()
        to_add = True
        for point_to_test in temp_contour:
            if (point_to_add != point_to_test and
                    points_too_close(point_to_add, point_to_test)):
                to_add = False
        if to_add:
            temp_contour.append(point_to_add)
            index += 1

    return_contour = np.empty((index, 1, 2), dtype=int)
    for index, contour in enumerate(temp_contour):
        return_contour[index, 0] = contour
    return return_contour


def point_close_to_array(point, array_of_contours):
    if array_of_contours:
        for contour in array_of_contours:
            for old_point in contour:
                if points_too_close(old_point, point):
                    return True
    else:
        return False


def points_too_close(first_point, second_point):
    if abs(first_point[0] - second_point[0]) < PROXIMITY_PIX and abs(first_point[1] - second_point[1]) < PROXIMITY_PIX:
        return True
    else:
        return False


def get_slope_contour(point_a, point_b):
    """Get the value of the slope between 2 points"""
    if point_a[0] - point_b[0]:
        slope = (point_a[1] - point_b[1]) / (point_a[0] - point_b[0])
    else:
        slope = INFINITY_SLOPE
    if slope > INFINITY_SLOPE:
        slope = INFINITY_SLOPE
    elif slope < -INFINITY_SLOPE:
        slope = -INFINITY_SLOPE
    return slope