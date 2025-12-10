import serial
import threading
from src.Drivers.BaseClasses import AbstractSensor


class ME_CTL(AbstractSensor):
    mode = 'Temperature'

    def __init__(self, _port):
        self.serial = serial.Serial(_port, baudrate=115200, timeout=1.5)
        self.com_lock = threading.Lock()
        self.serial.reset_input_buffer()

    def get_sensor_value(self):
        with self.com_lock:
            self.serial.write(b'\x01')
            data = self.serial.read(2)
            return self._bytes_to_temp(data)

    @staticmethod
    def _bytes_to_temp(data):
        return (int.from_bytes(data, byteorder='big') - 1000) / 10

    def close(self):
        self.serial.close()
