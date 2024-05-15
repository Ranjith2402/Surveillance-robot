from basemq import BaseMQ


class MQ2(BaseMQ):
    # Clean air coefficient
    MQ2_RO_BASE = float(9.83)

    def __init__(self, pin_data, pin_heater=-1, board_resistance=10, base_voltage=3.3,
                 measuring_strategy=BaseMQ.STRATEGY_ACCURATE):
        # Call superclass to fill attributes
        super().__init__(pin_data, pin_heater, board_resistance, base_voltage, measuring_strategy)

    # Measure liquefied hydrocarbon gas, LPG
    def readLPG(self):
        return self.readScaled(-0.45, 2.95)

    # Measure methane
    def readMethane(self):
        return self.readScaled(-0.38, 3.21)

    # Measure smoke
    def readSmoke(self):
        return self.readScaled(-0.42, 3.54)

    # Measure hydrogen
    def readHydrogen(self):
        return self.readScaled(-0.48, 3.32)

    #  Base RO differs for every sensor family
    def getRoInCleanAir(self):
        return self.MQ2_RO_BASE


if __name__ == '__main__':
    import time
    pin = 26

    sensor = MQ2(pin_data=pin, base_voltage=5)

    print("Calibrating")
    sensor.calibrate()
    print("Calibration completed")
    print("Base resistance:{0}".format(sensor._ro))

    while True:
        print("Smoke: {:.1f}".format(sensor.readSmoke())+" - ", end="")
        print("LPG: {:.1f}".format(sensor.readLPG())+" - ", end="")
        print("Methane: {:.1f}".format(sensor.readMethane())+" - ", end="")
        print("Hydrogen: {:.1f}".format(sensor.readHydrogen()))
        time.sleep(0.5)
