import lsm303
import tools
from machine import I2C, Pin


class My2C:
    def __init__(self, *args, **kwargs):
        self.i2c = I2C(*args, **kwargs)

    def write_i2c_block_data(self, address, register, data):
        self.i2c.writeto_mem(address, register, bytes(data))

    def read_i2c_block_data(self, address, register, num_bytes):
        return self.i2c.readfrom_mem(address, register, num_bytes)


class Compass:
    def __init__(self, id_: int, scl: Pin, sda: Pin):
        self.Ax = self.Ay = self.Az = self.Cx = self.Cy = self.Cz = 0
        self._angle = 0
        self.i2c = My2C(id_, scl=scl, sda=sda)
        self.compass = lsm303.LSM303(self.i2c)

    @property
    def get_angle(self) -> float:
        self.get_hall_effect()
        self.get_acceleration()
        return self.calculate_headings()

    @property
    def angle(self) -> float:
        return self.calculate_headings()

    @property
    def corrected_angle(self):
        return (self.angle + tools.CORRECTION_ANGLE) / 360

    def calculate_headings(self) -> float:
        angle = tools.calculate_heading(self.Ax, self.Ay, self.Az,
                                        self.Cx, self.Cy, self.Cz)
        return angle

    def get_acceleration(self) -> (float, float, float):
        self.Ax, self.Ay, self.Az = self.compass.read_accel()
        return self.Ax, self.Ay, self.Az

    def get_hall_effect(self) -> (float, float, float):
        self.Cx, self.Cy, self.Cz = self.compass.read_mag()
        return self.Cx, self.Cy, self.Cz


if __name__ == '__main__':
    i2c = My2C(0, scl=Pin(5), sda=Pin(4))

    compass = lsm303.LSM303(My2C)
