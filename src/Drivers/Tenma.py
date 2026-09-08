import threading

import serial

from src.Drivers.BaseClasses import AbstractPowerSupply, PowerSupplyFeatures


class Tenma(AbstractPowerSupply):
    features = {PowerSupplyFeatures.OUTPUT_ENABLE}

    def __init__(self, port: str):
        self.serial = serial.Serial(port, baudrate=9600, timeout=1.5)
        self.com_lock = threading.Lock()

    def set_voltage_limit(self, voltage: float) -> None:
        string = f'VSET05:{voltage:.3f}'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')

    def set_current_limit(self, current: float) -> None:
        string = f'ISET05:{current:.3f}'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')

    def get_voltage_limit(self) -> float:
        string = f'VSET05?'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')
            answer = self.serial.readline()
            return float(answer.decode())

    def get_current_limit(self) -> float:
        string = f'ISET05?'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')
            answer = self.serial.readline()
            return float(answer.decode())

    def get_voltage(self) -> float:
        string = f'VOUT05?'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')
            answer = self.serial.readline()
            return float(answer.decode())

    def get_current(self) -> float:
        string = f'IOUT05?'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')
            answer = self.serial.readline()
            return float(answer.decode())

    def get_limit_mode(self) -> str:
        string = f'STATUS05?'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')
            answer = self.serial.readline()
            return 'CV' if answer.decode()[-1] == '0' else 'CC'

    def get_resistance(self) -> float:
        string_c = f'IOUT05?'
        string_v = f'VOUT05?'
        with self.com_lock:
            self.serial.write(string_c.encode())
            self.serial.write(b'\x0D')
            answer_c = self.serial.readline()
            self.serial.write(string_v.encode())
            self.serial.write(b'\x0D')
            answer_v = self.serial.readline()

            voltage = float(answer_v.decode())
            current = float(answer_c.decode())
            if current < 0.1:
                return -1
            else:
                return voltage / current

    def enable_output(self) -> None:
        string = f'OUT05:1'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')

    def disable_output(self) -> None:
        string = f'OUT05:0'
        with self.com_lock:
            self.serial.write(string.encode())
            self.serial.write(b'\x0D')

    def close(self) -> None:
        self.serial.close()
