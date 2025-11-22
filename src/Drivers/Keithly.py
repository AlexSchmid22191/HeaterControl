import time
import serial
import threading
from src.Drivers.BaseClasses import AbstractSensor


class Keithly2000(AbstractSensor, serial.Serial):
    mode = None

    def __init__(self, port):
        super().__init__(port, timeout=1.5)
        self.com_lock = threading.Lock()
        time.sleep(1)
        self.write('*RST\n'.encode())

    def close(self):
        serial.Serial.close(self)


class Keithly2000Temp(Keithly2000):
    mode = 'Temperature'

    def __init__(self, port):
        super().__init__(port)
        with self.com_lock:
            self.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?\n'.encode())

            return float(self.read(16).decode())


class Keithly2000Volt(Keithly2000):
    mode = 'Voltage'

    def __init__(self, port):
        super().__init__(port)
        with self.com_lock:
            self.write(":FUNC 'VOLT'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?\n'.encode())

            return float(self.read(16).decode()) * 1000
