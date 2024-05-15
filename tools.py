import time

import math
from machine import Pin

MOTION_SENSOR_WAIT_TIME = 6  # 5s waiting time PIR motion sensor
MOTION_SENSOR_FREQUENCY = 10

RIGHT_SENSOR_NEXT_DATA_WAIT_TIME = 5
RIGHT_MAX_LIMIT = 500  # 5m

NORMAL_FRONT_DISTANCE = 45  # 60cm
FRONT_DISTANCE_BUFFER = 5  # 5cm
NORMAL_FRONT_DISTANCE_LOWER_LIMIT = 25
NORMAL_FRONT_DISTANCE_UPPER_LIMIT = NORMAL_FRONT_DISTANCE + FRONT_DISTANCE_BUFFER
NORMAL_LEFT_DISTANCE = 75  # 75cm

COVER_MAX_MOVE_TIME = 5
COVER_MAX_DISTANCE = 400  # 4m

CORRECTION_ANGLE = 0

RIGHT_ANGLE_ROTATION_TIME = .8
ROTATION_SPEED = int(65535 * 0.65)

rotation_buffer_angle = 5
rotation_angle = 90
rotation_speed = 65534 * 0.45

FORWARD = '1'
BACKWARD = '2'
LEFT = '3'
RIGHT = '4'
STOP = '0'


MQ2_SMOKE_THRESHOLD = 800
MQ2_LPG_THRESHOLD = 250


def pulse_in(pin: Pin, max_delay: int = 2_000_000):
    is_time_out = False
    signal_off = signal_on = time.ticks_us()
    s_time = time.ticks_us()

    def check_delay():
        nonlocal is_time_out
        if time.ticks_diff(time.ticks_us(), s_time) > max_delay:
            is_time_out = True

    s_time = time.ticks_us()
    while pin.value() == 0 and not is_time_out:
        signal_off = time.ticks_us()
        check_delay()
    while pin.value() == 1 and not is_time_out:
        signal_on = time.ticks_us()
        check_delay()
    if is_time_out:
        return None
    return signal_on - signal_off


def calculate_heading(ax, ay, az, cx, cy, cz) -> float:
    hx = cy * az - cz * ay
    hy = cz * ax - cx * az
    hz = cx * ay - cy * ax

    inv_h = 1 / ((hx ** 2 + hy ** 2 + hz ** 2) ** 0.5)
    inv_a = 1 / ((ax ** 2 + ay ** 2 + az ** 2) ** 0.5)

    hx *= inv_h
    hy *= inv_h
    hz *= inv_h

    ax *= inv_a
    az *= inv_a

    mag_y = az * hx - ax * hz

    rad = math.atan2(hy, mag_y)

    angle = rad * 180 / math.pi
    if angle < 0:
        angle += 360
    return angle


def _check_angle(angle: float) -> float:
    if angle < 0:
        angle += 360
    return angle % 360


def _verify_angle(initial: float, current: float, buffer: float = None, rot_angle: int = None,
                  slack: bool = True, approach: int = 1) -> int:
    if buffer is None:
        buffer = rotation_buffer_angle
    if rot_angle is None:
        rot_angle = rotation_angle

    def verify(u, l_):
        if u < current:
            return -1
        elif l_ > current:
            return 1
        return 0

    ul = _check_angle(initial + rot_angle + buffer)
    ll = _check_angle(ul - 2 * buffer)

    if not slack:
        if approach == 1:
            ul = _check_angle(ul - buffer)
        else:
            ll = _check_angle(ll + buffer)

    if ll > ul:
        ul = _check_angle(ul + 180)
        ll = _check_angle(ll + 180)
        current = _check_angle(current + 180)
    return verify(ul, ll) * approach


def __verify_angle(initial: float, current: float, buffer: float = None, rot_angle: int = None,
                   slack: bool = True, approach: int = 1) -> int:
    if buffer is None:
        buffer = rotation_buffer_angle
    if rot_angle is None:
        rot_angle = rotation_angle

    resultant_angle = initial + rot_angle
    resultant_angle = resultant_angle % 360
    lower_bound = resultant_angle - buffer
    upper_bound = resultant_angle + buffer

    if not slack:
        if approach == 1:
            lower_bound += buffer
        else:
            upper_bound -= buffer

    if lower_bound <= current <= upper_bound:
        return 0
    elif current < lower_bound:
        return 1
    else:
        return -1


def verify_angle(initial: float, current: float, buffer: float = None, rot_angle: int = None,
                 slack: bool = True, approach: int = 1) -> int:
    def verify(u, l_, c) -> int:
        if c < l_:
            return 1
        elif c > u:
            return -1
        return 0

    if buffer is None:
        buffer = rotation_buffer_angle
    if rot_angle is None:
        rot_angle = rotation_angle

    if initial >= 250 and approach == 1:
        if current < 112:
            current += 360
    elif initial < 112 and approach != 1:
        if initial <= 112:
            initial += 360
        if current <= 112:
            current += 360

    if approach == 1:
        ul = initial + rot_angle + buffer
        # approach is in increasing order add buffer so,
        # add nothing is slack is true or else add buffer so, it reaches actual angle
        ll = ul - (2 * buffer) + ((1 - int(slack)) * buffer)
    else:
        ll = initial - rot_angle - buffer
        ul = ll + (2 * buffer) - ((1 - int(slack)) * buffer)
    return verify(ul, ll, current) * approach


if __name__ == '__main__':
    verify_angle(50, 65)
