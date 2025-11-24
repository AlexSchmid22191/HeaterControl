import threading
import time

import serial

from src.Drivers.BaseClasses import AbstractSensor


class Keithley2000(AbstractSensor, serial.Serial):
    mode = None

    def __init__(self, _port):
        super().__init__(_port, timeout=1.5)
        self.com_lock = threading.Lock()
        time.sleep(1)
        self.write('*RST\n'.encode())

    def get_sensor_value(self):
        pass

    def close(self):
        serial.Serial.close(self)


class Keithley2000Temp(Keithley2000):
    mode = 'Temperature'

    def __init__(self, _port):
        super().__init__(_port)
        with self.com_lock:
            self.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?\n'.encode())
            return float(self.read(16).decode())


class Keithley2000Volt(Keithley2000):
    mode = 'Voltage'

    def __init__(self, _port):
        super().__init__(_port)
        with self.com_lock:
            self.write(":FUNC 'VOLT'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?\n'.encode())
            return float(self.read(16).decode()) * 1000
