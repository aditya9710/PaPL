import time

FORWARD_SPEED = 250
FORWARD_TURN_SPEED = 100
STOP_SPEED = 0
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
LEDS_OFF = [0, 0, 0]
PROX_THRESHOLD = 1000
NOISE_THRESHOLD = 80
GROUND_WHITE_THRESHOLD = 500
GROUND_BLACK_THRESHOLD = 250
TIME_TIMER = 3
PROX_LL = 0
PROX_ML = 1
PROX_MM = 2
PROX_MR = 3
PROX_RR = 4
PROX_BL = 5
PROX_BR = 6
PROX_GR_L = 0
PROX_GR_R = 1


def static_vars(**kwargs):
    """"Decorator used to define static variable in function"""

    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


@static_vars(time_flag=False, time=0)
def thymio_exchange(th, program):
    """Communication between the Thymio and the program in Python"""
    events_prog = check_event_program(program)
    event = check_event(th, events_prog)
    if event or thymio_exchange.time_flag:
        action = check_program(program, event)
        if action:
            check_actions(th, action)
    return event


def check_actions(th, action):
    """Check if any action must be executed"""
    for act in action:
        if act == 'Action_Color_Red':
            th.set_var_array("leds.top", RED)
        elif act == 'Action_Color_Blue':
            th.set_var_array("leds.top", BLUE)
        elif act == 'Action_Color_Green':
            th.set_var_array("leds.top", GREEN)
        elif act == 'Action_Color_Yellow':
            th.set_var_array("leds.top", YELLOW)
        elif act == 'Motors_Forward':
            th.set_var("motor.left.target", FORWARD_SPEED)
            th.set_var("motor.right.target", FORWARD_SPEED)
        elif act == 'Motors_Backward':
            th.set_var("motor.left.target", 2**16 - FORWARD_SPEED)
            th.set_var("motor.right.target", 2**16 - FORWARD_SPEED)
        elif act == 'Motors_Forward_Left':
            th.set_var("motor.left.target", FORWARD_TURN_SPEED)
            th.set_var("motor.right.target", FORWARD_SPEED)
        elif act == 'Motors_Forward_Right':
            th.set_var("motor.left.target", FORWARD_SPEED)
            th.set_var("motor.right.target", FORWARD_TURN_SPEED)
        elif act == 'Motors_Left':
            th.set_var("motor.left.target", STOP_SPEED)
            th.set_var("motor.right.target", FORWARD_SPEED)
        elif act == 'Motors_Right':
            th.set_var("motor.left.target", FORWARD_SPEED)
            th.set_var("motor.right.target", STOP_SPEED)
        elif act == 'Motors_Stop':
            th.set_var("motor.left.target", STOP_SPEED)
            th.set_var("motor.right.target", STOP_SPEED)
        elif act == 'Action_Timer_3':
            thymio_exchange.time = time.time()
            thymio_exchange.time_flag = True


def check_event(th, events_prog):
    """Check on Thymio if an event happened"""
    for event in events_prog:
        if event == "Button_Center" and th.get_var("button.center"):
            return event
        elif event == "Button_Top" and th.get_var("button.forward"):
            return event
        elif event == "Button_Left" and th.get_var("button.left"):
            return event
        elif event == "Button_Right" and th.get_var("button.right"):
            return event
        elif event == "Button_Bottom" and th.get_var("button.backward"):
            return event
        elif event == "Obstacle_Front" and th.get_var("prox.horizontal", PROX_MM) > PROX_THRESHOLD:
            return event
        elif event == "Obstacle_Left" and th.get_var("prox.horizontal", PROX_ML) > PROX_THRESHOLD:
            return event
        elif event == "Obstacle_Right" and th.get_var("prox.horizontal", PROX_MR) > PROX_THRESHOLD:
            return event
        elif event == "Obstacle_Back_Right" and th.get_var("prox.horizontal", PROX_BR) > PROX_THRESHOLD:
            return event
        elif event == "Obstacle_Back_Left" and th.get_var("prox.horizontal", PROX_BL) > PROX_THRESHOLD:
            return event
        elif event == "Clap" and th.get_var("mic.intensity") > NOISE_THRESHOLD:
            return event
        elif th.get_var("prox.ground.delta", PROX_GR_L) > GROUND_WHITE_THRESHOLD:
            if event == "Ground_White" and th.get_var("prox.ground.delta", PROX_GR_R) > GROUND_WHITE_THRESHOLD:
                return event
            elif event == "Ground_White_Black" and th.get_var("prox.ground.delta", PROX_GR_R) < GROUND_BLACK_THRESHOLD:
                return event
        elif th.get_var("prox.ground.delta", PROX_GR_L) < GROUND_BLACK_THRESHOLD:
            if event == "Ground_Black_White" and th.get_var("prox.ground.delta", PROX_GR_R) > GROUND_WHITE_THRESHOLD:
                return event
            elif event == "Ground_Black" and th.get_var("prox.ground.delta", PROX_GR_R) < GROUND_BLACK_THRESHOLD:
                return event
    else:
        return ""


def check_program(program, event):
    """Return the action linked to the happened events"""
    action = []
    if thymio_exchange.time_flag:
        if time.time() - thymio_exchange.time > TIME_TIMER:
            event = 'Event_Timer'
            thymio_exchange.time_flag = False
    for line in program:
        event_program = line[0]
        if event_program == 'Ground_Edge':
            event_program = 'Ground_Black'
        if event == event_program:
            for index, tile in enumerate(line):
                if index == 0:
                    pass
                else:
                    action.append(tile)
    return action


def check_event_program(program):
    """"return the list of events in the program"""
    event = []
    for line in program:
        event.append(line[0])
    return event


def init_thymio(th):
    """Initialize the Thymio"""
    th.set_var_array("leds.top", LEDS_OFF)
    th.set_var("motor.left.target", STOP_SPEED)
    th.set_var("motor.right.target", STOP_SPEED)
    th.set_var("mic.threshold", 250)
    thymio_exchange.time_flag = False