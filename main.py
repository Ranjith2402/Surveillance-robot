import tools
import PIR
import ESPCommunicator as Esp32
import Motor_handler as Robot
from tools import FORWARD, BACKWARD, LEFT, RIGHT, STOP
from UltraSonic import get_ultrasonic_distance
from mq2 import MQ2
import time
from machine import Pin, Timer
from Servo import Servo

Robot.stop()
mv_dir = '0'

red_led = Pin(12, Pin.OUT)
green_led = Pin(13, Pin.OUT)

red_led.low()
green_led.low()

trig = Pin(18, Pin.OUT)
r_trig = Pin(9, Pin.IN)
l_trig = Pin(8, Pin.IN)
left = Pin(19, Pin.IN, Pin.PULL_DOWN)
right = Pin(8, Pin.IN, Pin.PULL_DOWN)
front = Pin(21, Pin.IN, Pin.PULL_DOWN)

PIR1 = Pin(10, Pin.IN, Pin.PULL_DOWN)
PIR2 = Pin(11, Pin.IN, Pin.PULL_DOWN)

LPG = Pin(22, Pin.IN, Pin.PULL_DOWN)

SPEED = 65535 * 0.75  # 75% of full speed

ultrasonic_sensors = {'Left': left,
                      'Right': right,
                      'Front': front,
                      'Trigger': trig,
                      'R_Trig': r_trig,
                      'L_Trig': l_trig}

isAuto = False  # need to be turned on by client
isLPG_announced = False
isStarted = False

right_distances = []  # left wall follower
front_distance = left_distance = None
is_right_receiving = False
is_other_receiving = False


last_right_measure_time = time.time()
last_pir_measure_time = time.time()
is_1st_pir = True

is_moving_till_wall = True

mq2_sensor = MQ2(26, base_voltage=5)


pan = Servo(Pin(6))
tilt = Servo(Pin(7))


def move_till_wall():
    global isStarted, right_distances
    isStarted = False
    while not isStarted:
        read_serial()
        Robot.move(int(SPEED))
        get_proximity()
        if front_distance is not None:
            if front_distance < tools.NORMAL_FRONT_DISTANCE_LOWER_LIMIT:
                isStarted = True
                break
        else:
            isStarted = True
            break
    right_distances = []


def get_right_distance(_=None):
    global is_right_receiving
    while is_other_receiving:
        time.sleep(1)
    is_right_receiving = True
    d = get_ultrasonic_distance(ultrasonic_sensors['Right'], ultrasonic_sensors['R_Trig'])
    if isAuto and d is not None:
        right_distances.append(d)
    is_right_receiving = False


def get_proximity():
    global is_other_receiving, front_distance, left_distance
    while is_right_receiving:
        time.sleep(.1)
    is_other_receiving = True
    front_distance = get_ultrasonic_distance(ultrasonic_sensors['Front'], ultrasonic_sensors['Trigger'])
    left_distance = get_ultrasonic_distance(ultrasonic_sensors['Left'], ultrasonic_sensors['L_Trig'])
    is_other_receiving = False


def read_lpg():
    lpg = []
    smoke = []

    for _ in range(3):
        lpg.append(mq2_sensor.readLPG())
        smoke.append(mq2_sensor.readSmoke())
    if lpg:
        lpg_ = sum(lpg) / len(lpg)
        if lpg_ > tools.MQ2_LPG_THRESHOLD:
            Esp32.send('ALERT:LPG:Lpg gas leak found')
    if smoke:
        smoke_ = sum(smoke) / len(smoke)
        if smoke_ > tools.MQ2_SMOKE_THRESHOLD:
            Esp32.send('ALERT:FIRE:Robot detected smoke')


def scan_pir(_=None):
    Robot.stop()
    for k in range(2):
        for _ in range(2):
            red_led.high()
            green_led.high()
            time.sleep(0.3)
            red_led.low()
            green_led.low()
            time.sleep(0.2)
        time.sleep(4)  # wait for 4s for PIR sensor to settle
        out = PIR.detect_motion(PIR1, PIR2)
        if out != 0:
            if out == 2:
                pass
                # Robot.turn_right_by_90()
                # Robot.turn_right_by_90()
            Esp32.send('ALERT:THEFT:Motion sensor detected some movement!')
        if k == 0:
            Robot.turn_right_by_90(SPEED)
    Robot.turn_left_by_90(SPEED)
    timer = Timer()
    timer.init(freq=1, mode=Timer.ONE_SHOT, callback=read_lpg)


def read_serial():
    texts = Esp32.read()
    if texts is None:
        return
    texts = texts.split('\n')
    for text in texts:
        print(text)
        serial_action(text)


def serial_action(text: str):
    global isAuto, SPEED, mv_dir, is_moving_till_wall, is_1st_pir
    if text.startswith('MODE:'):
        isAuto = not isAuto
        is_moving_till_wall = True
    if text.startswith('WEB:'):
        new_text = text[4:]
        if new_text.startswith('MOVE:') and not isAuto:
            mv_dir = new_text[5:]
            if mv_dir == STOP:
                Robot.stop()
            elif mv_dir == FORWARD:
                Robot.move(int(SPEED))
            elif mv_dir == BACKWARD:
                Robot.move_back(int(SPEED))
            elif mv_dir == RIGHT:
                Robot.turn_right(int(SPEED))
            elif mv_dir == LEFT:
                Robot.turn_left(int(SPEED))
        elif new_text.startswith('SPEED'):
            try:
                spd = int(new_text[6:])
                SPEED = spd / 255 * 65534
            except ValueError:
                pass
        elif new_text.startswith('MODE'):
            isAuto = not isAuto
            is_moving_till_wall = True

    elif text.startswith('PAN:'):
        angle = int(text[4:])
        pan.write(angle)
    elif text.startswith('TILT:'):
        angle = int(text[5:])
        tilt.write(angle)

    elif text == 'CLIENT:HANDSHAKE':
        Esp32.send('HELLO')
    elif text.startswith('CLIENT:'):
        new_text = text[7:]
        if new_text == 'RESEND':
            Esp32.resend_last_message()
        elif new_text == 'MODE:AUTO':
            isAuto = True
            for _ in range(10):
                green_led.high()
                time.sleep(0.4)
                green_led.low()
                time.sleep(0.4)
        elif text == 'CLIENT:LAUNCH_WEB' or text == 'CLIENT:MODE:MANUAL' or text.startswith('WebSocketClientConnected'):
            isAuto = False
            Robot.stop()
    elif text.startswith('Connecting to'):
        red_led.high()
        time.sleep(.5)
        red_led.low()
        time.sleep(.5)
    elif text.startswith('Connected'):
        green_led.high()
        time.sleep(1)
        green_led.low()
    elif text.startswith('WebSocketClientDisconnected'):
        Robot.stop()
        is_1st_pir = True
    elif 'Camera init failed' in text:
        Esp32.send('ALERT:Camera init failed:Camera initialisation failed check camera connection')
        for _ in range(5000):
            red_led.high()
            time.sleep(0.1)
            red_led.low()
            time.sleep(0.1)
    elif 'Brownout' in text:
        for _ in range(3):
            red_led.high()
            time.sleep(0.05)
            red_led.low()
            time.sleep(0.05)


def main():
    global isAuto, is_moving_till_wall, right_distances, last_pir_measure_time, is_1st_pir
    mq2_sensor.calibrate()
    pan.angle = tilt.angle = 90
    last_pir_measure_time = time.time()
    for _ in range(3):
        red_led.high()
        green_led.high()
        time.sleep(0.2)
        red_led.low()
        green_led.low()
        time.sleep(0.1)
    while True:
        read_serial()
        if isAuto:
            get_proximity()
            Robot.move(int(SPEED))
            t = time.time() - last_pir_measure_time
            if t > tools.MOTION_SENSOR_FREQUENCY:
                if not is_1st_pir:
                    scan_pir()
                is_1st_pir = False
                last_pir_measure_time = time.time()
            if front_distance is not None:
                if front_distance < tools.NORMAL_FRONT_DISTANCE:
                    Robot.stop()
                    Robot.turn_right_by_90(SPEED)
            if left_distance is not None:
                if left_distance > tools.NORMAL_LEFT_DISTANCE:
                    Robot.stop()
                    Robot.turn_left_by_90(SPEED)
        elif mv_dir == '1':
            d = get_ultrasonic_distance(ultrasonic_sensors['Front'], ultrasonic_sensors['Trigger'])
            if d is not None and d < tools.NORMAL_FRONT_DISTANCE:
                Robot.move_back(int(SPEED))
                time.sleep(0.1)
                Robot.stop()  # to protect robot hardware, stops robot hitting the wall in manual mode
                time.sleep(0.2)


if __name__ == '__main__':
    on_board_led = Pin(25, Pin.OUT)
    for i in range(10):
        on_board_led.high()
        if i % 2 == 0:
            red_led.high()
        else:
            green_led.high()
        time.sleep(0.1)
        on_board_led.low()
        if i % 2 == 0:
            red_led.low()
        else:
            green_led.low()
        time.sleep(0.1)
    green_led.low()
    red_led.low()
#     isAuto = True
    try:
        main()
    except Exception as err:
        error = 'ERROR' + str(err.args)
        Esp32.send(error)
        time.sleep(3)  # wait for 3s before sending another message, so it won't merge both message
        Esp32.send('EndError')
