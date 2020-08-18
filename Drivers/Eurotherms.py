import threading
import minimalmodbus
from Drivers.AbstractSensorController import AbstractController, AbstractSensor


class Eurotherm3216(AbstractController, minimalmodbus.Instrument):
    """Instrument class for Eurotherm 3216 process controller.
    Args:
    * portname (str): port name
    * slaveadress (int): slave address in the range 1 to 247
    """

    def __init__(self, portname, slaveadress, baudrate=9600):
        super().__init__(portname, slaveadress)
        self.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.read_register(1, number_of_decimals=0)

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        with self.com_lock:
            self.write_register(2, setpoint, number_of_decimals=0)

    def get_target_setpoint(self):
        """Get the target setpoint"""
        with self.com_lock:
            return self.read_register(2, number_of_decimals=0)

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        with self.com_lock:
            self.write_register(3, output, number_of_decimals=1)

    def get_working_output(self):
        """Return the current power output of the controller"""
        with self.com_lock:
            return self.read_register(4, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.read_register(5, number_of_decimals=0)

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint i.e. the heating/cooling rate"""
        with self.com_lock:
            self.write_register(35, rate, number_of_decimals=1)

    def get_rate(self):
        """Get the rate of change for the working setpoint i.e. the heating/cooling rate"""
        with self.com_lock:
            return self.read_register(35, number_of_decimals=1)

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.write_register(273, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.write_register(273, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return self.read_register(273, 1)

    def write_external_target_setpoint(self, target):
        """Set an external target setpoint value (for complex temperature programs)"""
        with self.com_lock:
            self.write_register(26, target, number_of_decimals=0)

    def write_external_sensor_value(self, sensor_value):
        """Write temperature control variable from an external sensor to the controller """
        with self.com_lock:
            self.write_register(203, sensor_value, number_of_decimals=0)

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller"""
        with self.com_lock:
            self.write_register(6, p, number_of_decimals=1)

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
            return self.read_register(6, number_of_decimals=1)

    def get_pid_i(self):
        with self.com_lock:
            return self.read_register(8, number_of_decimals=0)

    def get_pid_d(self):
        with self.com_lock:
            return self.read_register(9, number_of_decimals=0)


class Eurotherm2408(AbstractController, minimalmodbus.Instrument):
    """Instrument class for Eurotherm 2408 process controller.

    Implementations for automatic mode need to be reworked, since the Eurotherm can only access the run list via comms,
     not the prog list
     #TODO: Rework automatic mode
    Args:
    * portname (str): port name
    * slaveadress (int): slave address in the range 1 to 247
    """
    def __init__(self, portname, slaveadress, baudrate=9600):
        super().__init__(portname, slaveadress)
        self.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

        # Due to the way the programmer works, the driver needs to know ramp and setpoint
        self.setpoint = 0
        self.rate = 15

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.read_register(1, number_of_decimals=0)

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        with self.com_lock:
            self.write_register(3, output, number_of_decimals=1)

    def get_working_output(self):
        """Return the current power output of the controller"""
        with self.com_lock:
            return self.read_register(4, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.read_register(5, number_of_decimals=0)

    def set_automatic_mode(self):
        """Set controller to automatic mode, also reset and restart the temperature programmer"""
        with self.com_lock:
            self.write_register(273, 0)
            self.write_register(23, 1)
            self.write_register(23, 2)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.write_register(273, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return self.read_register(273)

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        self.setpoint = setpoint
        self.adjust_programmer()

    def get_target_setpoint(self, setpoint):
        """Get the target setpoint"""
        with self.com_lock:
            return self.read_register(2, number_of_decimals=0)

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint e.g. the heating/cooling rate"""
        self.rate = rate
        self.adjust_programmer()

    def adjust_programmer(self):
        """The 2408 cannot adjust ramp and setpoint directly, only via a temeprature program. This function edits
        program #1 and starts it"""

        with self.com_lock:
            # Reset currently running program
            self.write_register(23, 1)
            # Set segment to rate controlled ramp segment
            self.write_register(8336, 1)
            # Set the target set point
            self.write_register(8337, self.setpoint, number_of_decimals=0)
            # Set the rate
            self.write_register(8338, self.rate, number_of_decimals=1)
            # Set segment 2 to end segment
            self.write_register(8344, 3)  # set to end type
            # Set the end type to indefinite dwell
            self.write_register(8346, 3)  # set endsegment to dwell
            # Start program 1
            self.write_register(23, 2)


class Eurotherm3508(AbstractController, minimalmodbus.Instrument):
    """
    Instrument class for Eurotherm 3508 process controller.
    The automatic mode is only setpoint controlled, no ramps
    Args:
    * portname (str): port name
    * slaveadress (int): slave address in the range 1 to 247
    """

    def __init__(self, portname, slaveadress, baudrate=9600):
        super().__init__(portname, slaveadress)
        self.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.read_register(1, number_of_decimals=4, signed=True)

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        with self.com_lock:
            self.write_register(2, setpoint, number_of_decimals=4, signed=True)

    def get_target_setpoint(self):
        """Get the target setpoint"""
        with self.com_lock:
            return self.read_register(2, number_of_decimals=0)

    def set_manual_output_power(self, output):
        """Set the power output of the instrument in percent"""
        with self.com_lock:
            self.write_register(3, output, number_of_decimals=1, signed=True)

    def get_rate(self):
        """Get the rate of change for the working setpoint i.e. the heating/cooling rate"""
        with self.com_lock:
            return self.read_register(35, number_of_decimals=1)

    def get_working_output(self):
        """Return the current power output of the instrument"""
        with self.com_lock:
            return self.read_register(3, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.read_register(5, number_of_decimals=4, signed=True)

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.write_register(273, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.write_register(273, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return {0: 'Automatic', 1: 'Manual'}[self.read_register(273, 1)]

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller, Set 1"""
        with self.com_lock:
            self.write_register(6, p, number_of_decimals=1)

    def set_pid_p2(self, p):
        """Set the P (Proportional band) for the PID controller, Set 2"""
        with self.com_lock:
            self.write_register(48, p, number_of_decimals=1)

    def set_pid_p3(self, p):
        """Set the P (Proportional band) for the PID controller, Set 3"""
        with self.com_lock:
            self.write_register(180, p, number_of_decimals=1)

    def get_pid_p(self):
        """Get the P (Proportional band) for the PID controller"""
        with self.com_lock:
            return self.read_register(6, number_of_decimals=1)

    def get_pid_p2(self):
        """Get the P (Proportional band) for the PID controller, Set2"""
        with self.com_lock:
            return self.read_register(48, number_of_decimals=1)

    def get_pid_p3(self):
        """Get the P (Proportional band) for the PID controller, Set3"""
        with self.com_lock:
            return self.read_register(180, number_of_decimals=1)

    def set_pid_i(self, i):
        """Set the I (Integral time) for the PID controller"""
        with self.com_lock:
            self.write_register(8, i, number_of_decimals=0)

    def set_pid_i2(self, i):
        """Set the I (Integral time) for the PID controller, Set2"""
        with self.com_lock:
            self.write_register(49, i, number_of_decimals=0)

    def set_pid_i3(self, i):
        """Set the I (Integral time) for the PID controller, Set3"""
        with self.com_lock:
            self.write_register(181, i, number_of_decimals=0)

    def get_pid_i(self):
        """Get the I (Integral time) for the PID controller"""
        with self.com_lock:
            return self.read_register(8, number_of_decimals=0)

    def get_pid_i2(self):
        """Get the I (Integral time) for the PID controller, Set2"""
        with self.com_lock:
            return self.read_register(49, number_of_decimals=0)

    def get_pid_i3(self):
        """Get the I (Integral time) for the PID controller, Set3"""
        with self.com_lock:
            return self.read_register(181, number_of_decimals=0)

    def set_pid_d(self, d):
        """Set the D (Derivative time) for the PID controller"""
        with self.com_lock:
            self.write_register(9, d, number_of_decimals=0)

    def set_pid_d2(self, d):
        """Set the D (Derivative time) for the PID controller, Set2"""
        with self.com_lock:
            self.write_register(51, d, number_of_decimals=0)

    def set_pid_d3(self, d):
        """Set the D (Derivative time) for the PID controller, Set3"""
        with self.com_lock:
            self.write_register(183, d, number_of_decimals=0)

    def get_pid_d(self):
        """Get the D (Derivative time) for the PID controller"""
        with self.com_lock:
            return self.read_register(9, number_of_decimals=0)

    def get_pid_d2(self):
        """Get the D (Derivative time) for the PID controller, Set2"""
        with self.com_lock:
            return self.read_register(51, number_of_decimals=0)

    def get_pid_d3(self):
        """Get the D (Derivative time) for the PID controller, Set3"""
        with self.com_lock:
            return self.read_register(183, number_of_decimals=0)

    def set_boundary_12(self, boundary):
        """Set the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        with self.com_lock:
            self.write_register(153, boundary, number_of_decimals=0)

    def set_boundary_23(self, boundary):
        """Set the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        with self.com_lock:
            self.write_register(152, boundary, number_of_decimals=0)

    def get_boundary_12(self):
        """Get the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        with self.com_lock:
            return self.read_register(153, number_of_decimals=0)

    def get_boundary_23(self):
        """Get the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        with self.com_lock:
            return self.read_register(152, number_of_decimals=0)

    def set_gain_scheduling(self, mode):
        """Set the gain scheduling mode"""
        mode_dict = {'Off': 0, 'Set': 1, 'Setpoint': 2, 'Process Variable': 3, 'Output': 5}
        with self.com_lock:
            self.write_register(15360, mode_dict[mode])

    def get_gain_scheduling(self):
        """Get the gain scheduling mode"""
        mode_dict = {0: 'Off', 1: 'Set', 2: 'Setpoint', 3: 'Process Variable', 5: 'Output'}
        with self.com_lock:
            return mode_dict[self.read_register(15360)]


class Eurotherm3508S(AbstractSensor, minimalmodbus.Instrument):
    """
        Instrument class for Eurotherm 3508 process controller.
        The automatic mode is only setpoint controlled, no ramps
        Args:
        * portname (str): port name
        * slaveadress (int): slave address in the range 1 to 247
        """

    def __init__(self, portname, slaveadress, baudrate=9600):
        super().__init__(portname, slaveadress)
        self.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def get_sensor_value(self):
        with self.com_lock:
            return self.read_register(1, number_of_decimals=4, signed=True)
