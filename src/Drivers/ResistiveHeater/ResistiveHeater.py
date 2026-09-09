import configparser
import os
import time

from PySide6.QtCore import QThreadPool, QTimer
from scipy.stats import linregress

from src.Drivers.ResistiveHeater.ResHeaterConfig import *
from src.Drivers.BaseClasses import AbstractController, AbstractPowerSupply, ControllerFeatures, UnitType
from src.Drivers.HCS import HCS34
from src.Drivers.Software_PID import SoftwarePID
from src.Drivers.Tenma import Tenma
from src.Engine.Worker import Worker
from src.Signals import engine_signals, gui_signals


class ResistiveHeater(AbstractController):
    controller_type = UnitType.TEMPERATURE
    features = {ControllerFeatures.SIMPLE_PID, ControllerFeatures.MANUAL_POWER, ControllerFeatures.EXTERNAL_PV,
                ControllerFeatures.EXT_CONFIG}

    def __init__(self, _port_name: str, power_supply: type[AbstractPowerSupply], config_name: str):

        self.config_name = config_name
        self.port = _port_name
        self.power_supply: AbstractPowerSupply = power_supply(_port_name)

        self.workers: list[Worker] = []

        config = self.read_from_config()

        self.working_setpoint: float = 25
        self.target_setpoint: float = 25

        self.manual_output_power: float = 0
        self.working_power: float = 0

        self.smoothed_temperature: float = 25
        self.smoothing_factor: float = 0.8

        self.max_voltage = config.heater.max_voltage
        self.max_current = config.heater.max_current
        self.min_output = config.heater.min_output
        self.r_cold = config.heater.r_cold

        self.offset = config.material.offset
        self.slope = config.material.slope
        self.wire_geometry_factor: float = 0.2075 / self.r_cold

        self.rate = config.control.rate

        # Timer for automatic ramping mode
        self.loop_time: int = 250
        self.timer = QTimer()
        self.timer.timeout.connect(self._control_loop)
        self.timer.start(self.loop_time)
        self.pid_controller = SoftwarePID(config.pid.p, config.pid.i, config.pid.d, loop_interval=self.loop_time / 1000)

        self.power_supply.set_voltage_limit(self.max_voltage)
        self.control_mode = 'Manual'

        # Used for ensuring that sensor values arrive at least every 2 seconds in external pv mode
        self.external_pv_mode: bool = False
        self.external_pv: float = 0
        self.sentinel_timer = QTimer()
        self.sentinel_timer.setSingleShot(True)
        self.sentinel_timer.setInterval(2000)
        self.sentinel_timer.timeout.connect(self.sentinel_trip)

        gui_signals.get_resistive_heater_config.connect(self.report_heater_config)
        gui_signals.set_resistive_heater_config.connect(self.update_config)
        gui_signals.get_calibration_data.connect(self.calibrate)

    def close(self) -> None:
        self.timer.stop()
        self.power_supply.close()

    def set_external_pv_mode(self, mode: bool) -> None:
        self.external_pv_mode = mode
        self.working_setpoint = self.external_pv if mode else self.get_process_variable()
        self.pid_controller.output_sum = 0
        if self.external_pv_mode:
            self.sentinel_timer.start()
        else:
            self.sentinel_timer.stop()

    def update_external_pv(self, value: float) -> None:
        self.external_pv = value
        if self.external_pv_mode:
            self.sentinel_timer.start()

    def sentinel_trip(self) -> None:
        self.external_pv = 0
        self.set_external_pv_mode(False)
        engine_signals.error.emit('Did not receive PV value from sensor in time. Reverting to normal control mode!')

    def _control_loop(self) -> None:
        if self.control_mode == 'Manual':
            self.working_power = self.manual_output_power
        else:
            self._working_setpoint_adjust()
            pv = self.external_pv if self.external_pv_mode else self.smoothed_temperature
            pid_result = (self.pid_controller.calculate_output(pv, self.working_setpoint) or self.working_power)

            self.working_power = max(pid_result, self.min_output)

        worker = Worker(lambda: self.power_supply.set_current_limit(self.working_power / 100 * self.max_current))
        self.workers.append(worker)
        worker.signals.error.connect(lambda error: engine_signals.error.emit(error))
        worker.signals.finished.connect(lambda w=worker: self.workers.remove(w))
        QThreadPool.globalInstance().start(worker)

    def _working_setpoint_adjust(self) -> None:
        increment = self.rate * self.loop_time / 1000 / 60
        if self.working_setpoint < self.target_setpoint:
            self.working_setpoint = min(self.working_setpoint + increment, self.target_setpoint)
        elif self.working_setpoint > self.target_setpoint:
            self.working_setpoint = max(self.working_setpoint - increment, self.target_setpoint)

    def _temp_from_resistance(self, resistance: float) -> float:
        """
        Calculates the heater coil temperature based on heater coil resistance.
        Slope and offset are the coefficients of a linear equation that converts resistivity to temperature.
        """
        return (resistance * self.wire_geometry_factor - self.offset) / self.slope

    def get_process_variable(self) -> float:
        resistance = self.power_supply.get_resistance()
        if resistance == -1:
            resistance = self.r_cold

        new_temperature = self._temp_from_resistance(resistance)
        self.smoothed_temperature *= self.smoothing_factor
        self.smoothed_temperature += new_temperature * (1 - self.smoothing_factor)

        return self.smoothed_temperature

    def set_manual_output_power(self, output: float) -> None:
        self.manual_output_power = output

    def get_working_output(self) -> float:
        return self.working_power

    def get_manual_output_power(self) -> float:
        return self.manual_output_power

    def get_rate(self) -> float:
        return self.rate

    def get_target_setpoint(self) -> float:
        return self.target_setpoint

    def get_working_setpoint(self) -> float:
        return self.working_setpoint

    def get_control_mode(self) -> str:
        return self.control_mode

    def set_target_setpoint(self, setpoint: float) -> None:
        self.target_setpoint = setpoint

    def set_rate(self, rate: float) -> None:
        self.rate = rate
        self.write_config_to_file()

    def set_manual_mode(self) -> None:
        self.manual_output_power = self.working_power
        self.control_mode = 'Manual'

    def set_automatic_mode(self) -> None:
        self.working_setpoint = self.get_process_variable()
        # Reset the error accumulator on each switch to automatic mode to avoid windup
        self.pid_controller.output_sum = 0
        self.control_mode = 'Automatic'

    def set_pid_p(self, p: float) -> None:
        self.pid_controller.pb = p
        self.write_config_to_file()

    def set_pid_i(self, i: float) -> None:
        self.pid_controller.ti = i
        self.write_config_to_file()

    def set_pid_d(self, d: float) -> None:
        self.pid_controller.td = d
        self.write_config_to_file()

    def get_pid_p(self) -> float:
        return self.pid_controller.pb

    def get_pid_i(self) -> float:
        return self.pid_controller.ti

    def get_pid_d(self) -> float:
        return self.pid_controller.td

    def write_config_to_file(self) -> None:
        config = configparser.ConfigParser()
        app_data = os.getenv('APPDATA')
        if not app_data:
            raise ValueError("APPDATA environment variable not found")
        else:
            config_file_dir = os.path.join(app_data, 'ElchWorks', 'ElchiTools')
        config_file_path = os.path.join(config_file_dir, self.config_name)
        if os.path.exists(config_file_path):
            config.read(config_file_path)
        else:
            os.makedirs(config_file_dir, exist_ok=True)

        config[self.port] = {'P':     str(self.pid_controller.pb), 'I': str(self.pid_controller.ti),
                             'D':     str(self.pid_controller.td), 'Rate': str(self.rate), 'R_cold': str(self.r_cold),
                             'U_max': str(self.max_voltage), 'I_max': str(self.max_current),
                             'P_min': str(self.min_output), 'Offset': str(self.offset), 'Slope': str(self.slope)}

        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    def read_from_config(self) -> ResistiveHeaterConfig:
        config = configparser.ConfigParser()

        app_data = os.getenv("APPDATA")
        if not app_data:
            raise ValueError("APPDATA environment variable not set")

        config_file_path = os.path.join(app_data, "ElchWorks", "ElchiTools", self.config_name)
        if os.path.exists(config_file_path):
            config.read(config_file_path)
            if self.port in config.sections():
                engine_signals.message.emit(f"Using configuration file for port {self.port}!")
            else:
                engine_signals.message.emit(f"No configuration file found for port {self.port}, using defaults!")
        else:
            engine_signals.message.emit("No configuration file found, using defaults!")

        pid_conf = PIDConfig(p=config.getfloat(self.port, "P", fallback=750),
                             i=config.getfloat(self.port, "I", fallback=12),
                             d=config.getfloat(self.port, "D", fallback=0))
        heater_conf = HeaterConfig(r_cold=config.getfloat(self.port, "R_cold", fallback=0.5),
                                   max_voltage=config.getfloat(self.port, "U_max", fallback=10),
                                   max_current=config.getfloat(self.port, "I_max", fallback=10),
                                   min_output=config.getfloat(self.port, "P_min", fallback=10))
        control_conf = ControlConfig(rate=config.getfloat(self.port, "Rate", fallback=15))
        material_conf = MaterialConfig(offset=config.getfloat(self.port, "Offset", fallback=0.2),
                                       slope=config.getfloat(self.port, "Slope", fallback=0.0003))

        return ResistiveHeaterConfig(pid=pid_conf, control=control_conf, heater=heater_conf, material=material_conf)

    def update_config(self, parameters: HeaterConfig) -> None:
        self.max_voltage = parameters.max_voltage
        self.max_current = parameters.max_current
        self.r_cold = parameters.r_cold
        self.wire_geometry_factor = 0.2075 / self.r_cold
        self.min_output = parameters.min_output
        self.write_config_to_file()
        self.power_supply.set_voltage_limit(self.max_voltage)

    def report_heater_config(self) -> None:
        parameters = HeaterConfig(r_cold=self.r_cold, max_current=self.max_current, max_voltage=self.max_voltage,
                                  min_output=self.min_output)
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
                slope, intercept, r_value, *_ = linregress(j, u)
                return {'U': u, 'I': j, 'R': slope, 'OS': intercept, 'R2': r_value, 'State': 'Success'}
            except ValueError:
                return {'State': 'Fail'}

        worker = Worker(_calib)
        self.workers.append(worker)
        worker.signals.over.connect(lambda result: engine_signals.calibration_data_update.emit(result))
        worker.signals.error.connect(lambda error: engine_signals.error.emit(error))
        worker.signals.finished.connect(lambda w=worker: self.workers.remove(w))
        QThreadPool.globalInstance().start(worker)

    def emergency_stop(self) -> None:
        self.set_manual_mode()
        self.set_manual_output_power(0)


class ResistiveHeaterTenma(ResistiveHeater):
    features = ResistiveHeater.features | {ControllerFeatures.OUTPUT_ENABLE}

    def __init__(self, _port_name: str):
        super().__init__(_port_name=_port_name, power_supply=Tenma, config_name='Tenma.ini')

    def enable_output(self) -> None:
        self.power_supply.enable_output()

    def disable_output(self) -> None:
        self.power_supply.disable_output()


class ResistiveHeaterHCS(ResistiveHeater):
    def __init__(self, _port_name: str):
        super().__init__(_port_name=_port_name, power_supply=HCS34, config_name='HCS.ini')
