# Must be a multiple of 5
AVERAGE_LENGTH = 20


def update_program(rectified_object, session):
    if len(rectified_object.contours):
        try:
            min_line = min(point[0] for point in rectified_object.grid_list)
            min_column = min(point[1] for point in rectified_object.grid_list)
        except ValueError:  # If the recified_object is empty
            return
        temp_grid_list = []
        temp_tile_list = []
        for average_index in range(len(rectified_object.grid_list)):
            try:
                tile = rectified_object.tiles[rectified_object.grid_order[average_index]]
            except:
                tile = ''
            grid = rectified_object.grid_list[average_index]
            line = grid[0] - min_line
            col = grid[1] - min_column
            temp_tile_list.append(tile)
            temp_grid_list.append([line, col])

        if len(session.average_tile) < AVERAGE_LENGTH:
            session.average_tile.append(temp_tile_list)
            session.average_grid.append(temp_grid_list)
        else:
            for average_index in range(AVERAGE_LENGTH - 1, 0, -1):
                session.average_tile[average_index] = session.average_tile[average_index - 1]
                session.average_grid[average_index] = session.average_grid[average_index - 1]
            session.average_tile[0] = temp_tile_list
            session.average_grid[0] = temp_grid_list
    else:
        update_void_program(session)

    find_best_program(session)

    return


def update_void_program(session):
    if len(session.average_tile) < AVERAGE_LENGTH:
        session.average_tile = []
        session.average_grid = []

    else:
        for average_index in range(AVERAGE_LENGTH - 1, 0, -1):
            session.average_tile[average_index] = session.average_tile[average_index - 1]
            session.average_grid[average_index] = session.average_grid[average_index - 1]
        session.average_tile[0] = []
        session.average_grid[0] = []

    find_best_program(session)

    return


def find_best_program(session):
    max_line = 0
    max_column = 0
    for average_index in range(len(session.average_grid)):
        if session.average_grid[average_index]:
            min_line = min(point[0] for point in session.average_grid[average_index])
            min_column = min(point[1] for point in session.average_grid[average_index])
            nb_line = max(point[0] for point in session.average_grid[average_index]) - min_line + 1
            nb_column = max(point[1] for point in session.average_grid[average_index]) - min_column + 1
            if nb_line > max_line:
                max_line = nb_line
            if nb_column > max_column:
                max_column = nb_column

    session.best_grid = []
    session.best_tile = []

    for no_line in range(max_line):
        for no_column in range(max_column):
            counter = {}
            session.best_grid.append([no_line, no_column])
            for average_index in range(len(session.average_tile)):
                grid_is_found = 0
                for tile_index in range(len(session.average_tile[average_index])):
                    tile = session.average_tile[average_index][tile_index]
                    grid = session.average_grid[average_index][tile_index]
                    if grid != [no_line, no_column]:
                        continue
                    else:
                        grid_is_found = 1
                        if tile in counter:
                            counter[tile] = counter[tile] + 1
                        else:
                            counter[tile] = 1
                if not grid_is_found:
                    if '' in counter:
                        counter[''] = counter[''] + 1
                    else:
                        counter[''] = 1
            if '' in counter:
                counter[''] = counter[''] - AVERAGE_LENGTH / 5
            session.best_tile.append(max(counter, key=lambda k: counter[k]))


def update_program_file(rectified_object, session):
    if len(rectified_object.contours):
        min_line = min(point[0] for point in rectified_object.grid_list)
        min_column = min(point[1] for point in rectified_object.grid_list)
        session.average_tile = []
        session.average_grid = []
        temp_average_tile = []
        temp_average_grid = []
        for object_index in range(len(rectified_object.grid_list)):
            try:
                tile = rectified_object.tiles[rectified_object.grid_order[object_index]]
            except:
                tile = ''
            grid = rectified_object.grid_list[object_index]
            line = grid[0] - min_line
            col = grid[1] - min_column
            temp_average_tile.append(tile)
            temp_average_grid.append([line, col])
        for average_index in range(AVERAGE_LENGTH):
            session.average_grid.append(temp_average_grid)
            session.average_tile.append(temp_average_tile)
        find_best_program(session)
    else:
        session.best_tile = []
        session.best_grid = []