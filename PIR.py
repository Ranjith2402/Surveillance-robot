import time
from tools import MOTION_SENSOR_WAIT_TIME
from machine import Pin


def detect_motion(pin1: Pin, pin2: Pin) -> int:
    s_time = time.time()
    while time.time() - s_time <= MOTION_SENSOR_WAIT_TIME:
        if pin1.value() == 1:
            return 1
        if pin2.value() == 1:
            return 2
    return 0
