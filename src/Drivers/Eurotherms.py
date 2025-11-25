import threading

import minimalmodbus

from src.Drivers.BaseClasses import AbstractController, AbstractSensor


class Eurotherm3216(AbstractController):
    """Instrument class for Eurotherm 3216 process controller."""
    mode = 'Temperature'

    def __init__(self, _port_name, _slave_address, baudrate=9600):
        self.instrument = minimalmodbus.Instrument(_port_name, _slave_address)
        self.instrument.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def close(self):
        self.instrument.serial.close()

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.instrument.read_register(1, number_of_decimals=0)

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        with self.com_lock:
            self.instrument.write_register(2, setpoint, number_of_decimals=0)

    def get_target_setpoint(self):
        """Get the target setpoint"""
        with self.com_lock:
            return self.instrument.read_register(2, number_of_decimals=0)

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        with self.com_lock:
            self.instrument.write_register(3, output, number_of_decimals=1)

    def get_working_output(self):
        """Return the current power output of the controller"""
        with self.com_lock:
            return self.instrument.read_register(4, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.instrument.read_register(5, number_of_decimals=0)

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            self.instrument.write_register(35, rate, number_of_decimals=1)

    def get_rate(self):
        """Get the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            return self.instrument.read_register(35, number_of_decimals=1)

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.instrument.write_register(273, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.instrument.write_register(273, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return self.instrument.read_register(273, 1)

    def write_external_target_setpoint(self, target):
        """Set an external target setpoint value (for complex temperature programs)"""
        with self.com_lock:
            self.instrument.write_register(26, target, number_of_decimals=0)

    def write_external_sensor_value(self, sensor_value):
        """Write temperature control variable from an external sensor to the controller """
        with self.com_lock:
            self.instrument.write_register(203, sensor_value, number_of_decimals=0)

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller"""
        with self.com_lock:
            self.instrument.write_register(6, p, number_of_decimals=1)

    def set_pid_i(self, i):
        """Set the I (Integral time) for the PID controller"""
        with self.com_lock:
            self.instrument.write_register(8, i, number_of_decimals=0)

    def set_pid_d(self, d):
        """Set the D (Derivative time) for the PID controller"""
        with self.com_lock:
            self.instrument.write_register(9, d, number_of_decimals=0)

    def get_pid_p(self):
        with self.com_lock:
            return self.instrument.read_register(6, number_of_decimals=1)

    def get_pid_i(self):
        with self.com_lock:
            return self.instrument.read_register(8, number_of_decimals=0)

    def get_pid_d(self):
        with self.com_lock:
            return self.instrument.read_register(9, number_of_decimals=0)


class Eurotherm2408(AbstractController):
    """Instrument class for Eurotherm 2408 process controller."""
    mode = 'Temperature'

    def __init__(self, _port_name, _slave_address, baudrate=9600):
        self.instrument = minimalmodbus.Instrument(_port_name, _slave_address)
        self.instrument.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def close(self):
        self.instrument.serial.close()

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.instrument.read_register(1, number_of_decimals=0)

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        with self.com_lock:
            self.instrument.write_register(3, output, number_of_decimals=1)

    def get_working_output(self):
        """Return the current power output of the controller"""
        with self.com_lock:
            return self.instrument.read_register(4, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.instrument.read_register(5, number_of_decimals=0)

    def set_automatic_mode(self):
        """Set controller to automatic mode, also reset and restart the temperature programmer"""
        with self.com_lock:
            self.instrument.write_register(273, 0)
            self.instrument.write_register(23, 1)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.instrument.write_register(273, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return {0: 'Automatic', 1: 'Manual'}[self.instrument.read_register(273, 0)]

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        with self.com_lock:
            self.instrument.write_register(2, setpoint, number_of_decimals=0)

    def get_target_setpoint(self):
        """Get the target setpoint"""
        with self.com_lock:
            return self.instrument.read_register(2, number_of_decimals=0)

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint e.g., the heating/cooling rate"""
        with self.com_lock:
            self.instrument.write_register(35, rate, number_of_decimals=0)

    def get_rate(self):
        with self.com_lock:
            return self.instrument.read_register(35, number_of_decimals=0)


class Eurotherm3508(AbstractController):
    """
    Instrument class for Eurotherm 3508 process controller.
    The automatic mode is only setpoint controlled, no ramps
    Args:
    * _port_name (str): port name
    * _slave_address (int): slave address in the range 1 to 247
    """

    mode = 'Voltage'

    def __init__(self, _port_name, _slave_address, baudrate=9600):
        self.instrument = minimalmodbus.Instrument(_port_name, _slave_address)
        self.instrument.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def close(self):
        self.instrument.serial.close()

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.instrument.read_register(1, number_of_decimals=4, signed=True) * 1000

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        with self.com_lock:
            self.instrument.write_register(2, setpoint / 1000, number_of_decimals=4, signed=True)

    def get_target_setpoint(self):
        """Get the target setpoint"""
        with self.com_lock:
            return self.instrument.read_register(2, number_of_decimals=4) * 1000

    def set_manual_output_power(self, output):
        """Set the power output of the instrument in percent"""
        with self.com_lock:
            self.instrument.write_register(3, output, number_of_decimals=1, signed=True)

    def get_rate(self):
        """Get the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            return self.instrument.read_register(35, number_of_decimals=1) * 1000

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            self.instrument.write_register(35, rate / 1000, number_of_decimals=1, signed=True)

    def get_working_output(self):
        """Return the current power output of the instrument"""
        with self.com_lock:
            return self.instrument.read_register(3, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.instrument.read_register(5, number_of_decimals=4, signed=True) * 1000

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.instrument.write_register(273, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.instrument.write_register(273, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return {0: 'Automatic', 1: 'Manual'}[self.instrument.read_register(273, 0)]

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller, Set 1"""
        with self.com_lock:
            self.instrument.write_register(6, p / 1000, number_of_decimals=1)

    def set_pid_p2(self, p):
        """Set the P (Proportional band) for the PID controller, Set 2"""
        with self.com_lock:
            self.instrument.write_register(48, p / 1000, number_of_decimals=1)

    def set_pid_p3(self, p):
        """Set the P (Proportional band) for the PID controller, Set 3"""
        with self.com_lock:
            self.instrument.write_register(180, p / 1000, number_of_decimals=1)

    def get_pid_p(self):
        """Get the P (Proportional band) for the PID controller"""
        with self.com_lock:
            return self.instrument.read_register(6, number_of_decimals=1) * 1000

    def get_pid_p2(self):
        """Get the P (Proportional band) for the PID controller, Set2"""
        with self.com_lock:
            return self.instrument.read_register(48, number_of_decimals=1) * 1000

    def get_pid_p3(self):
        """Get the P (Proportional band) for the PID controller, Set3"""
        with self.com_lock:
            return self.instrument.read_register(180, number_of_decimals=1) * 1000

    def set_pid_i(self, i):
        """Set the I (Integral time) for the PID controller"""
        with self.com_lock:
            self.instrument.write_register(8, i, number_of_decimals=0)

    def set_pid_i2(self, i):
        """Set the I (Integral time) for the PID controller, Set2"""
        with self.com_lock:
            self.instrument.write_register(49, i, number_of_decimals=0)

    def set_pid_i3(self, i):
        """Set the I (Integral time) for the PID controller, Set3"""
        with self.com_lock:
            self.instrument.write_register(181, i, number_of_decimals=0)

    def get_pid_i(self):
        """Get the I (Integral time) for the PID controller"""
        with self.com_lock:
            return self.instrument.read_register(8, number_of_decimals=0)

    def get_pid_i2(self):
        """Get the I (Integral time) for the PID controller, Set2"""
        with self.com_lock:
            return self.instrument.read_register(49, number_of_decimals=0)

    def get_pid_i3(self):
        """Get the I (Integral time) for the PID controller, Set3"""
        with self.com_lock:
            return self.instrument.read_register(181, number_of_decimals=0)

    def set_pid_d(self, d):
        """Set the D (Derivative time) for the PID controller"""
        with self.com_lock:
            self.instrument.write_register(9, d, number_of_decimals=0)

    def set_pid_d2(self, d):
        """Set the D (Derivative time) for the PID controller, Set2"""
        with self.com_lock:
            self.instrument.write_register(51, d, number_of_decimals=0)

    def set_pid_d3(self, d):
        """Set the D (Derivative time) for the PID controller, Set3"""
        with self.com_lock:
            self.instrument.write_register(183, d, number_of_decimals=0)

    def get_pid_d(self):
        """Get the D (Derivative time) for the PID controller"""
        with self.com_lock:
            return self.instrument.read_register(9, number_of_decimals=0)

    def get_pid_d2(self):
        """Get the D (Derivative time) for the PID controller, Set2"""
        with self.com_lock:
            return self.instrument.read_register(51, number_of_decimals=0)

    def get_pid_d3(self):
        """Get the D (Derivative time) for the PID controller, Set3"""
        with self.com_lock:
            return self.instrument.read_register(183, number_of_decimals=0)

    def set_boundary_12(self, boundary):
        """Set the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        with self.com_lock:
            self.instrument.write_float(15361, boundary / 1000)

    def set_boundary_23(self, boundary):
        """Set the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        with self.com_lock:
            self.instrument.write_float(15362, boundary / 1000)

    def get_boundary_12(self):
        """Get the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        with self.com_lock:
            return self.instrument.read_float(15361) * 1000

    def get_boundary_23(self):
        """Get the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        with self.com_lock:
            return self.instrument.read_float(15362) * 1000

    def set_gain_scheduling(self, mode):
        """Set the gain scheduling mode"""
        mode_dict = {'None': 0, 'Set': 1, 'Setpoint': 2, 'Process Variable': 3, 'Output': 5}
        with self.com_lock:
            self.instrument.write_register(15360, mode_dict[mode])

    def get_gain_scheduling(self):
        """Get the gain scheduling mode"""
        mode_dict = {0: 'None', 1: 'Set', 2: 'Setpoint', 3: 'Process Variable', 5: 'Output'}
        with self.com_lock:
            return mode_dict[self.instrument.read_register(15360)]

    def get_active_set(self):
        with self.com_lock:
            return self.instrument.read_register(72)

    def set_active_set(self, active_set):
        with self.com_lock:
            self.instrument.write_register(72, active_set)


class Eurotherm3508S(AbstractSensor):
    """
        Instrument class for Eurotherm 3508 process controller.
        The automatic mode is only setpoint controlled, no ramps
        Args:
        * _port_name (str): port name
        * _slave_address (int): slave address in the range 1 to 247
        """
    mode = 'Voltage'

    def __init__(self, _port, _slave_address=1, baudrate=9600):
        self.instrument = minimalmodbus.Instrument(_port, _slave_address)
        self.instrument.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def close(self):
        self.instrument.serial.close()

    def get_sensor_value(self):
        with self.com_lock:
            return self.instrument.read_register(1, number_of_decimals=4, signed=True) * 1000
