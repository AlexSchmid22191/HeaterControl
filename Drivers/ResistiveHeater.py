from AbstractSensorController import AbstractController
from HCS import HCS34
from threading import Lock
from PySide2.QtCore import QTimer


class CeramicSputterHeater(AbstractController):
    def __init__(self, portname, slaveadress, *args, **kwargs):
        self.power_supply = HCS34(portname)
        self.power_supply.set_voltage_limit()
        self.mode = 'Manual'
        self.isRamping = False

        self.rate = 15
        self.working_setpoint = 25
        self.target_setpoint = 25

        # In automatic mode the ramp function is run in a separate thread, so a Lock is required
        self.lock = Lock()

        # Timer for automatic ramping mode
        self.timer = QTimer(1)




    def _current_from_temp(self, t_set):
        """Calculates the required current to achive a temperature of t_set"""
        return





    @staticmethod
    def _temp_from_resistance(resistance):
        """
        Calcualtes heater coil temeprture based on heater coil resistance.
        Equation is absed on empirical data from the ceramic sputter device
        and known temeprature dependence of heater coil resistance.
        Should be generalised in the future
        """
        return (resistance/1.06 - 0.2) / 0.0003

    def get_process_variable(self):
        resistance = self.power_supply.get_resistance()
        return self._temp_from_resistance(resistance)

    def set_manual_output_power(self, output):
        self.power_supply.set_current_limit(output / 10)

    def get_working_output(self):
        return self.power_supply.get_current() * 10

    def get_rate(self):
        return self.rate

    def get_target_setpoint(self):
        return self.target_setpoint

    def get_working_setpoint(self):
        return self.working_setpoint

    def get_control_mode(self):
        return self.mode

    def set_target_setpoint(self, setpoint):
        self.target_setpoint = setpoint

    def set_rate(self, rate):
        self.rate = rate




