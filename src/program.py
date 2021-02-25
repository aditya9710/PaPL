import cv2
import numpy as np


IMAGE_SIZE = 400
MAX_PROGRAM = 4


def show_best_program(session, tile_size):
    program_tile = np.empty((1, 1), dtype=object)
    if session.best_grid != [] and session.best_tile != []:
        nb_line = max(point[0] for point in session.best_grid) + 1
        nb_column = max(point[1] for point in session.best_grid) + 1
        program_img = np.zeros((tile_size * nb_line, tile_size * nb_column, 3), dtype=np.uint8)
        program_tile = np.resize(program_tile, (nb_line, nb_column))
        for tile, grid in zip(session.best_tile, session.best_grid):
            if tile == '':
                continue
            line = grid[0]
            col = grid[1]
            program_img[tile_size * line:tile_size * (line + 1), tile_size * col:tile_size * (col + 1), :] = \
                session.tile_library[tile]
            program_tile[line, col] = tile

        ratio = IMAGE_SIZE / max([nb_line, nb_column]) / tile_size
        program_img_width = int(program_img.shape[1] * ratio)
        program_img_height = int(program_img.shape[0] * ratio)
        program_img = cv2.resize(program_img, (program_img_width, program_img_height))  # Maybe width and height
        # should be reversed
    else:
        program_img = []

    return program_tile, program_img


def show_rectified_image(rectified_object):
    if len(rectified_object.contours):
        rectified_img = rectified_object.image
        for contour in rectified_object.contours:
            if contour == rectified_object.contours[0]:
                cv2.circle(rectified_img, tuple(contour[0]), 15, (255, 0, 0))
                cv2.circle(rectified_img, tuple(contour[1]), 15, (0, 255, 0))
                cv2.circle(rectified_img, tuple(contour[2]), 15, (0, 0, 255))
                cv2.circle(rectified_img, tuple(contour[3]), 15, (255, 255, 0))
            cv2.circle(rectified_img, tuple(contour[0]), 5, (255, 0, 0), -1)
            cv2.circle(rectified_img, tuple(contour[1]), 5, (0, 255, 0), -1)
            cv2.circle(rectified_img, tuple(contour[2]), 5, (0, 0, 255), -1)
            cv2.circle(rectified_img, tuple(contour[3]), 5, (255, 255, 0), -1)
        ratio = IMAGE_SIZE / max(rectified_img.shape) * 2
        rectified_img_width = int(rectified_img.shape[1] * ratio)
        rectified_img_height = int(rectified_img.shape[0] * ratio)
        rectified_img = cv2.resize(rectified_img, (rectified_img_width, rectified_img_height))  # Maybe width and height
        # should be reversed
        cv2.imshow("rectified image", rectified_img)
    else:
        cv2.destroyWindow("rectified image")