import time
from tools import pulse_in
from machine import Pin


def get_ultrasonic_distance(echo: Pin, trigger: Pin):
    trigger.low()
    time.sleep_us(2)
    trigger.high()
    time.sleep_us(10)
    trigger.low()

    delay = pulse_in(echo, max_delay=75_800)

    if delay is None:
        return None
    return delay * 0.01715  # 343m / 2, 343m -> 0.0343cm/us
