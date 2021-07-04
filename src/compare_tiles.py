import cv2
import numpy as np
import session
import time

# works better without any border
FEATURE_EXTRA_SIZE = 0  # round(TILE_SIZE/10)
RED_BLUE_RATIO = 1.2
LIKENESS_THRESHOLD = 0.3
B = 0
G = 1
R = 2


def compare_tiles(object_rectified, tile_library, tile_type, tile_size):
    """compare tiles in the image with the library, now we compare direct in color image and not only the edges, we have
    better results"""

    orientation = [0]  # , 90, 180, 270]
    best_tile = []
    best_orientation = []

    for index_image, image in enumerate(object_rectified.images):

        # crop the rectified image to only have the ROI
        size_crop = (tile_size, tile_size)
        try:
            resized_image = cv2.resize(image, size_crop)
        except:
            object_rectified.images.remove(image)
            object_rectified.contours.remove(object_rectified.contours[index_image])
            continue

        # compare the crop image with the edge tile library in the 4 orientations
        best_lib = ""
        best_angle = 0

        # parameter to find the best result
        best_likeness = 0

        for key in tile_library:
            (h, w) = tile_library[key].shape[:2]
            # center = (w / 2, h / 2)
            # scale = 1
            for angle in orientation:
                # m_rotation = cv2.getRotationMatrix2D(center, angle, scale)  # takes no time
                # edges_library_rot = cv2.warpAffine(tile_library[key], m_rotation, (h, w))  # 0.5-1 ms
                match = cv2.matchTemplate(tile_library[key], resized_image, cv2.TM_CCOEFF_NORMED)  # ~4-7ms
                _, max_val, _, _ = cv2.minMaxLoc(match)

                if max_val > best_likeness:
                    best_likeness = max_val
                    best_lib = key
                    best_angle = angle

        if best_likeness > LIKENESS_THRESHOLD:
            best_tile.append(best_lib)
            best_orientation.append(best_angle)
        else:
            best_tile.append('')
            best_orientation.append(best_angle)

    object_rectified.tiles = best_tile
    object_rectified.orientations = best_orientation

    return object_rectified