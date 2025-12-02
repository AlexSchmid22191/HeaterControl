import configparser
import os
import time

from PySide6.QtCore import QTimer, QThreadPool
from scipy.stats import linregress

from src.Drivers.BaseClasses import AbstractController
from src.Drivers.HCS import HCS34
from src.Drivers.Software_PID import SoftwarePID
from src.Drivers.Tenma import Tenma
from src.Engine.Worker import Worker
from src.Signals import engine_signals, gui_signals


class ResistiveHeater(AbstractController):
    mode = 'Temperature'

    def __init__(self, parent_engine, _port_name, power_supply=None, config_fname=None, *args, **kwargs):

        self.engine = parent_engine
        self.config_fname = config_fname
        self.power_supply = power_supply(_port_name)

        config = self.read_from_config()

        self.working_setpoint = 25
        self.target_setpoint = 25

        self.smoothed_temperature = 25
        self.smoothing_factor = 0.8

        self.max_voltage = config['Heater']['U_max']
        self.max_current = config['Heater']['I_max']
        self.min_output = config['Heater']['P_min']

        self.power_supply.set_voltage_limit(self.max_voltage)
        self.control_mode = 'Manual'

        self.manual_output_power = 0
        self.working_power = 0

        self.rate = config['Control']['Rate']

        # Timer for automatic ramping mode
        self.loop_time = 250
        self.timer = QTimer()
        self.timer.timeout.connect(self._control_loop)
        self.timer.start(self.loop_time)

        # Take heater resistance from the config file
        self.r_cold = config['Heater']['R_cold']
        self.wire_geometry_factor = 0.2075 / self.r_cold

        pb = config['PID']['P']
        ti = config['PID']['I']
        td = config['PID']['D']
        self.pid_controller = SoftwarePID(pb, ti, td, loop_interval=self.loop_time / 1000)

        # Used for ensuring that sensor values arrive at least every 2 seconds in external pv mode
        self.external_pv_mode = False
        self.external_pv = 0
        self.sentinel_timer = QTimer(singleShot=True)
        self.sentinel_timer.setInterval(2000)
        self.sentinel_timer.timeout.connect(self.sentinel_trip)

        gui_signals.get_resistive_heater_config.connect(self.report_heater_config)
        gui_signals.set_resistive_heater_config.connect(self.update_config)
        gui_signals.get_calibration_data.connect(self.calibrate)

    def close(self):
        self.timer.stop()
        self.power_supply.close()

    def set_external_pv_mode(self, mode):
        self.external_pv_mode = mode
        self.working_setpoint = self.external_pv if mode else self.get_process_variable()
        self.pid_controller.output_sum = 0
        if self.external_pv_mode:
            self.sentinel_timer.start()
        else:
            self.sentinel_timer.stop()

    def update_external_pv(self, value):
        self.external_pv = value
        if self.external_pv_mode:
            self.sentinel_timer.start()

    def sentinel_trip(self):
        self.external_pv = 0
        self.set_external_pv_mode(False)
        engine_signals.error.emit('Did not receive PV value from sensor in time. Reverting to normal control mode!')

    def _control_loop(self):
        if self.control_mode == 'Manual':
            self.working_power = self.manual_output_power
        else:
            self._working_setpoint_adjust()
            pv = self.external_pv if self.external_pv_mode else self.get_process_variable()
            pid_result = (self.pid_controller.calculate_output(pv, self.working_setpoint)
                          or self.working_power)

            self.working_power = max(pid_result, self.min_output)

        self.power_supply.set_current_limit(self.working_power / 100 * self.max_current)

    def _working_setpoint_adjust(self):
        increment = self.rate * self.loop_time / 1000 / 60
        if self.working_setpoint < self.target_setpoint:
            self.working_setpoint = min(self.working_setpoint + increment, self.target_setpoint)
        elif self.working_setpoint > self.target_setpoint:
            self.working_setpoint = max(self.working_setpoint - increment, self.target_setpoint)

    def _temp_from_resistance(self, resistance):
        """
        Calculates the heater coil temperature based on heater coil resistance.
        Equation is based on empirical data from the ceramic sputter device
        and known temperature dependence of heater coil resistance.
        Should be generalized in the future.
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
        # Reset the error accumulator on each switch to automatic mode to avoid windup
        self.pid_controller.output_sum = 0
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
        config = configparser.ConfigParser()
        config['PID'] = {'P': str(self.pid_controller.pb),
                         'I': str(self.pid_controller.ti),
                         'D': str(self.pid_controller.td)}
        config['Control'] = {'Rate': str(self.rate)}
        config['Heater'] = {'R_cold': str(self.r_cold), 'U_max': str(self.max_voltage), 'I_max': str(self.max_current),
                            'P_min': str(self.min_output)}

        config_file_path = os.path.join(directory := os.path.join(os.getenv('APPDATA'), 'ElchiWorks', 'ElchiTools'),
                                        self.config_fname)

        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    def read_from_config(self):
        config = configparser.ConfigParser()
        config_file_path = os.path.join(os.getenv('APPDATA'), 'ElchiWorks', 'ElchiTools', self.config_fname)
        if os.path.exists(config_file_path):
            config.read(config_file_path)

            return {'PID': {'P': config.getfloat('PID', 'P', fallback=750),
                            'I': config.getfloat('PID', 'I', fallback=12),
                            'D': config.getfloat('PID', 'D', fallback=20)},
                    'Control': {
                        'Rate': config.getfloat('Control', 'Rate', fallback=15)},
                    'Heater': {
                        'R_cold': config.getfloat('Heater', 'R_cold', fallback=0.5),
                        'U_max': config.getfloat('Heater', 'U_max', fallback=10),
                        'I_max': config.getfloat('Heater', 'I_max', fallback=10),
                        'P_min': config.getfloat('Heater', 'P_min', fallback=10)}}

        else:
            return {'PID': {'P': 750, 'I': 12, 'D': 20},
                    'Control': {'Rate': 15},
                    'Heater': {'R_cold': 0.528, 'U_max': 10, 'I_max': 10, 'P_min': 10}}

    def update_config(self, parameters):
        self.max_voltage = parameters['maximum voltage']
        self.max_current = parameters['maximum current']
        self.r_cold = parameters['cold resistance']
        self.wire_geometry_factor = 0.2075 / self.r_cold
        self.min_output = parameters['minimum output']
        self.write_config_to_file()

        self.power_supply.set_voltage_limit(self.max_voltage)

    def report_heater_config(self):
        parameters = {'cold resistance': self.r_cold, 'maximum current': self.max_current,
                      'maximum voltage': self.max_voltage, 'minimum output': self.min_output}
        engine_signals.resistive_heater_config_update.emit(parameters)

    def calibrate(self):
        engine_signals.message.emit('Calibrating heater. Please wait...')

        def _calib():
            u = []
            j = []
            for i in range(10):
                self.set_manual_output_power(i + 1)
                time.sleep(1)
                u.append(self.power_supply.get_voltage())
                j.append(self.power_supply.get_current())
            self.set_manual_output_power(0)
            try:
                slope, intercept, r_value, p_value, std_err = linregress(j, u)
                return {'U': u, 'I': j, 'R': slope, 'OS': intercept, 'R2': r_value, 'State': 'Success'}
            except ValueError:
                return {'State': 'Fail'}

        worker = Worker(_calib)
        worker.signals.over.connect(
            lambda result: engine_signals.calibration_data_update.emit(result))
        worker.signals.error.connect(lambda error: engine_signals.error.emit(error))
        QThreadPool.globalInstance().start(worker)


class ResistiveHeaterTenma(ResistiveHeater):
    def __init__(self, _port_name, *args, **kwargs):
        super().__init__(_port_name=_port_name, power_supply=Tenma, config_fname='Tenma.ini', *args, **kwargs)

    def enable_output(self):
        self.power_supply.enable_output()

    def disable_output(self):
        self.power_supply.disable_output()


class ResistiveHeaterHCS(ResistiveHeater):
    def __init__(self, _port_name, *args, **kwargs):
        super().__init__(_port_name=_port_name, power_supply=HCS34, config_fname='HCS.ini', *args, **kwargs)
