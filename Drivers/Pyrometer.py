import time
import serial
import threading
from Drivers.AbstractSensorController import AbstractSensor


class Pyrometer(AbstractSensor, serial.Serial):
    def __init__(self, port):
        super().__init__(port, timeout=1.5)
        self.com_lock = threading.Lock()

    def get_sensor_value(self):
        with self.com_lock:
            self.reset_input_buffer()
            self.write('TEMP'.encode())
            self.write('\r'.encode())

            answer = self.read_until(b'\r', 20).decode()
            temp = float(answer.split()[0])
            return temp

    def close(self):
        serial.Serial.close(self)