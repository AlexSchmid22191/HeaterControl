from Drivers.AbstractSensorController import AbstractSensor
from serial import Serial
from threading import Lock
from time import sleep


class Thermolino(AbstractSensor, Serial):
    def __init__(self, port):
        Serial.__init__(self, port, timeout=1.5)
        self.com_lock = Lock()
        sleep(1)
        with self.com_lock:
            self.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?'.encode())
            self.write('\n'.encode())
            return float(self.readline().decode())


class Thermoplatino(AbstractSensor, Serial):
    def __init__(self, port):
        Serial.__init__(self, port, timeout=1.5, baudrate=115200)
        self.com_lock = Lock()
        sleep(1)
        with self.com_lock:
            self.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?'.encode())
            self.write('\n'.encode())
            answer = self.readline().decode()
            try:
                return float(answer)
            except ValueError:
                return answer
