import cv2
import fuse

SIZE_THRESHOLD = 5000


def find_contour_frames(image):
    """Find quadrilateral shapes in the image that are bigger than the threshold defined abow"""
    edges = cv2.Canny(cv2.medianBlur(image, 5), 30, 90)

    # Works better without it
    # kernel = np.ones((3, 3))
    # edges = cv2.dilate(edges, kernel)
    # cv2.imshow("original", image)
    # cv2.imshow("canny", edges)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    # sort the contours from top to bottom then left to right
    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0] + cv2.boundingRect(ctr)[1] * image.shape[1])

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        for point in contour:
            cv2.circle(edges, (point[0][0], point[0][1]), 5, (0, 0, 255))

    contours_frame = []
    for contour in contours:
        contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.01, True)
        for point in contour:
            cv2.circle(edges, (point[0][0], point[0][1]), 5, (0, 0, 255))
        if is_contour_frame(contour):
            contours_frame.append(contour)

    contours_frame = fuse.fuse_points_in_contours(contours_frame)

    for contour in contours_frame:
        for point in contour:
            cv2.circle(edges, (point[0], point[1]), 5, (0, 255, 255), -1)

    return contours_frame


def is_contour_frame(contour):
    """Check whether the contour has 4 point (is a quadrilateral) and is bigger than the threshold"""
    if (contour.size >= 8 and
            abs(cv2.contourArea(contour)) > SIZE_THRESHOLD and
            cv2.isContourConvex(contour)):
        return True
    else:
        return False