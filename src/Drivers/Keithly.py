import threading
import time

import serial

from src.Drivers.BaseClasses import AbstractSensor, SensorFeatures, UnitType


class Keithley2000(AbstractSensor):

    def __init__(self, _port: str):
        self.serial = serial.Serial(_port, timeout=1.5)
        self.com_lock = threading.Lock()
        time.sleep(1)
        with self.com_lock:
            self.serial.write(b'*RST\n')
            self.serial.write(b'*CLS\n')
            self.serial.write(b':ABOR\n')
            self.serial.write(b':INIT:CONT OFF\n')

    def _read_line(self) -> bytes | None:
        """Custom readline function to deal with either combination of CR and LF line terminators"""
        data = bytearray()
        while True:
            char = self.serial.read(1)
            if not char:
                return None
            if char in (b'\r', b'\n'):
                if data:
                    return bytes(data)
                continue
            data.extend(char)

    def _write(self, command: str) -> None:
        with self.com_lock:
            self.serial.write(f'{command}\n'.encode('ascii'))

    def _query(self, command: str) -> bytes:
        with self.com_lock:
            self.serial.write(f'{command}\n'.encode('ascii'))
            answer = self._read_line()
        if answer is None:
            raise TimeoutError(f"Keithley timed out waiting for response to {command!r}")
        return answer

    def get_sensor_value(self) -> float:
        return float(self._query(':READ?'))

    def close(self) -> None:
        self.serial.close()


class Keithley2000Temp(Keithley2000):
    type = UnitType.TEMPERATURE
    features = [SensorFeatures.TC_SELECT]
    valid_tc_types = ['K', 'J', 'T']

    def __init__(self, _port: str):
        super().__init__(_port)
        self._write(":FUNC 'TEMP'")
        self.set_sensor_tc('K')

    def set_sensor_tc(self, tc: str) -> None:
        if tc not in self.valid_tc_types:
            raise ValueError(f"Invalid thermocouple type: {tc}")
        self._write(f':TEMP:TC:TYPE {tc}')

    def get_sensor_tc(self) -> str:
        return self._query(':TEMP:TC:TYPE?').decode('ascii').strip()


class Keithley2000Volt(Keithley2000):
    type = UnitType.VOLTAGE

    def __init__(self, _port: str):
        super().__init__(_port)
        self._write(":FUNC 'VOLT'")

    def get_sensor_value(self) -> float:
        return super().get_sensor_value() * 1000
