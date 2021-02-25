from enum import Enum, auto
import cv2
import find_frames as ff
import compare_tiles as ct
import rectify
import grids
import average
import program
import datetime
import os
import bridge_thymio_python as btp
import bridge_scratch_jr as bsj


ORIGINAL_TILE_SIZE = 200
RESIZED_TILE_SIZE = 50


class States(Enum):
    GAME_CHOICE = auto()
    IMG_SOURCE_CHOICE = auto()
    WEBCAM_CHOICE = auto()
    CAPTURE_CHOICE = auto()
    WEBCAM_MAIN = auto()
    IMG_FILE_MAIN = auto()
    CAPTURE_MAIN = auto()
    LAUNCH_WEBCAM = auto()
    LAUNCH_FILE = auto()
    LAUNCH_CAPTURE = auto()
    EXECUTE_WEBCAM = auto()
    EXECUTE_FILE = auto()
    EXECUTE_CAPTURE = auto()
    EXIT = auto()


class Module(Enum):
    THYMIO = auto()
    SCRATCH = auto()


def static_vars(**kwargs):
    """"Decorator used to define static variable in function"""

    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


class Session:
    def __init__(self):
        self.state = States.GAME_CHOICE
        self.tile_library = []
        self.tile_library_resized = []
        self.tile_type = []
        self.module = None
        self.module_logo = None
        self.average_grid = []
        self.average_tile = []
        self.best_grid = []
        self.best_tile = []
        self.best_program = []
        self.program_tile = []
        self.current_event_tile = []
        self.scenery = None
        self.character = None

    def reset(self):
        self.state = States.GAME_CHOICE
        self.tile_library = []
        self.tile_library_resized = []
        self.tile_type = []
        self.module = None
        self.module_logo = None
        self.average_grid = []
        self.average_tile = []
        self.best_grid = []
        self.best_tile = []
        self.best_program = []
        self.program_tile = []
        self.current_event_tile = []
        self.scenery = None
        self.character = None


@static_vars(counter=0)
def add_element_to_library(session, element_to_add, name_of_the_element=""):
    """"Add a new element in the library. If no name is given, it uses the name
        "new_element_x" with x being the xth element without name added"""
    if name_of_the_element == "":
        add_element_to_library.counter += 1
        name_of_the_element = "new_element_" + str(add_element_to_library.counter)
    element_to_add = cv2.resize(element_to_add, (ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE))
    session.tile_library.update({name_of_the_element: element_to_add})
    element_to_add = cv2.resize(element_to_add, (RESIZED_TILE_SIZE, RESIZED_TILE_SIZE))
    session.tile_library_resized.update({name_of_the_element: element_to_add})


def interpret_image(image, session):
    """Input : original image and current session
    Make all operations to find the program on the image. In the order :
    1. Look for the tiles contour
    2. Rectify the image such that the frames are horizontal and vertical
    3. Compare the tiles with the tile library
    4. Make a grid out of all previous results
    5. Show the program"""
    # t = time.time()
    contours_frames = ff.find_contour_frames(image)  # ~30-50 ms
    rectified_object = rectify.rectify_image(contours_frames, image, RESIZED_TILE_SIZE)  # ~8-30 ms
    if len(rectified_object.contours):
        rectified_object = ct.compare_tiles(rectified_object, session.tile_library_resized,
                                            session.tile_type, RESIZED_TILE_SIZE)
        # 7'000-10'000 ms
        rectified_object.grid_list, rectified_object.grid_order = \
            grids.sort_to_grids(rectified_object, session.tile_library_resized)
    # print(time.time() - t)

    average.update_program(rectified_object, session)
    session.program_tile, session.best_program = program.show_best_program(session, ORIGINAL_TILE_SIZE)


def save_file(best_program):
    my_path = str(datetime.datetime.now())
    my_path = my_path.replace(":", "")
    my_path = os.getcwd() + "/data/program/" + my_path + ".png"
    cv2.imwrite(my_path, best_program)


def execute(flag, session, path_to_scratch=None, th=None):
    if session.module == Module.THYMIO:
        last_event = btp.thymio_exchange(th, session.program_tile)
        if last_event:
            session.current_event_tile = session.tile_library[last_event]
    else:
        if not flag:
            flag = True
            bsj.load_scratch(session.program_tile, session.scenery, session.character, path_to_scratch)
    return flag