from abc import ABC, abstractmethod
from enum import auto, Enum
from typing import Set


class UnitType(Enum):
    TEMPERATURE = auto()
    VOLTAGE = auto()


class SensorFeatures(Enum):
    AIMING_BEAM = auto()
    TC_SELECT = auto()


class ControllerFeatures(Enum):
    SIMPLE_PID = auto()
    GAIN_SCHEDULING = auto()
    AIMING_BEAM = auto()
    OUTPUT_ENABLE = auto()
    EXTERNAL_PV = auto()
    MANUAL_POWER = auto()
    EXT_CONFIG = auto()
    TC_SELECT = auto()


class AbstractController(ABC):
    """
    Abstract base class for controllers. Drivers for specific devices inherit this class and implement the methods.
    Core functionality is mandatory and has to be overridden.
    Optional functionality raises an exception if the methods are not overwritten in derived subclasses.
    """
    type: UnitType
    features: Set[ControllerFeatures] = set()

    # Mandatory methods ------------------------------------------------------------------------------------------------

    @abstractmethod
    def __init__(self, _port_name: str, _slave_address: int = 1):
        """Init"""

    @abstractmethod
    def get_process_variable(self) -> float:
        """Return the current process variable of the controller (often this is the oven thermocouple temperature)"""

    @abstractmethod
    def get_working_output(self) -> float:
        """Return the current power output of the controller in percent"""

    @abstractmethod
    def get_working_setpoint(self) -> float:
        """Get the current working setpoint of the controller"""

    @abstractmethod
    def get_target_setpoint(self) -> float:
        """Get the target setpoint"""

    @abstractmethod
    def set_target_setpoint(self, setpoint: float) -> None:
        """Set the target setpoint"""

    @abstractmethod
    def get_rate(self) -> float:
        """Get the rate of change for the working setpoint"""

    @abstractmethod
    def set_rate(self, rate: float) -> None:
        """Set the rate of change for the working setpoint"""

    @abstractmethod
    def get_control_mode(self) -> str:
        """Get the active control mode"""

    @abstractmethod
    def set_automatic_mode(self) -> None:
        """Set controller to automatic mode, PID controls output power"""

    @abstractmethod
    def set_manual_mode(self) -> None:
        """Set controller to manual mode, output power is held constant"""

    @abstractmethod
    def close(self) -> None:
        """Close the controller serial port"""

    @abstractmethod
    def emergency_stop(self) -> None:
        """Stop the controller immediately"""

    # Optional methods -------------------------------------------------------------------------------------------------

    def set_manual_output_power(self, output: float) -> None:
        """Set the power output of the controller in percent"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_manual_output_power', self.__class__.__name__))

    def get_manual_output_power(self) -> float:
        """Get the power output of the controller in percent"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_manual_output_power', self.__class__.__name__))

    def get_pid_p(self) -> float:
        """Get the P (Proportional band) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_p', self.__class__.__name__))

    def set_pid_p(self, p: float) -> None:
        """Set the P (Proportional band) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_p', self.__class__.__name__))

    def get_pid_p2(self) -> float:
        """Get the P2 (Proportional band) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_p2', self.__class__.__name__))

    def set_pid_p2(self, p: float) -> None:
        """Set the P2 (Proportional band) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_p2', self.__class__.__name__))

    def get_pid_p3(self) -> float:
        """Get the P3 (Proportional band) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_p3', self.__class__.__name__))

    def set_pid_p3(self, p: float) -> None:
        """Set the P3 (Proportional band) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_p3', self.__class__.__name__))

    def get_pid_i(self) -> float:
        """Get the I (Integral time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_i', self.__class__.__name__))

    def set_pid_i(self, i: float) -> None:
        """Set the I (Integral time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_i', self.__class__.__name__))

    def get_pid_i2(self) -> float:
        """Get the I2 (Integral time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_i2', self.__class__.__name__))

    def set_pid_i2(self, i: float) -> None:
        """Set the I2 (Integral time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_i2', self.__class__.__name__))

    def get_pid_i3(self) -> float:
        """Get the I3 (Integral time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_i3', self.__class__.__name__))

    def set_pid_i3(self, i: float) -> None:
        """Set the I3 (Integral time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_i3', self.__class__.__name__))

    def get_pid_d(self) -> float:
        """Get the D (Derivative time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_d', self.__class__.__name__))

    def set_pid_d(self, d: float) -> None:
        """Set the D (Derivative time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_d', self.__class__.__name__))

    def get_pid_d2(self) -> float:
        """Get the D2 (Derivative time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_d2', self.__class__.__name__))

    def set_pid_d2(self, d: float) -> None:
        """Set the D2 (Derivative time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_d2', self.__class__.__name__))

    def get_pid_d3(self) -> float:
        """Get the D3 (Derivative time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_pid_d3', self.__class__.__name__))

    def set_pid_d3(self, d: float) -> None:
        """Set the D3 (Derivative time) for the PID controller"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_pid_d3', self.__class__.__name__))

    def get_boundary_12(self) -> float:
        """Get the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_boundary_12', self.__class__.__name__))

    def set_boundary_12(self, boundary: float) -> None:
        """Set the boundary between Set 1 and 2 of PID parameters for gain scheduling"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_boundary_12', self.__class__.__name__))

    def get_boundary_23(self) -> float:
        """Get the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_boundary_23', self.__class__.__name__))

    def set_boundary_23(self, boundary: float) -> None:
        """Set the boundary between Set 2 and 3 of PID parameters for gain scheduling"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_boundary_23', self.__class__.__name__))

    def get_gain_scheduling(self) -> str:
        """Get the gain scheduling mode"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_gain_scheduling', self.__class__.__name__))

    def set_gain_scheduling(self, mode: str) -> None:
        """Set the gain scheduling mode"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_gain_scheduling', self.__class__.__name__))

    def get_active_set(self) -> int:
        """Get the currently active set of PID parameters"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_active_set', self.__class__.__name__))

    def set_active_set(self, active_set: int) -> None:
        """Set the currently active set of PID parameters"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_active_set', self.__class__.__name__))

    def enable_aiming_beam(self) -> None:
        """Toggle the aiming beam on/off"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('enable_aiming_beam', self.__class__.__name__))

    def disable_aiming_beam(self) -> None:
        """Toggle the aiming beam on/off"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('disable_aiming_beam', self.__class__.__name__))

    def enable_output(self) -> None:
        """Enable the output"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('enable_output', self.__class__.__name__))

    def disable_output(self) -> None:
        """Disable the output"""
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('disable_output', self.__class__.__name__))

    def update_external_pv(self, value: float) -> None:
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('update_external_pv', self.__class__.__name__))

    def set_external_pv_mode(self, mode: bool) -> None:
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_external_pv_mode', self.__class__.__name__))

    def set_tc_type(self, tc: str) -> None:
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_tc_type', self.__class__.__name__))

    def get_tc_type(self) -> str:
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_tc_type', self.__class__.__name__))


class AbstractSensor(ABC):
    """
    Abstract base class for sensors. Drivers for specific devices inherit this class and implement the read method.
    Raises a NotImplementedException if the methods are not overwritten in derived subclasses.
    """

    type: UnitType
    features: Set[SensorFeatures] = set()

    @abstractmethod
    def __init__(self, _port: str):
        """Init"""

    @abstractmethod
    def get_sensor_value(self) -> float:
        """Return the current readout value of the sensor"""

    @abstractmethod
    def close(self) -> None:
        """Close the sensors serial port"""
        pass

    def switch_aiming_beam(self, state: bool) -> None:
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('switch_aiming_beam', self.__class__.__name__))

    def set_sensor_tc(self, tc: str) -> None:
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('set_sensor_tc', self.__class__.__name__))

    def get_sensor_tc(self) -> str:
        raise NotImplementedError(
            'Operation {:s} not supported for {:s} yet!'.format('get_sensor_tc', self.__class__.__name__))
