import threading

import minimalmodbus

from src.Drivers.BaseClasses import AbstractController


class JumoQuantrol(minimalmodbus.Instrument, AbstractController):
    mode = 'Temperature'

    def __init__(self, _port_name, _slave_address):
        super().__init__(_port_name, _slave_address)
        self.serial.baudrate = 9600
        self.serial.timeout = 0.25
        self.com_lock = threading.Lock()

    def close(self):
        self.serial.close()

    def get_process_variable(self):
        with self.com_lock:
            return self.read_float(0x031, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_target_setpoint(self):
        with self.com_lock:
            return self.read_float(0x3100, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_working_output(self):
        with self.com_lock:
            return self.read_float(0x0037, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_working_setpoint(self):
        with self.com_lock:
            return self.read_float(0x0035, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_rate(self):
        with self.com_lock:
            return self.read_float(0x004E, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_control_mode(self):
        with self.com_lock:
            return {0: 'Automatic', 1: 'Manual'}[self.read_register(0x0020) >> 12 & 1]

    def set_manual_mode(self):
        with self.com_lock:
            self.write_register(0x0047, 0b1 << 2)

    def set_automatic_mode(self):
        with self.com_lock:
            self.write_register(0x0047, 0b1 << 3)

    def set_target_setpoint(self, setpoint):
        with self.com_lock:
            self.write_float(0x3100, setpoint, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
            self.write_register(0x0047, 0b1 << 8)  # Restart ramp function, so it begins at current process value

    def set_rate(self, rate):
        with self.com_lock:
            self.write_float(0x004E, rate, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
            self.write_register(0x0047, 0b1 << 8)  # Restart ramp function, so it begins at current process value

    def set_pid_p(self, p):
        with self.com_lock:
            self.write_float(0x3000, p, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def set_pid_i(self, i):
        with self.com_lock:
            self.write_float(0x3006, i, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def set_pid_d(self, d):
        with self.com_lock:
            self.write_float(0x3004, d, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_pid_p(self):
        with self.com_lock:
            return self.read_float(0x3000, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_pid_i(self):
        with self.com_lock:
            return self.read_float(0x3006, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_pid_d(self):
        with self.com_lock:
            return self.read_float(0x3004, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
