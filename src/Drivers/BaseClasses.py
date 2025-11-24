from abc import ABC, abstractmethod
from typing import Literal


class AbstractController(ABC):
    """
    Abstract base class for controllers. Drivers for specific devices inherit this class and implement the methods.
    Core functionality is mandatory and has to be overridden.
    Optional functionality raises an exception if the methods are not overwritten in derived subclasses.
    """
    mode: Literal["auto", "manual"]

    # Mandatory methods ------------------------------------------------------------------------------------------------

    @abstractmethod
    def __init__(self, _port_name, _slave_address=1):
        """Init"""

    @abstractmethod
    def get_process_variable(self):
        """Return the current process variable of the controller (often this is the oven thermocouple temperature)"""

    @abstractmethod
    def get_working_output(self):
        """Return the current power output of the controller in percent"""

    @abstractmethod
    def get_working_setpoint(self):
        """Get the current working setpoint of the controller"""

    @abstractmethod
    def get_target_setpoint(self):
        """Get the target setpoint"""

    @abstractmethod
    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""

    @abstractmethod
    def get_rate(self):
        """Get the rate of change for the working setpoint"""

    @abstractmethod
    def set_rate(self, rate):
        """Set the rate of change for the working setpoint"""

    @abstractmethod
    def get_control_mode(self):
        """Get the active control mode"""

    @abstractmethod
    def set_automatic_mode(self):
        """Set controller to automatic mode, PID controls output power"""

    @abstractmethod
    def set_manual_mode(self):
        """Set controller to manual mode, output power is held constant"""

    @abstractmethod
    def close(self):
        """Close the controller serial port"""

    # Optional methods -------------------------------------------------------------------------------------------------

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_manual_output_power',
                                                                                      self.__class__.__name__))

    def get_pid_p(self):
        """Get the P (Proportional band) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_p',
                                                                                      self.__class__.__name__))

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_p',
                                                                                      self.__class__.__name__))

    def get_pid_p2(self):
        """Get the P2 (Proportional band) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_p2',
                                                                                      self.__class__.__name__))

    def set_pid_p2(self, p):
        """Set the P2 (Proportional band) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_p2',
                                                                                      self.__class__.__name__))

    def get_pid_p3(self):
        """Get the P3 (Proportional band) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_p3',
                                                                                      self.__class__.__name__))

    def set_pid_p3(self, p):
        """Set the P3 (Proportional band) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_p3',
                                                                                      self.__class__.__name__))

    def get_pid_i(self):
        """Get the I (Integral time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_i',
                                                                                      self.__class__.__name__))

    def set_pid_i(self, i):
        """Set the I (Integral time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_i',
                                                                                      self.__class__.__name__))

    def get_pid_i2(self):
        """Get the I2 (Integral time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_i2',
                                                                                      self.__class__.__name__))

    def set_pid_i2(self, i):
        """Set the I2 (Integral time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_i2',
                                                                                      self.__class__.__name__))

    def get_pid_i3(self):
        """Get the I3 (Integral time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_i3',
                                                                                      self.__class__.__name__))

    def set_pid_i3(self, i):
        """Set the I3 (Integral time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_i3',
                                                                                      self.__class__.__name__))

    def get_pid_d(self):
        """Get the D (Derivative time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_d',
                                                                                      self.__class__.__name__))

    def set_pid_d(self, d):
        """Set the D (Derivative time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_d',
                                                                                      self.__class__.__name__))

    def get_pid_d2(self):
        """Get the D2 (Derivative time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_d2',
                                                                                      self.__class__.__name__))

    def set_pid_d2(self, d):
        """Set the D2 (Derivative time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_d2',
                                                                                      self.__class__.__name__))

    def get_pid_d3(self):
        """Get the D3 (Derivative time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_pid_d3',
                                                                                      self.__class__.__name__))

    def set_pid_d3(self, d):
        """Set the D3 (Derivative time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_d3',
                                                                                      self.__class__.__name__))

    def get_boundary_12(self):
        """Get the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_boundary_12',
                                                                                      self.__class__.__name__))

    def set_boundary_12(self, boundary):
        """Set the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_boundary_12',
                                                                                      self.__class__.__name__))

    def get_boundary_23(self):
        """Get the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_boundary_23',
                                                                                      self.__class__.__name__))

    def set_boundary_23(self, boundary):
        """Set the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_boundary_23',
                                                                                      self.__class__.__name__))

    def get_gain_scheduling(self):
        """Get the gain scheduling mode"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_gain_scheduling',
                                                                                      self.__class__.__name__))

    def set_gain_scheduling(self, mode):
        """Set the gain scheduling mode"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_gain_scheduling',
                                                                                      self.__class__.__name__))

    def get_active_set(self):
        """Get the currently active set of PID parameters"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_active_set',
                                                                                      self.__class__.__name__))

    def set_active_set(self, active_set):
        """Set the currently active set of PID parameters"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_active_set',
                                                                                      self.__class__.__name__))

    def enable_aiming_beam(self):
        """Toggle the aiming beam on/off"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('enable_aiming_beam',
                                                                                      self.__class__.__name__))

    def disable_aiming_beam(self):
        """Toggle the aiming beam on/off"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('disable_aiming_beam',
                                                                                      self.__class__.__name__))

    def enable_output(self):
        """Enable the output"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('enable_output',
                                                                                      self.__class__.__name__))

    def disable_output(self):
        """Disable the output"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('disable_output',
                                                                                      self.__class__.__name__))


class AbstractSensor(ABC):
    """
    Abstract base class for sensors. Drivers for specific devices inherit this class and implement the read method.
    Raises a NotImplementedException if the methods are not overwritten in derived subclasses.
    """

    mode: Literal["auto", "manual"]

    @abstractmethod
    def __init__(self, _port):
        """Init"""

    @abstractmethod
    def get_sensor_value(self):
        """Return the current readout value of the sensor"""

    @abstractmethod
    def close(self):
        """Close the sensors serial port"""
        pass
