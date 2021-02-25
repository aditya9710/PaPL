import json
import sqlite3
import os
WIDTH = 65
HEIGHT = 100
WIDTH_START = 73
INIT_X = 350
INIT_Y = 1

start_green_flag = [
    "onflag",
    "null"
]
start_on_click = [
    "onclick",
    "null"
]
forward = [
    "forward",
    1
]
backward = [
    "back",
    1
]
up = [
    "up",
    1
]
down = [
    "down",
    1
]
say = [
    "say",
    "hi"
]
end = [
    "endstack",
    "null"
]
forever = [
    "forever",
    "null"
]

file_to_obj_dict = {'Start_On_Click': start_on_click,
                    'Start_Green_Flag': start_green_flag,
                    'Forward': forward,
                    'Backward': backward,
                    'Up': up,
                    'Down': down,
                    'Say': say,
                    'Forever': forever,
                    'End': end
                    }

img_to_thumbnail_dict = {
    'Farm.svg': '_660eb5a74995f827f52cbb67aa38468e.png',
    'Park.svg': '_a3bb61aa38c17ff4d9d17c4fb56693db.png',
    'Fall.svg': '_f9aab3c458f5dbf96b239287c923cb32.png',
    'BeachDay.svg': '_f60e5f0d3558dae0232167330c1bb73f.png'
}


def static_vars(**kwargs):
    """"Decorator used to define static variable in function"""

    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def load_scratch(program, scenery, character, path):
    """Function to update the sql restore file of scratch with the new project"""
    conn = sqlite3.connect(path+'/scratchjr.sqllite.restore')
    data = interpret_prog_scratch(program, scenery, character)
    conn.execute("INSERT INTO PROJECTS (JSON, DELETED, VERSION) VALUES (?, 'NO', 'iOSv01')", (str(data),))
    conn.commit()
    cursor = conn.execute("SELECT seq FROM sqlite_sequence")
    for val in cursor:
        nb_project = int(val[0])
    img = img_to_thumbnail_dict[scenery]
    img = str(nb_project) + img
    thumbnail = {
        "pagecount": 1,
        "md5": img}
    thumbnail_json = json.dumps(thumbnail)
    name = ('Project' + str(nb_project))
    conn.execute("UPDATE PROJECTS set (NAME, THUMBNAIL) = (?, ?) where ID = ?", (str(name), str(thumbnail_json),
                                                                                 nb_project))
    conn.commit()
    conn.close()


@static_vars(pos_x=350, pos_y=1)
def interpret_prog_scratch(program, scenery, character):
    """Interpretation of the program to write in the json part of the sql file"""

    character_id = character + " 1"
    if character == 'Tic':
        character_img = 'Blue.svg'
    elif character == 'Tac':
        character_img = 'Purple.svg'
    elif character == 'Toc':
        character_img = 'Red.svg'
    else:
        character_img = character + ".svg"
    data = {
        "pages": ["page 1"],
        "currentPage": "page 1",
        "page 1": {
            "textstartat": 36,
            "sprites": [character_id],
            "md5": scenery,
            "num": 1,
            "lastSprite": character_id,
            character_id: {
                "shown": True,
                "type": "sprite",
                "md5": character_img,
                "id": character_id,
                "flip": False,
                "name": character,
                "angle": 0,
                "scale": 0.5,
                "speed": 2,
                "defaultScale": 0.5,
                "sounds": ["pop.mp3"],
                "xcoor": 240,
                "ycoor": 180,
                "cx": 110,
                "cy": 160,
                "w": 235,
                "h": 320,
                "homex": 240,
                "homey": 180,
                "homescale": 0.5,
                "homeshown": True,
                "homeflip": False,
                "scripts": []
            },
            "layers": [character_id]
        }
    }
    for index, line in enumerate(program):
        data["page 1"][character_id]["scripts"].insert(index, [])
        for tile in line:
            if tile:
                new_elem = file_to_obj_dict[tile].copy()
                new_elem.extend([interpret_prog_scratch.pos_x, interpret_prog_scratch.pos_y])
                data["page 1"][character_id]["scripts"][index].append(new_elem)
            if tile == 'Button_Center' or tile == 'Button_Top':
                interpret_prog_scratch.pos_x = interpret_prog_scratch.pos_x + WIDTH_START
            else:
                interpret_prog_scratch.pos_x = interpret_prog_scratch.pos_x + WIDTH
        interpret_prog_scratch.pos_x = INIT_X
        interpret_prog_scratch.pos_y = interpret_prog_scratch.pos_y + HEIGHT
    interpret_prog_scratch.pos_x = INIT_X
    interpret_prog_scratch.pos_y = INIT_Y
    data_json = json.dumps(data)

    return data_json


def create_sql_file(path):
    conn = sqlite3.connect(path + '/scratchjr.sqllite.restore')
    conn.execute('''CREATE TABLE PROJECTFILES 
    (MD5        TEXT PRIMARY KEY, 
    CONTENTS    TEXT);''')
    conn.commit()
    conn.execute('''CREATE TABLE PROJECTS 
    (ID         INTEGER PRIMARY KEY AUTOINCREMENT, 
    CTIME       DATETIME DEFAULT CURRENT_TIMESTAMP, 
    MTIME       DATETIME, 
    ALTMD5      TEXT, 
    POS         INTEGER, 
    NAME        TEXT, 
    JSON        TEXT, 
    THUMBNAIL   TEXT, 
    OWNER       TEXT, 
    GALLERY     TEXT, 
    DELETED     TEXT, 
    VERSION     TEXT, 
    ISGIFT      INTEGER DEFAULT 0);''')
    conn.commit()
    conn.execute('''CREATE TABLE USERBKGS 
    (ID     INTEGER PRIMARY KEY AUTOINCREMENT, 
    CTIME   DATETIME DEFAULT CURRENT_TIMESTAMP, 
    MD5     TEXT, 
    ALTMD5  TEXT, 
    WIDTH   TEXT, 
    HEIGHT  TEXT, 
    EXT     TEXT, 
    OWNER   TEXT, 
    VERSION TEXT);''')
    conn.commit()
    conn.execute('''CREATE TABLE USERSHAPES 
    (ID     INTEGER PRIMARY KEY AUTOINCREMENT, 
    CTIME   DATETIME DEFAULT CURRENT_TIMESTAMP, 
    MD5     TEXT, 
    ALTMD5  TEXT, 
    WIDTH   TEXT, 
    HEIGHT  TEXT, 
    EXT     TEXT, 
    NAME    TEXT, 
    OWNER   TEXT, 
    SCALE   TEXT, 
    VERSION TEXT);''')
    conn.commit()
    conn.execute("INSERT INTO PROJECTFILES (MD5, CONTENTS) VALUES ('homescroll.sjr', 'MA==')")
    conn.commit()
    conn.close()