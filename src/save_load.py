import os
import sys
import cv2
from session import Module, ORIGINAL_TILE_SIZE, RESIZED_TILE_SIZE


ACTION_TILE = ["Action_Color_Blue", "Action_Color_Green", "Action_Color_Red", "Action_Color_Yellow",
               "Motors_Backward", "Motors_Forward", "Motors_Forward_Left", "Motors_Forward_Right",
               "Motors_Left", "Motors_Right", "Motors_Stop"]
EVENT_TILE = ["Button_Bottom", "Button_Center", "Button_Left", "Button_Right", "Button_Top",
              "Event_Color_Blue", "Event_Color_Green", "Event_Color_Red", "Event_Color_Yellow",
              "Ground_Black", "Ground_White", "Ground_Black_White", "Ground_White_Black", "Ground_Edge",
              "Obstacle_Front", "Obstacle_Left", "Obstacle_Right", "Obstacle_Back_Right", "Obstacle_Back_Light",
              "Event_Timer", "Action_Timer_3", "Clap"]
SCRATCH_TILE = ["Start_On_Click", "Start_Green_Flag", "Forward", "Backward", "Up", "Down", "Say", "Forever", "End"]
EVENT = "event"
ACTION = "action"
ACT = "act"
SCRATCH = "scratch"
CUSTOM_TILE = "custom"


def load_data(module):
    """Load the library save in the /data/templ_imgs folder and also sort the tile in the library by type"""
    tile_library = dict()
    tile_library_resized = dict()
    tile_type = {EVENT: [], ACTION: [], ACT: [], SCRATCH: [], CUSTOM_TILE: []}
    if module == Module.THYMIO:
        path = "data/templ_imgs_thymio"
    else:
        path = "data/templ_imgs_scratch"
    # Look for png file in data/templ_imgs and save them and with their name in tile_library
    for file in os.listdir(os.getcwd() + "/" + path):
        if file.endswith(".png"):
            temp_image = cv2.imread(path + "/" + file)
            if temp_image is None:
                sys.exit("can not load library")
                break
            temp_image = cv2.resize(temp_image, (ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE))
            tile_library.update({os.path.splitext(file)[0]: temp_image})
            temp_image = cv2.resize(temp_image, (RESIZED_TILE_SIZE, RESIZED_TILE_SIZE))
            tile_library_resized.update({os.path.splitext(file)[0]: temp_image})

    for key in tile_library:
        if key in EVENT_TILE:
            tile_type[EVENT].append(key)
        elif key in ACTION_TILE:
            tile_type[ACTION].append(key)
        elif key in SCRATCH_TILE:
            tile_type[SCRATCH].append(key)
        else:
            tile_type[CUSTOM_TILE].append(key)

    return tile_library, tile_library_resized, tile_type


def save_data(tile_library, module):
    """save all images in tile_library with their key as name"""
    if module == Module.THYMIO:
        path = "/data/templ_imgs_thymio"
    else:
        path = "/data/templ_imgs_scrtach"
    for key in tile_library:
        cv2.imwrite(os.getcwd() + path + key + ".png", tile_library[key])