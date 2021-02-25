import os
import sys
import time
import tkinter as tk

import cv2
import serial.tools.list_ports
from PIL import Image

import bridge_thymio_python as btp
import bridge_scratch_jr as bsp
import save_load
import session
import tk_gui
from Thymio import Thymio
from session import Module
from session import States

if __name__ == '__main__':
    # Can be useful if we want to work simultaneously with several sessions
    # Need to be implemented
    my_sessions = [session.Session()]
    working_session = 0
    th = None

    # GUI Initialization
    root = tk.Tk()
    myApp = tk_gui.Interface(root, my_sessions[working_session], "PaPL")
    root.protocol("WM_DELETE_WINDOW", myApp.on_delete)

    while True:
        if my_sessions[working_session].state == States.GAME_CHOICE:
            while my_sessions[working_session].state == States.GAME_CHOICE:
                my_sessions[working_session].reset()
                module = myApp.get_choice("Game choice", "Choose your game", ["Thymio", "ScratchJr", "Exit"])
                if module == "Thymio":
                    my_sessions[working_session].module_logo = Image.open(os.getcwd() + "/data/logo/thymio_logo.png")
                    my_sessions[working_session].module = Module.THYMIO
                    tile_library, tile_library_resized, tile_type = save_load.load_data(Module.THYMIO)
                    if not th:
                        ports = serial.tools.list_ports.comports()
                        device = None
                        for port in ports:
                            if 'Thymio' in port.description:
                                device = port.device
                        if device:
                            th = Thymio.serial(port=device, refreshing_rate=0.1)
                            dir(th)
                            time.sleep(1)
                            variables = th.variable_description()
                            time.sleep(2)
                        else:
                            myApp.show_info("Info", "No thymio has been found. Please connect a thymio.")
                            continue
                elif module == "ScratchJr":
                    my_sessions[working_session].module_logo = Image.open(os.getcwd() + "/data/logo/scratchjr_logo.png")

                    for root, dirs, files in os.walk("C:\\"):
                        if 'ScratchJr.exe' in files:
                            path_scratch_exe = os.path.join(root, 'ScratchJr.exe')
                            path_scratch_exe = path_scratch_exe.replace("\\", "/")
                            break
                    for root, dirs, files in os.walk("C:\\"):
                        if 'scratchjr.sqllite' in files:
                            path_scratch_sql = os.path.join(root)
                            path_scratch_sql = path_scratch_sql.replace("\\", "/")
                            break
                    for root, dirs, files in os.walk(path_scratch_sql):
                        if not 'scratchjr.sqllite.restore' in files:
                            bsp.create_sql_file(path_scratch_sql)
                    os.system(path_scratch_exe)
                    my_sessions[working_session].module = Module.SCRATCH
                    tile_library, tile_library_resized, tile_type = save_load.load_data(Module.SCRATCH)

                    scenery = myApp.get_choice("Scenery choice", "Select a scenery", ["Farm", "Park", "Fall",
                                                                                      "BeachDay"])
                    my_sessions[working_session].scenery = scenery + ".svg"
                    my_sessions[working_session].character = myApp.get_choice("Character choice", "Select a character",
                                                                              ["Tic", "Tac", "Toc", "Dragon", "Fairy",
                                                                               "Wizard"])
                elif module =="Exit":
                    my_sessions[working_session].state = States.EXIT
                    break
                else:
                    continue
                my_sessions[working_session].tile_library = tile_library
                my_sessions[working_session].tile_library_resized = tile_library_resized
                my_sessions[working_session].tile_type = tile_type
                my_sessions[working_session].state = States.IMG_SOURCE_CHOICE

        elif my_sessions[working_session].state == States.IMG_SOURCE_CHOICE:
            while my_sessions[working_session].state == States.IMG_SOURCE_CHOICE:
                source_choice = myApp.get_choice("Source choice",
                                                 "Choose the source between webcam, image files or capture mode",
                                                 ["webcam", "image files", "capture", "exit"])
                if source_choice == "webcam":
                    my_sessions[working_session].state = States.WEBCAM_CHOICE
                elif source_choice == "image files":
                    my_sessions[working_session].state = States.IMG_FILE_MAIN
                elif source_choice == "capture":
                    my_sessions[working_session].state = States.CAPTURE_CHOICE
                elif source_choice == "exit":
                    my_sessions[working_session].state = States.EXIT
                else:
                    my_sessions[working_session].state = States.EXIT

        elif my_sessions[working_session].state == States.WEBCAM_CHOICE:
            while my_sessions[working_session].state == States.WEBCAM_CHOICE:
                # cap_choice = myApp.get_integer("Webcam number", "Please enter the webcam number")
                cap_choice = 0
                try:
                    cap = cv2.VideoCapture(int(cap_choice))
                    if cap.isOpened():
                        my_sessions[working_session].state = States.WEBCAM_MAIN
                except TypeError:
                    my_sessions[working_session].state = States.IMG_SOURCE_CHOICE

        elif my_sessions[working_session].state == States.WEBCAM_MAIN:
            my_sessions[working_session].current_event_tile = None
            if my_sessions[working_session].module == Module.THYMIO:
                btp.init_thymio(th)
            while my_sessions[working_session].state == States.WEBCAM_MAIN:
                ret, image = cap.read()
                if not ret:
                    print("The program was not able to capture image from the webcam")
                    my_sessions[working_session].state == States.WEBCAM_CHOICE
                else:
                    image = cv2.flip(image, 1)
                    image = cv2.resize(image, (1200, 900))
                    session.interpret_image(image, my_sessions[working_session])
                    try:
                        myApp.update_gui(image, program=my_sessions[working_session].best_program)
                    except tk.TclError:
                        sys.exit(0)

        elif my_sessions[working_session].state == States.LAUNCH_WEBCAM:
            while my_sessions[working_session].state == States.LAUNCH_WEBCAM:
                try:
                    myApp.update_gui(image, program=my_sessions[working_session].best_program)
                except tk.TclError:
                    sys.exit(0)
                if my_sessions[working_session].program_tile.any():
                    session.save_file(my_sessions[working_session].best_program)
                    my_sessions[working_session].state = States.EXECUTE_WEBCAM
                else:
                    my_sessions[working_session].state = States.WEBCAM_MAIN

        elif my_sessions[working_session].state == States.EXECUTE_WEBCAM:
            flag = False
            while my_sessions[working_session].state == States.EXECUTE_WEBCAM:
                try:
                    myApp.update_gui(image, program=my_sessions[working_session].best_program)
                except tk.TclError:
                    sys.exit(0)
                if my_sessions[working_session].module == Module.THYMIO:
                    flag = session.execute(flag, my_sessions[working_session], th=th)
                else:
                    flag = session.execute(flag, my_sessions[working_session], path_to_scratch=path_scratch_sql)

        elif my_sessions[working_session].state == States.IMG_FILE_MAIN:
            my_sessions[working_session].current_event_tile = None
            if my_sessions[working_session].module == Module.THYMIO:
                btp.init_thymio(th)
            flag = False
            while my_sessions[working_session].state == States.IMG_FILE_MAIN:
                if not flag:
                    file_path = myApp.get_text("Path to file", "Enter the file address")
                    if file_path == "q" or file_path == "None":
                        my_sessions[working_session].state = States.IMG_SOURCE_CHOICE
                        break
                    try:
                        image = cv2.imread("data/" + file_path)
                    except TypeError:
                        my_sessions[working_session].state = States.IMG_SOURCE_CHOICE
                    if image is None:
                        print("Invalid or missing file.")
                    else:
                        flag = True
                        image = cv2.resize(image, (1200, 900))
                        session.interpret_image(image, my_sessions[working_session])
                try:
                    myApp.update_gui(image, program=my_sessions[working_session].best_program)
                except tk.TclError:
                    sys.exit(0)

        elif my_sessions[working_session].state == States.LAUNCH_FILE:
            while my_sessions[working_session].state == States.LAUNCH_FILE:
                try:
                    myApp.update_gui(image, program=my_sessions[working_session].best_program)
                except tk.TclError:
                    sys.exit(0)
                if my_sessions[working_session].program_tile.any():
                    session.save_file(my_sessions[working_session].best_program)
                    my_sessions[working_session].state = States.EXECUTE_FILE
                else:
                    my_sessions[working_session].state = States.IMG_FILE_MAIN

        elif my_sessions[working_session].state == States.EXECUTE_FILE:
            flag = False
            while my_sessions[working_session].state == States.EXECUTE_FILE:
                try:
                    myApp.update_gui(image, program=my_sessions[working_session].best_program)
                except tk.TclError:
                    sys.exit(0)
                if my_sessions[working_session].module == Module.THYMIO:
                    flag = session.execute(flag, my_sessions[working_session], th=th)
                else:
                    flag = session.execute(flag, my_sessions[working_session], path_to_scratch=path_scratch_sql)

        elif my_sessions[working_session].state == States.CAPTURE_CHOICE:
            while my_sessions[working_session].state == States.CAPTURE_CHOICE:
                cap_choice = myApp.get_integer("Webcam number", "Please enter the webcam number")
                try:
                    cap = cv2.VideoCapture(int(cap_choice))
                    if cap.isOpened():
                        my_sessions[working_session].state = States.CAPTURE_MAIN
                except TypeError:
                    my_sessions[working_session].state = States.IMG_SOURCE_CHOICE

        elif my_sessions[working_session].state == States.CAPTURE_MAIN:
            my_sessions[working_session].current_event_tile = None
            if my_sessions[working_session].module == Module.THYMIO:
                btp.init_thymio(th)
            while my_sessions[working_session].state == States.CAPTURE_MAIN:
                ret, image = cap.read()
                if not ret:
                    print("The program was not able to capture image from the webcam")
                    my_sessions[working_session].state == States.CAPTURE_CHOICE
                else:
                    image = cv2.resize(image, (1200, 900))
                    session.interpret_image(image, my_sessions[working_session])
                    try:
                        myApp.update_gui(image, program=my_sessions[working_session].best_program)
                    except tk.TclError:
                        sys.exit(0)

        elif my_sessions[working_session].state == States.LAUNCH_CAPTURE:
            while my_sessions[working_session].state == States.LAUNCH_CAPTURE:
                try:
                    myApp.update_gui(image, program=my_sessions[working_session].best_program)
                except tk.TclError:
                    sys.exit(0)
                if my_sessions[working_session].program_tile.any():
                    session.save_file(my_sessions[working_session].best_program)
                    my_sessions[working_session].state = States.EXECUTE_CAPTURE
                else:
                    my_sessions[working_session].state = States.CAPTURE_MAIN

        elif my_sessions[working_session].state == States.EXECUTE_CAPTURE:
            flag = False
            while my_sessions[working_session].state == States.EXECUTE_CAPTURE:
                try:
                    myApp.update_gui(image, program=my_sessions[working_session].best_program)
                except tk.TclError:
                    sys.exit(0)
                if my_sessions[working_session].module == Module.THYMIO:
                    flag = session.execute(flag, my_sessions[working_session], th=th)
                else:
                    flag = session.execute(flag, my_sessions[working_session], path_to_scratch=path_scratch_sql)

        elif my_sessions[working_session].state == States.EXIT:
            print("fermeture du programme")
            try:
                root.destroy()
            except tk.TclError:
                pass  # root is already destroyed
            sys.exit(0)

        else:
            myApp.show_info("Unknown error", "Session " + str(working_session) + " has stopped working. "
                            "Please restart the program")
            sys.exit(0)