import threading
import time

import serial

from src.Drivers.BaseClasses import AbstractSensor


class Keithley2000(AbstractSensor):
    mode = None

    def __init__(self, _port):
        self.serial = serial.Serial(_port, timeout=1.5)
        self.com_lock = threading.Lock()
        time.sleep(1)
        self.serial.write('*RST\n'.encode())

    def get_sensor_value(self):
        pass

    def close(self):
        self.serial.close()


class Keithley2000Temp(Keithley2000):
    mode = 'Temperature'

    def __init__(self, _port):
        super().__init__(_port)
        with self.com_lock:
            self.serial.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.serial.write(':read?\n'.encode())
            return float(self.serial.read(16).decode())


class Keithley2000Volt(Keithley2000):
    mode = 'Voltage'

    def __init__(self, _port):
        super().__init__(_port)
        with self.com_lock:
            self.serial.write(":FUNC 'VOLT'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.serial.write(':read?\n'.encode())
            return float(self.serial.read(16).decode()) * 1000
