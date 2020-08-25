import time
import serial
from threading import Lock
from Drivers.AbstractSensorController import AbstractSensor


class Thermolino(AbstractSensor, serial.Serial):
    mode = 'Temperature'

    def __init__(self, port):
        super().__init__(self, port, timeout=1.5)
        self.com_lock = Lock()
        time.sleep(1)
        with self.com_lock:
            self.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?'.encode())
            self.write('\n'.encode())
            return float(self.readline().decode())

    def close(self):
        serial.Serial.close(self)


class Thermoplatino(AbstractSensor, serial.Serial):
    mode = 'Temperature'

    def __init__(self, port):
        super().__init__(self, port, timeout=1.5, baudrate=115200)
        self.com_lock = Lock()
        time.sleep(1)
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

    def close(self):
        serial.Serial.close(self)