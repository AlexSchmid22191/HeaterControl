import serial
import threading
from src.Drivers.BaseClasses import AbstractSensor


class Pyrometer(AbstractSensor):
    mode = 'Temperature'

    def __init__(self, _port):
        self.serial = serial.Serial(_port, timeout=1.5)
        self.com_lock = threading.Lock()
        with self.com_lock:
            self.serial.write('TRIG SP OFF\r'.encode())
        self.serial.reset_input_buffer()

    def get_sensor_value(self):
        with self.com_lock:
            self.serial.write('TEMP'.encode())
            self.serial.write('\r'.encode())

            answer = self.serial.read_until(b'\r', 20).decode()
            temp = float(answer.split()[0])
            return temp

    def close(self):
        self.serial.close()
