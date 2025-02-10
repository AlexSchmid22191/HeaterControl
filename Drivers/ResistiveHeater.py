import configparser
import os

from PySide2.QtCore import QTimer

from Drivers.AbstractSensorController import AbstractController
from Drivers.HCS import HCS34
from Drivers.Software_PID import SoftwarePID


class CeramicSputterHeater(AbstractController):
    mode = 'Temperature'

    def __init__(self, portname, *args, **kwargs):
        self.config_dir_path = os.path.join(os.getenv('APPDATA'), 'ElchiWorks', 'ElchiTools')
        config = self.read_from_config()

        self.power_supply = HCS34(portname)
        self.max_voltage = config['Heater']['U_max']
        self.power_supply.set_voltage_limit(self.max_voltage)
        self.control_mode = 'Manual'

        self.manual_output_power = 0
        self.working_power = 0

        self.rate = config['Control']['Rate']
        self.working_setpoint = 25
        self.target_setpoint = 25

        self.smoothed_temperature = 25
        self.smoothing_factor = 0.8

        # Timer for automatic ramping mode
        self.loop_time = 250
        self.timer = QTimer()
        self.timer.timeout.connect(self._control_loop)
        self.timer.start(self.loop_time)

        # Take heater resistance from config file
        self.r_cold = config['Heater']['R_cold']
        self.wire_geometry_factor = config['Heater']['Geom_factor']

        pb = config['PID']['P']
        ti = config['PID']['I']
        td = config['PID']['D']
        self.pid_controller = SoftwarePID(pb, ti, td, loop_interval=self.loop_time / 1000)

    @staticmethod
    def _power_from_temp(t_set):
        """
        Calculates the required set current to achive a temperature of t_set
        Uses a quadratic fit to approximate data meaasured on ceramic sputter device
        Warning: Even at 0 Celsius set this approximation yields a current of 0.84 A
        """
        # Calibration using measured curernts
        # current = 0.84347681 + 0.00105813 * t_set + 4.52795972e-06 * t_set**2
        # Calibration using set currents
        current = 0.91967429 + 0.00111274 * t_set + 4.46679138e-06 * t_set ** 2
        # Constrain pwoer to 0 - 100
        return max(0, min(current * 10, 100))

    def _control_loop(self):

        if self.control_mode == 'Manual':
            self.working_power = self.manual_output_power
        else:
            self._working_setpoint_adjust()
            self.working_power = self.pid_controller.calculate_output(self.get_process_variable(),
                                                                      self.working_setpoint)

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
            resistance = self.r_cold

        new_temperature = self._temp_from_resistance(resistance)
        self.smoothed_temperature *= self.smoothing_factor
        self.smoothed_temperature += new_temperature * (1 - self.smoothing_factor)

        return self.smoothed_temperature

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
        self.write_config_to_file()

    def set_manual_mode(self):
        self.manual_output_power = self.working_power
        self.control_mode = 'Manual'

    def set_automatic_mode(self):
        self.working_setpoint = self.get_process_variable()
        self.control_mode = 'Automatic'

    def set_pid_p(self, p):
        self.pid_controller.pb = p
        self.write_config_to_file()

    def set_pid_i(self, i):
        self.pid_controller.ti = i
        self.write_config_to_file()

    def set_pid_d(self, d):
        self.pid_controller.td = d
        self.write_config_to_file()

    def get_pid_p(self):
        return self.pid_controller.pb

    def get_pid_i(self):
        return self.pid_controller.ti

    def get_pid_d(self):
        return self.pid_controller.td

    def write_config_to_file(self):
        if not os.path.exists(self.config_dir_path):
            os.makedirs(self.config_dir_path)

        # Define the config file path
        config_file_path = os.path.join(self.config_dir_path, 'HCS34.ini')
        config = configparser.ConfigParser()
        config['PID'] = {'P': str(self.pid_controller.pb),
                         'I': str(self.pid_controller.ti),
                         'D': str(self.pid_controller.td)}
        config['Control'] = {'Rate': str(self.rate)}
        config['Heater'] = {'R_cold': str(self.r_cold), 'Geom_factor': str(self.wire_geometry_factor),
                            'U_max': str(self.max_voltage)}

        # Writing to config.ini file
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    def read_from_config(self):
        config = configparser.ConfigParser()
        config_file_path = os.path.join(self.config_dir_path, 'HCS34.ini')
        if os.path.exists(config_file_path):
            config.read(config_file_path)

            return {'PID': {'P': config.getfloat('PID', 'P', fallback=750),
                            'I': config.getfloat('PID', 'I', fallback=12),
                            'D': config.getfloat('PID', 'D', fallback=20)},
                    'Control': {
                        'Rate': config.getfloat('Control', 'Rate', fallback=15)},
                    'Heater': {
                        'R_cold': config.getfloat('Heater', 'R_cold', fallback=0.5),
                        'Geom_factor': config.getfloat('Heater', 'Geom_factor', fallback=0.4),
                        'U_max': config.getfloat('Heater', 'U_max', fallback=10)}}

        else:
            return {'PID': {'P': 750, 'I': 12, 'D': 20},
                    'Control': {'Rate': 15},
                    'Heater': {'R_cold': 0.528, 'Geom_factor': 0.3929, 'U_max': 10}}
