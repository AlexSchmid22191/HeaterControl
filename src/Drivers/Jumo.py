import threading

import minimalmodbus

from src.Drivers.BaseClasses import AbstractController, ControllerFeatures, UnitType


class JumoQuantrol(AbstractController):
    controller_type = UnitType.TEMPERATURE
    features = {ControllerFeatures.SIMPLE_PID}

    def __init__(self, _port_name: str, _slave_address: int) -> None:
        self.instrument = minimalmodbus.Instrument(_port_name, _slave_address)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.timeout = 0.25
        self.com_lock = threading.Lock()

    def close(self) -> None:
        self.instrument.serial.close()

    def get_process_variable(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x031, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_target_setpoint(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x3100, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_working_output(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x0037, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_working_setpoint(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x0035, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_rate(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x004E, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_control_mode(self) -> str:
        with self.com_lock:
            return {0: 'Automatic', 1: 'Manual'}[int(self.instrument.read_register(0x0020)) >> 12 & 1]

    def set_manual_mode(self) -> None:
        with self.com_lock:
            self.instrument.write_register(0x0047, 0b1 << 2)

    def set_automatic_mode(self) -> None:
        with self.com_lock:
            self.instrument.write_register(0x0047, 0b1 << 3)

    def set_target_setpoint(self, setpoint: float) -> None:
        with self.com_lock:
            self.instrument.write_float(0x3100, setpoint, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
            self.instrument.write_register(0x0047,
                                           0b1 << 8)  # Restart ramp function, so it begins at current process value

    def set_rate(self, rate: float) -> None:
        with self.com_lock:
            self.instrument.write_float(0x004E, rate, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
            self.instrument.write_register(0x0047,
                                           0b1 << 8)  # Restart ramp function, so it begins at current process value

    def set_pid_p(self, p: float) -> None:
        with self.com_lock:
            self.instrument.write_float(0x3000, p, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def set_pid_i(self, i: float) -> None:
        with self.com_lock:
            self.instrument.write_float(0x3006, i, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def set_pid_d(self, d: float) -> None:
        with self.com_lock:
            self.instrument.write_float(0x3004, d, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_pid_p(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x3000, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_pid_i(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x3006, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def get_pid_d(self) -> float:
        with self.com_lock:
            return self.instrument.read_float(0x3004, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)

    def emergency_stop(self) -> None:
        self.set_target_setpoint(0)
        self.set_rate(1200)
        raise NotImplementedError('Emergency stop not possible for JumoQuantrol. Cooling to 0 with maximum rate!')
