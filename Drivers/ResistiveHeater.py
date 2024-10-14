from PySide2.QtCore import QTimer

from Drivers.AbstractSensorController import AbstractController
from Drivers.HCS import HCS34


class CeramicSputterHeater(AbstractController):
    mode = 'Temperature'

    def __init__(self, portname, *args, **kwargs):
        self.power_supply = HCS34(portname)
        self.power_supply.set_voltage_limit(10)
        self.control_mode = 'Manual'

        self.manual_output_power = 0
        self.working_power = 0

        self.rate = 15
        self.working_setpoint = 25
        self.target_setpoint = 25

        # Timer for automatic ramping mode
        self.loop_time = 250
        self.timer = QTimer()
        self.timer.timeout.connect(self._control_loop)
        self.timer.start(self.loop_time)

        # Hard coded resistance at 25 Celsius, should be made variable in the future
        self.r_cold = 0.528
        self.wire_geometry_factor = 0.2075 / self.r_cold

    @staticmethod
    def _current_from_temp(t_set):
        """Calculates the required current to achive a temperature of t_set"""
        return 0

    def _control_loop(self):
        if self.control_mode == 'Manual':
            self.working_power = self.manual_output_power
        else:
            self._working_setpoint_adjust()
            self.working_power = self._current_from_temp(self.working_setpoint)

        self.power_supply.set_current_limit(self.working_power / 10)

    def _working_setpoint_adjust(self):
        increment = self.rate * self.loop_time / 1000 / 60
        if self.working_setpoint < self.target_setpoint:
            self.working_setpoint = min(self.working_setpoint + increment, self.target_setpoint)
        elif self.working_setpoint > self.target_setpoint:
            self.working_setpoint = max(self.working_setpoint - increment, self.target_setpoint)

    def _temp_from_resistance(self, resistance):
        """
        Calcualtes heater coil temeprture based on heater coil resistance.
        Equation is absed on empirical data from the ceramic sputter device
        and known temeprature dependence of heater coil resistance.
        Should be generalised in the future
        """
        return (resistance * self.wire_geometry_factor - 0.2) / 0.0003

    def get_process_variable(self):
        resistance = self.power_supply.get_resistance()
        if resistance == -1:
            return -1
        return self._temp_from_resistance(resistance)

    def set_manual_output_power(self, output):
        self.manual_output_power = output

    def get_working_output(self):
        return self.working_power

    def get_rate(self):
        return self.rate

    def get_target_setpoint(self):
        return self.target_setpoint

    def get_working_setpoint(self):
        return self.working_setpoint

    def get_control_mode(self):
        return self.control_mode

    def set_target_setpoint(self, setpoint):
        self.target_setpoint = setpoint

    def set_rate(self, rate):
        self.rate = rate

    def set_manual_mode(self):
        self.control_mode = 'Manual'

    def set_automatic_mode(self):
        self.control_mode = 'Automatic'
