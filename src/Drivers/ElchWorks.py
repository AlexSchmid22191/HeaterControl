import time
from threading import Lock

import minimalmodbus
import serial

from src.Drivers.BaseClasses import AbstractController, AbstractSensor


class Thermolino(AbstractSensor, serial.Serial):
    mode = 'Temperature'

    def __init__(self, _port):
        super().__init__(_port, timeout=1.5)
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

    def __init__(self, _port):
        super().__init__(_port, timeout=1.5, baudrate=115200)
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


class ElchLaser(AbstractController, minimalmodbus.Instrument):
    mode = 'Temperature'

    def __init__(self, _port_name, _slave_address, baudrate=9600):
        super().__init__(_port_name, _slave_address)
        time.sleep(1)
        self.serial.baudrate = baudrate
        self.com_lock = Lock()

    def close(self):
        self.serial.close()

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.read_register(0, number_of_decimals=1)

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        with self.com_lock:
            self.write_register(1, setpoint, number_of_decimals=1)

    def get_target_setpoint(self):
        """Get the target setpoint"""
        with self.com_lock:
            return self.read_register(1, number_of_decimals=1)

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        with self.com_lock:
            self.write_register(2, output, number_of_decimals=2)

    def get_working_output(self):
        """Return the current power output of the controller"""
        with self.com_lock:
            return self.read_register(3, number_of_decimals=2)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.read_register(4, number_of_decimals=1)

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            self.write_register(5, rate, number_of_decimals=1)

    def get_rate(self):
        """Get the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            return self.read_register(5, number_of_decimals=1)

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.write_register(6, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.write_register(6, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return {0: 'Automatic', 1: 'Manual'}[self.read_register(6, 0)]

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller"""
        with self.com_lock:
            self.write_register(7, p, number_of_decimals=1)

    def set_pid_i(self, i):
        """Set the I (Integral time) for the PID controller"""
        with self.com_lock:
            self.write_register(8, i, number_of_decimals=0)

    def set_pid_d(self, d):
        """Set the D (Derivative time) for the PID controller"""
        with self.com_lock:
            self.write_register(9, d, number_of_decimals=0)

    def get_pid_p(self):
        with self.com_lock:
            return self.read_register(7, number_of_decimals=1)

    def get_pid_i(self):
        with self.com_lock:
            return self.read_register(8, number_of_decimals=0)

    def get_pid_d(self):
        with self.com_lock:
            return self.read_register(9, number_of_decimals=0)

    def enable_output(self):
        with self.com_lock:
            self.write_register(10, 1)

    def disable_output(self):
        with self.com_lock:
            self.write_register(10, 0)

    def get_enable_state(self):
        with self.com_lock:
            return self.read_register(10)

    def get_tc_fault(self):
        with self.com_lock:
            return self.read_register(12)

    def enable_aiming_beam(self):
        with self.com_lock:
            self.write_register(13, 1)

    def disable_aiming_beam(self):
        with self.com_lock:
            self.write_register(13, 0)
