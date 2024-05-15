from machine import PWM, Pin


class Servo:
    def __init__(self, pin: Pin):
        self.pin = PWM(pin)
        self.pin.freq(50)
        self._angle = None

    def write(self, angle: int):
        if angle > 180:
            angle = 180
        elif angle < 0:
            angle = 0
        self._angle = angle
        a = angle / 180 * (2048 * 3) + 2048
        self.pin.duty_u16(int(a))

    def set_angle(self, angle: int):
        self.write(angle)

    @property
    def angle(self) -> int:
        return self._angle

    @angle.setter
    def angle(self, value: int):
        self.write(angle=value)
