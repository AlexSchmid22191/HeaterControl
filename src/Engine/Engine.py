import math
from typing import Type
from datetime import timezone, datetime

import serial.tools.list_ports
from PySide2.QtCore import QThreadPool, QTime, QTimer
from minimalmodbus import NoResponseError
from serial import SerialException

from src.Drivers.BaseClasses import AbstractController, AbstractSensor
from src.Drivers.ElchWorks import Thermolino, Thermoplatino, ElchLaser
from src.Drivers.Eurotherms import Eurotherm3216, Eurotherm3508, Eurotherm2408, Eurotherm3508S
from src.Drivers.Jumo import JumoQuantol
from src.Drivers.Keithly import Keithly2000Temp, Keithly2000Volt
from src.Drivers.Omega import OmegaPt
from src.Drivers.Pyrometer import Pyrometer
from src.Drivers.ResistiveHeater import ResistiveHeaterTenma, ResistiveHeaterHCS
from src.Drivers.TestDevices import TestSensor, TestController, NiceTestController
from src.Engine.SetProg import SetpointProgrammer
from src.Engine.ThreadDecorators import Worker
from src.Signals import engine_signals, gui_signals

TEST_MODE = True


class HeaterControlEngine:
    sensor: AbstractSensor
    controller: AbstractController
    programmer: SetpointProgrammer | None

    def __init__(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}
        self.controller_types: dict[str, Type[AbstractController]] = {
            'Eurotherm2408': Eurotherm2408,
            'Eurotherm3216': Eurotherm3216,
            'Eurotherm3508': Eurotherm3508,
            'Omega Pt': OmegaPt,
            'Jumo Quantrol': JumoQuantol,
            'Elchi Laser Control': ElchLaser,
            'Elchi Heater Controller': ElchLaser,
            'Resistive Heater Tenma': ResistiveHeaterTenma,
            'Resistive Heater HCS': ResistiveHeaterHCS
        }
        self.sensor_types: dict[str, Type[AbstractSensor]] = {
            'Pyrometer': Pyrometer,
            'Thermolino': Thermolino,
            'Thermoplatino': Thermoplatino,
            'Keithly2000 Temperature': Keithly2000Temp,
            'Keithly2000 Voltage': Keithly2000Volt,
            'Eurotherm3508': Eurotherm3508S
        }

        if TEST_MODE:
            self.sensor_types['Test Sensor'] = TestSensor
            self.controller_types['Test Controller'] = TestController
            self.controller_types['Nice Test Controller'] = NiceTestController
            self.available_ports['COM Test'] = 'Test Port'

        self.controller_slave_address = 1

        self.is_logging = False
        self.log_start_time = None
        self.data = {'Sensor PV': [], 'Controller PV': [], 'Setpoint': [], 'Power': []}

        self.mode = 'Temperature'
        self.units = {'Temperature': '°C', 'Voltage': 'mV'}

        gui_signals.set_units.connect(self.set_units)
        gui_signals.request_ports.connect(self.refresh_available_ports)
        gui_signals.connect_controller.connect(self.add_controller)
        gui_signals.connect_sensor.connect(self.add_sensor)

        gui_signals.export_log.connect(self.export_log)
        gui_signals.start_log.connect(self.start_logging)
        gui_signals.clear_log.connect(self.clear_log)

        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(1000)
        self.refresh_timer.setSingleShot(False)
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start()

        self.programmer = None

        self.pool = QThreadPool()

    def set_units(self, unit):
        self.mode = unit
        self.report_devices()

    def report_devices(self):
        mode = self.mode
        devices = {'Controller': [key for key, controller in self.controller_types.items() if controller.mode == mode],
                   'Sensor': [key for key, sensor in self.sensor_types.items() if sensor.mode == mode]}
        engine_signals.available_devices.emit(devices)

    def refresh_available_ports(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}
        if TEST_MODE:
            self.available_ports['COM Test'] = 'Test Port'
        engine_signals.available_ports.emit(self.available_ports)

    def add_sensor(self, sensor_type, sensor_port):
        try:
            self.sensor = self.sensor_types[sensor_type](port=sensor_port)
        except SerialException as e:
            engine_signals.connection_failed.emit(e)
        else:
            engine_signals.sensor_connected.emit(sensor_type, sensor_port)
            gui_signals.disconnect_sensor.connect(self.remove_sensor)
            gui_signals.connect_sensor.disconnect()

    def remove_sensor(self):
        gui_signals.disconnect_sensor.disconnect(self.remove_sensor)
        gui_signals.connect_sensor.connect(self.add_sensor)
        try:
            self.sensor.close()
        except SerialException as e:
            engine_signals.connection_failed.emit(f'Error when closing sensor: {e}')
        else:
            engine_signals.sensor_disconnected.emit()
        finally:
            del self.sensor

    def add_controller(self, controller_type, controller_port):
        try:
            self.controller = self.controller_types[controller_type](portname=controller_port,
                                                                     slaveadress=self.controller_slave_address)
        except (SerialException, NoResponseError) as e:
            engine_signals.connection_failed.emit(e)
        else:
            engine_signals.controller_connected.emit(controller_type, controller_port)

            gui_signals.disconnect_controller.connect(self.remove_controller)
            gui_signals.set_target_setpoint.connect(self.set_target_setpoint)
            gui_signals.set_rate.connect(self.set_rate)
            gui_signals.set_manual_output_power.connect(self.set_manual_output_power)
            gui_signals.set_control_mode.connect(self.set_control_mode)
            gui_signals.enable_output.connect(self.toggle_output_enable)
            gui_signals.toggle_aiming.connect(self.toggle_aiming_beam)
            gui_signals.refresh_status.connect(self.get_controller_status)
            gui_signals.refresh_parameters.connect(self.get_controller_parameters)
            gui_signals.set_pid_parameters.connect(self.set_pid_parameters)
            gui_signals.start_program.connect(self.start_programmer)
            gui_signals.connect_controller.disconnect()

            self.get_controller_parameters()
            self.get_pid_parameters()

    def remove_controller(self):
        gui_signals.disconnect_controller.disconnect(self.remove_controller)
        gui_signals.set_target_setpoint.disconnect(self.set_target_setpoint)
        gui_signals.set_rate.disconnect(self.set_rate)
        gui_signals.set_manual_output_power.disconnect(self.set_manual_output_power)
        gui_signals.set_control_mode.disconnect(self.set_control_mode)
        gui_signals.enable_output.disconnect(self.toggle_output_enable)
        gui_signals.toggle_aiming.disconnect(self.toggle_aiming_beam)
        gui_signals.refresh_status.disconnect(self.get_controller_status)
        gui_signals.set_pid_parameters.disconnect(self.set_pid_parameters)
        gui_signals.start_program.disconnect(self.start_programmer)

        gui_signals.connect_controller.connect(self.add_controller)

        try:
            self.controller.close()
        except SerialException as e:
            engine_signals.connection_failed.emit(f'Error when closing controller: {e}')
        else:
            engine_signals.controller_disconnected.emit()
        finally:
            del self.controller

    def refresh_status(self):
        if hasattr(self, 'sensor'):
            self.get_sensor_status()
        if hasattr(self, 'controller'):
            self.get_controller_status()

    def get_sensor_status(self):
        runtime = (datetime.now() - self.log_start_time).total_seconds() if self.log_start_time else None
        worker = Worker(self.sensor.get_sensor_value)
        worker.signals.over.connect(lambda result:
                                    engine_signals.sensor_status_update.emit({'Sensor PV': result}, runtime))
        if self.is_logging:
            worker.signals.over.connect(lambda result: self.add_log_data_point(data={'Sensor PV': result}))
        self.pool.start(worker)

    def get_controller_status(self):
        runtime = (datetime.now() - self.log_start_time).total_seconds() if self.log_start_time else None
        for parameter, function in {'Controller PV': self.controller.get_process_variable,
                                    'Setpoint': self.controller.get_working_setpoint,
                                    'Power': self.controller.get_working_output}.items():
            worker = Worker(function)
            worker.signals.over.connect(lambda result, _param=parameter:
                                        engine_signals.controller_status_update.emit({_param: result}, runtime))
            if self.is_logging:
                worker.signals.over.connect(lambda result, _param=parameter:
                                            self.add_log_data_point(data={_param: result}))
            self.pool.start(worker)

    def get_controller_parameters(self):
        for parameter, function in {'Setpoint': self.controller.get_target_setpoint,
                                    'Power': self.controller.get_working_output,
                                    'Rate': self.controller.get_rate,
                                    'Mode': self.controller.get_control_mode}.items():
            worker = Worker(function)
            worker.signals.over.connect(lambda result, _param=parameter:
                                        engine_signals.controller_parameters_update.emit({_param: result}))
            self.pool.start(worker)

    def set_control_mode(self, mode):
        function = self.controller.set_manual_mode if mode == 'Manual' else self.controller.set_automatic_mode
        worker = Worker(function)
        self.pool.start(worker)

    def set_target_setpoint(self, setpoint):
        worker = Worker(self.controller.set_target_setpoint, setpoint)
        self.pool.start(worker)

    def set_manual_output_power(self, power):
        worker = Worker(self.controller.set_manual_output_power, power)
        self.pool.start(worker)

    def set_rate(self, rate):
        worker = Worker(self.controller.set_rate, rate)
        self.pool.start(worker)

    def get_pid_parameters(self):
        for parameter, function in {'P1': self.controller.get_pid_p, 'P2': self.controller.get_pid_p2,
                                    'P3': self.controller.get_pid_p3, 'I1': self.controller.get_pid_i,
                                    'I2': self.controller.get_pid_i2, 'I3': self.controller.get_pid_i3,
                                    'D1': self.controller.get_pid_d, 'D2': self.controller.get_pid_d2,
                                    'D3': self.controller.get_pid_d3, 'B23': self.controller.get_boundary_23,
                                    'B12': self.controller.get_boundary_12, 'AS': self.controller.get_active_set,
                                    'GS': self.controller.get_gain_scheduling}.items():
            worker = Worker(function)
            worker.signals.over.connect(lambda result, _param=parameter:
                                        engine_signals.pid_parameters.emit({_param: result}))
            self.pool.start(worker)

    def set_pid_parameters(self, parameter, value):
        function = {'P1': self.controller.set_pid_p, 'P2': self.controller.set_pid_p2, 'P3': self.controller.set_pid_p3,
                    'I1': self.controller.set_pid_i, 'I2': self.controller.set_pid_i2, 'I3': self.controller.set_pid_i3,
                    'D1': self.controller.set_pid_d, 'D2': self.controller.set_pid_d2, 'D3': self.controller.set_pid_d3,
                    'B23': self.controller.set_boundary_23, 'B12': self.controller.set_boundary_12,
                    'GS': self.controller.set_gain_scheduling, 'AS': self.controller.set_active_set}[parameter]

        worker = Worker(function, value)
        self.pool.start(worker)

    def toggle_output_enable(self, state):
        function = self.controller.enable_output if state else self.controller.disable_output
        worker = Worker(function)
        self.pool.start(worker)

    def toggle_aiming_beam(self, state):
        function = self.controller.enable_aiming_beam if state else self.controller.disable_aiming_beam
        worker = Worker(function)
        self.pool.start(worker)

    def start_programmer(self, program):
        if self.programmer:
            self.programmer.timer.stop()
        self.programmer = SetpointProgrammer(program, self)
        gui_signals.skip_program.connect(self.skip_program_segment)
        gui_signals.stop_program.connect(self.stop_programmer)

    def stop_programmer(self):
        if self.programmer:
            self.programmer.timer.stop()
            del self.programmer

    def skip_program_segment(self):
        if self.programmer:
            self.programmer.current_segment += 1
            self.programmer.start_ramp()

    def start_logging(self):
        self.is_logging = True
        self.log_start_time = datetime.now() if not self.log_start_time else self.log_start_time

    def clear_log(self):
        self.is_logging = False
        self.log_start_time = None
        self.data = {'Sensor PV': [], 'Controller PV': [], 'Setpoint': [], 'Power': []}

    def export_log(self, filepath):
        """
        Tedious data aligning: The timestamps of the 4 separate data series (time -> value) are rounded to whole seconds
        and transferred into one dict (time -> 4 values), to align the 4 data series. This dict is then used to generate
         a csv file.
        """

        def _work():
            sorted_data = {}
            for parameter, series in self.data.items():
                for time, value in series:
                    timestamp = int(time.timestamp())
                    if timestamp not in sorted_data.keys():
                        sorted_data[timestamp] = {parameter: value}
                    else:
                        sorted_data[timestamp].update({parameter: value})

            unit = self.units[self.mode]

            with open(filepath, 'w+') as file:
                file.write('UTC, Unix timestamp (s), Process Variable ({:s}), Output Power (%), Sensor Value ({:s})\n'.
                           format(unit, unit))
                for timestamp, datapoint in sorted_data.items():
                    timestring = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
                    power = datapoint['Power'] if 'Power' in datapoint.keys() else math.nan
                    controller_pv = datapoint['Controller PV'] if 'Controller PV' in datapoint.keys() else math.nan
                    sensor_pv = datapoint['Sensor PV'] if 'Sensor PV' in datapoint.keys() else math.nan
                    file.write('{:s}, {:d}, {:.1f}, {:.1f}, {:.1f}\n'.
                               format(timestring, timestamp, controller_pv, power, sensor_pv))

        worker = Worker(_work)
        self.pool.start(worker)

    def add_log_data_point(self, data):
        for parameter, value in data.items():
            self.data[parameter].append((datetime.now(), value))
