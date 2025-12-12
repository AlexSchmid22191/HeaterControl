import serial
import threading
import functools
from operator import ixor
from src.Drivers.BaseClasses import AbstractSensor


class ME_CTL(AbstractSensor):
    mode = 'Temperature'

    def __init__(self, _port):
        self.serial = serial.Serial(_port, baudrate=115200, timeout=1.5)
        self.com_lock = threading.Lock()
        self.serial.reset_input_buffer()
        self.switch_aiming_beam(False)

    def get_sensor_value(self):
        with self.com_lock:
            self.serial.write(b'\x01')
            data = self.serial.read(2)
            return self._bytes_to_temp(data)

    @staticmethod
    def _bytes_to_temp(data):
        return (int.from_bytes(data, byteorder='big') - 1000) / 10

    @staticmethod
    def _checksum(command):
        return bytes([functools.reduce(ixor, command)])

    def switch_aiming_beam(self, state):
        command = b'\xA5\x01' if state else b'\xA5\x00'
        command += self._checksum(command)
        self.serial.write(command)
        self.serial.read(1)

    def close(self):
        self.serial.close()
