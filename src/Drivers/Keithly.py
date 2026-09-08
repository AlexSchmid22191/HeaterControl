import threading
import time

import serial

from src.Drivers.BaseClasses import AbstractSensor, UnitType


class Keithley2000Temp(AbstractSensor):
    type = UnitType.TEMPERATURE

    def __init__(self, _port: str):
        self.serial = serial.Serial(_port, timeout=1.5)
        self.com_lock = threading.Lock()
        time.sleep(1)
        with self.com_lock:
            self.serial.write('*RST\n'.encode())
            self.serial.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self) -> float:
        with self.com_lock:
            self.serial.write(':read?\n'.encode())
            return float(self.serial.read(16).decode())

    def close(self) -> None:
        self.serial.close()


class Keithley2000Volt(AbstractSensor):
    type = UnitType.VOLTAGE

    def __init__(self, _port: str):
        self.serial = serial.Serial(_port, timeout=1.5)
        self.com_lock = threading.Lock()
        time.sleep(1)
        with self.com_lock:
            self.serial.write('*RST\n'.encode())
            self.serial.write(":FUNC 'VOLT'\n".encode())

    def get_sensor_value(self) -> float:
        with self.com_lock:
            self.serial.write(':read?\n'.encode())
            return float(self.serial.read(16).decode()) * 1000

    def close(self) -> None:
        self.serial.close()
