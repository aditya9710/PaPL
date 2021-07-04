from rectify import get_abs_slope
from rectify import TOLERANCE

# tolerance used to check whether position in x between 2 points are the same
TOLERANCE = 10
# ratio of the empty space between 2 tiles to the size of the tile
# both should be 0.1 for 2.jpg
# With the "placing tile" used in the exercices book it is 0.2 and 0.3, respectively
HORIZONTAL_SPACE_TO_SIZE_RATIO = 0.2
VERTCAL_SPACE_TO_SIZE_RATIO = 0.3


def sort_to_grids(object_rectified, tile_library):
    """'Try to sort all the frames in one or several grids so that they an order
    and we can build the VPL program from it."""
    grid = []
    ordered_positions = []
    contour_of_positions = []
    contour_list = object_rectified.contours.copy()
    for trials in range(len(contour_list)):
        current_min_tile, position = min_tile(contour_list, object_rectified.contours)
        ordered_positions.append(position)
        contour_of_positions.append(object_rectified.contours[position])

        contour_list.remove(current_min_tile)

    # grid.append([0, 0])
    # grid_contours = [contour_of_positions[0]]
    # contour_of_positions.remove(contour_of_positions[0])
    # nb_trials = 0
    # while len(contour_of_positions):
    #     for contour in contour_of_positions:
    #         for index_grid, grid_ctr in enumerate(grid_contours):
    #             if [grid[index_grid][0], grid[index_grid][1] + 1] not in grid:
    #                 if abs(get_abs_slope(contour[0], contour[1]) - get_abs_slope(contour[0], grid_ctr[0])) < TOLERANCE:
    try:
        diff_x = abs(contour_of_positions[0][2][0] - contour_of_positions[0][0][0]) * (1 + HORIZONTAL_SPACE_TO_SIZE_RATIO)
        diff_y = abs(contour_of_positions[0][2][1] - contour_of_positions[0][0][1]) * (1 + VERTCAL_SPACE_TO_SIZE_RATIO)
    except IndexError:
        return grid, ordered_positions

    if not (diff_x and diff_y):
        return grid, ordered_positions

    for index, position in enumerate(ordered_positions):
        if position == ordered_positions[0]:
            grid.append([0, 0])
        else:
            grid.append(find_position(contour_of_positions[index], contour_of_positions[0][0], diff_x, diff_y))
    # orientation = find_grid_orientation(grid, object_rectified, ordered_positions)

    min_x = 0
    min_y = 0
    for coordinate in grid:
        if coordinate[0] < min_y:
            min_y = coordinate[0]
        if coordinate[1] < min_x:
            min_x = coordinate[1]

    if min_x:
        for coordinate in grid:
            coordinate[1] -= min_x
    if min_y:
        for coordinate in grid:
            coordinate[0] -= min_y

    # print(ordered_positions)
    # print(grid)
    return grid, ordered_positions


def min_tile(contours_list, list_copy):
    """Look for the upper leftmost tile in the image"""
    position = 0

    xy_coord = contours_list[0][0]

    if len(contours_list) >= 1:
        # possible_xy_coord is the Tile with least x-coordinate value
        possible_xy_coord = min(point for point in (min(contour for contour in contours_list)))
        for index, list in enumerate(contours_list):
            for i in range(len(list)):
                # To check least x-coordinate in the range of +/- TOLERANCE with the least y-coordinate as well
                if (list[i][0] < possible_xy_coord[0] + TOLERANCE) and (list[i][0] > possible_xy_coord[0] - TOLERANCE):
                    if list[i][1] < possible_xy_coord[1]:
                        xy_coord = [list[i][0], list[i][1]]
                        possible_xy_coord = xy_coord
                    # If contours_list is left with only one list in it
                    else:
                        xy_coord = possible_xy_coord

        # To find position of min tile in Actual Contour List
        for index, list in enumerate(list_copy):
            if xy_coord in list:
                position = index
        return list_copy[position], position


def find_position(position_contour, origin_contour_upper_leftmost_point, diff_x, diff_y):
    # Look for the upper left point index
    upper_leftmost_point = [position_contour[0][0], position_contour[0][1]]
    for index, point in enumerate(position_contour):
        if point[0] + point[1] < upper_leftmost_point[0] + upper_leftmost_point[1]:
            upper_leftmost_point = point

    pos_x = round((upper_leftmost_point[0] - origin_contour_upper_leftmost_point[0]) / diff_x)
    pos_y = round((upper_leftmost_point[1] - origin_contour_upper_leftmost_point[1]) / diff_y)

    return [pos_y, pos_x]


def find_grid_orientation(grid, rectified_object, position_list):
    event_tiles = ["add tile", "default_lib", "Button_Bottom", "Button_Center", "Button_Left", "Button_Right",
                   "Button_Top", "Clap", "Event_Color_Blue", "Event_Color_Green", "Event_Color_Red",
                   "Event_Color_Yellow", "Ground_Black_White", "Ground_Black", "Ground_Edge", "Ground_White_Black",
                   "Ground_White", "Obstacle_Front", "Obstacle_Right", "Obstacle_Left"]
    orientation = "Default"
    max_events = 0
    events_left = 0
    events_right = 0
    events_top = 0
    events_bottom = 0
    max_row = 0
    max_column = 0

    # Check if all tiles in 1st column are events, i.e. events_left
    for index, list in enumerate(grid):
        if list[1] == 0:
            column_tile = rectified_object.tiles[position_list.index(index)]
            # print("Column Tile: " + column_tile)
            if column_tile in event_tiles:
                events_left += 1
                if events_left > max_events:
                    max_events = events_left
                    orientation = "Left"
        # Meanwhile, to find number of rows in the grid
        if list[0] > max_row:
            max_row = list[0]

    # Check if all tiles in 1st row are events, i.e. events_top
    for index, list in enumerate(grid):
        if list[0] == 0:
            row_tile = rectified_object.tiles[position_list.index(index)]
            # print("Row Tile: " + row_tile)
            if row_tile in event_tiles:
                events_top += 1
                if events_top > max_events:
                    max_events = events_top
                    orientation = "Top"
        # Meanwhile, to find number of columns in the grid
        if list[1] > max_column:
            max_column = list[1]

    # Check if all tiles in last row, i.e events_bottom
    for index, list in enumerate(grid):
        if list[0] == max_row:
            row_tile = rectified_object.tiles[position_list.index(index)]
            if row_tile in event_tiles:
                events_bottom += 1
                if events_bottom > max_events:
                    max_events = events_bottom
                    orientation = "Bottom"

    # Check if all tiles in last column, i.e. events right
    for index, list in enumerate(grid):
        if list[1] == max_column:
            column_tile = rectified_object.tiles[position_list.index(index)]
            if column_tile in event_tiles:
                events_right += 1
                if events_right > max_events:
                    max_events = events_right
                    orientation = "Right"

    if max_events == 0:
        orientation = "No events"
    # print(orientation)
    return orientation