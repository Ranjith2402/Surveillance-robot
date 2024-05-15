import time
import tools
import GY511
from machine import PWM, Pin

MOTOR_LEFT = PWM(Pin(14))
MOTOR_LEFT_DIRECTOR = PWM(Pin(15))

MOTOR_RIGHT = PWM(Pin(16))
MOTOR_RIGHT_DIRECTOR = PWM(Pin(17))

compass = GY511.Compass(0, scl=Pin(5), sda=Pin(4))


def stop():
    MOTOR_LEFT.duty_u16(0)
    MOTOR_RIGHT.duty_u16(0)
    MOTOR_RIGHT_DIRECTOR.duty_u16(0)
    MOTOR_LEFT_DIRECTOR.duty_u16(0)


def move(spd: int):
    spd = int(spd)
    MOTOR_LEFT.duty_u16(spd)
    MOTOR_RIGHT.duty_u16(spd)
    MOTOR_RIGHT_DIRECTOR.duty_u16(0)
    MOTOR_LEFT_DIRECTOR.duty_u16(0)


def turn_right_by_90(spd: float):
    spd = int(spd)
    stop()
    time.sleep(0.2)
    initial_angle = compass.get_angle
    is_reached = False
    while True:
        curr = compass.get_angle
        out = tools.verify_angle(initial_angle, curr, slack=is_reached)
        if out == 0:
            stop()
            break
        elif out == -1:
            turn_left(spd)
            is_reached = True
        else:
            turn_right(spd)
    stop()
    time.sleep(0.2)


def turn_left_by_90(spd: float):
    spd = int(spd)
    stop()
    time.sleep(0.2)
    initial_angle = compass.get_angle
    is_reached = False
    while True:
        curr = compass.get_angle
        out = tools.verify_angle(initial_angle, curr, slack=is_reached, approach=-1)
        if out == 0:
            stop()
            break
        elif out == -1:
            turn_right(spd)
            is_reached = True
        else:
            turn_left(spd)
    stop()
    time.sleep(0.2)


def _turn_right_by_90():
    MOTOR_RIGHT_DIRECTOR.duty_u16(0)
    MOTOR_RIGHT.duty_u16(tools.ROTATION_SPEED)

    MOTOR_LEFT_DIRECTOR.duty_u16(tools.ROTATION_SPEED)
    MOTOR_LEFT.duty_u16(0)

    time.sleep(tools.RIGHT_ANGLE_ROTATION_TIME)
    stop()
    time.sleep(0.2)


def _turn_left_by_90():
    MOTOR_RIGHT_DIRECTOR.duty_u16(tools.ROTATION_SPEED)
    MOTOR_RIGHT.duty_u16(0)

    MOTOR_LEFT_DIRECTOR.duty_u16(0)
    MOTOR_LEFT.duty_u16(tools.ROTATION_SPEED)

    time.sleep(tools.RIGHT_ANGLE_ROTATION_TIME)
    stop()
    time.sleep(0.2)


def turn_right(spd: int):
    spd = int(spd)
    MOTOR_LEFT_DIRECTOR.duty_u16(spd)
    MOTOR_LEFT.duty_u16(0)

    MOTOR_RIGHT_DIRECTOR.duty_u16(0)
    MOTOR_RIGHT.duty_u16(spd)


def turn_left(spd: int):
    spd = int(spd)
    MOTOR_RIGHT_DIRECTOR.duty_u16(spd)
    MOTOR_RIGHT.duty_u16(0)

    MOTOR_LEFT_DIRECTOR.duty_u16(0)
    MOTOR_LEFT.duty_u16(spd)


def move_back(spd: int):
    spd = int(spd)
    MOTOR_LEFT.duty_u16(0)
    MOTOR_RIGHT.duty_u16(0)
    MOTOR_RIGHT_DIRECTOR.duty_u16(spd)
    MOTOR_LEFT_DIRECTOR.duty_u16(spd)
