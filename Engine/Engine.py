import datetime
import math

import pubsub.pub
import serial.tools.list_ports
from PySide2.QtCore import QThreadPool
from pubsub.pub import sendMessage
from serial import SerialException

from Drivers.AbstractSensorController import AbstractController, AbstractSensor
from Drivers.ElchWorks import Thermolino, Thermoplatino, ElchLaser
from Drivers.Eurotherms import Eurotherm3216, Eurotherm3508, Eurotherm2408, Eurotherm3508S
from Drivers.ResistiveHeater import CeramicSputterHeater
from Drivers.Jumo import JumoQuantol
from Drivers.Keithly import Keithly2000Temp, Keithly2000Volt
from Drivers.Omega import OmegaPt
from Drivers.Pyrometer import Pyrometer
from Drivers.TestDevices import TestSensor, TestController, NiceTestController
from Engine.ThreadDecorators import Worker
from Engine.SetProg import SetpointProgrammer

from Signals import engine_signals, gui_signals

TEST_MODE = False


class HeaterControlEngine:
    def __init__(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}
        self.controller_types = {'Eurotherm2408': Eurotherm2408, 'Eurotherm3216': Eurotherm3216,
                                 'Eurotherm3508': Eurotherm3508, 'Omega Pt': OmegaPt, 'Jumo Quantrol': JumoQuantol,
                                 'Elch Laser Control': ElchLaser, 'Elch Heater Controller': ElchLaser,
                                 'CSH (Experimental)': CeramicSputterHeater}
        self.sensor_types = {'Pyrometer': Pyrometer, 'Thermolino': Thermolino, 'Thermoplatino': Thermoplatino,
                             'Keithly2000 Temperature': Keithly2000Temp, 'Keithly2000 Voltage': Keithly2000Volt,
                             'Eurotherm3508': Eurotherm3508S}

        self.controller_functions = {'gui.request.status': (self.get_controller_status, True),
                                     'gui.request.control_parameters': (self.get_controller_parameters, True),
                                     'gui.request.pid_parameters': (self.get_pid_parameters, True),
                                     'gui.con.disconnect_controller': (self.remove_controller, True),
                                     'gui.con.connect_controller': (self.add_controller, False),
                                     'gui.set.power': (self.set_manual_output_power, True),
                                     'gui.set.setpoint': (self.set_target_setpoint, True),
                                     'gui.set.rate': (self.set_rate, True),
                                     'gui.set.control_mode': (self.set_control_mode, True),
                                     'gui.set.pid_parameters': (self.set_pid_parameters, True),
                                     'gui.set.start_program': (self.start_programmer, True)}
        self.sensor_functions = {'gui.request.status': (self.get_sensor_status, True),
                                 'gui.con.disconnect_sensor': (self.remove_sensor, True),
                                 'gui.con.connect_sensor': (self.add_sensor, False)}

        if TEST_MODE:
            self.sensor_types['Test Sensor'] = TestSensor
            self.controller_types['Test Controller'] = TestController
            self.controller_types['Nice Test Controller'] = NiceTestController
            self.available_ports['COM Test'] = 'Test Port'

        self.sensor = AbstractSensor()
        self.controller = AbstractController()
        self.controller_slave_address = 1

        self.is_logging = False
        self.log_start_time = None
        self.data = {'Sensor PV': [], 'Controller PV': [], 'Setpoint': [], 'Power': []}

        self.mode = 'Temperature'
        self.units = {'Temperature': '°C', 'Voltage': 'mV'}

        self.programmer = None

        pubsub.pub.subscribe(self.refresh_available_ports, 'gui.request.ports')
        pubsub.pub.subscribe(self.set_units, 'gui.set.units')
        pubsub.pub.subscribe(self.add_controller, 'gui.con.connect_controller')
        pubsub.pub.subscribe(self.add_sensor, 'gui.con.connect_sensor')
        pubsub.pub.subscribe(self.start_logging, 'gui.plot.start')
        pubsub.pub.subscribe(self.clear_log, 'gui.plot.clear')
        pubsub.pub.subscribe(self.export_log, 'gui.plot.export')

        self.pool = QThreadPool()

    def set_units(self, unit):
        self.mode = unit
        devices = {'Controller': [key for key, controller in self.controller_types.items() if controller.mode == unit],
                   'Sensor': [key for key, sensor in self.sensor_types.items() if sensor.mode == unit]}
        pubsub.pub.sendMessage(topicName='engine.answer.devices', devices=devices)

    def refresh_available_ports(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}
        if TEST_MODE:
            self.available_ports['COM Test'] = 'Test Port'
        pubsub.pub.sendMessage(topicName='engine.answer.ports', ports=self.available_ports)

    def add_controller(self, controller_type, controller_port):
        try:
            self.controller = self.controller_types[controller_type](portname=controller_port,
                                                                     slaveadress=self.controller_slave_address)

            self.get_controller_parameters()
            self.get_pid_parameters()
            gui_signals.enable_output.connect(self.toggle_output_enable)
            gui_signals.toggle_aiming.connect(self.toggle_aiming_beam)
            for topic, function in self.controller_functions.items():
                if function[1]:
                    pubsub.pub.subscribe(function[0], topic)
                else:
                    pubsub.pub.unsubscribe(function[0], topic)

            engine_signals.controller_connected.emit(controller_type, controller_port)

        except SerialException:
            sendMessage(topicName='engine.status', text='Connection error!')
            engine_signals.connection_failed.emit()

    def remove_controller(self):
        self.controller = None
        for topic, function in self.controller_functions.items():
            if not function[1]:
                pubsub.pub.subscribe(function[0], topic)
            else:
                pubsub.pub.unsubscribe(function[0], topic)
        self.sensor = AbstractSensor()
        engine_signals.controller_disconnected.emit()

    def toggle_output_enable(self, state):
        if state:
            self.controller.enable_output()
        else:
            self.controller.disable_output()

    def toggle_aiming_beam(self, state):
        if state:
            self.controller.enable_aiming_beam()
        else:
            self.controller.disable_aiming_beam()

    def add_sensor(self, sensor_type, sensor_port):
        try:
            self.sensor = self.sensor_types[sensor_type](port=sensor_port)
            for topic, function in self.sensor_functions.items():
                if function[1]:
                    pubsub.pub.subscribe(function[0], topic)
                else:
                    pubsub.pub.unsubscribe(function[0], topic)
            engine_signals.sensor_connected.emit(sensor_type, sensor_port)
        except SerialException:
            sendMessage(topicName='engine.status', text='Connection error!')
            engine_signals.connection_failed.emit()

    def remove_sensor(self):
        for topic, function in self.sensor_functions.items():
            if not function[1]:
                pubsub.pub.subscribe(function[0], topic)
            else:
                pubsub.pub.unsubscribe(function[0], topic)
        self.sensor.close()
        self.sensor = AbstractSensor()
        engine_signals.sensor_disconnected.emit()

    def get_sensor_status(self):
        runtime = (datetime.datetime.now() - self.log_start_time).total_seconds() if self.log_start_time else None
        worker = Worker(self.sensor.get_sensor_value)
        worker.signals.over.connect(lambda val: sendMessage('engine.answer.status',
                                                            status_values={'Sensor PV': (val, runtime)}))
        if self.is_logging:
            worker.signals.over.connect(lambda val, par='Sensor PV': self.add_log_data_point(data={par: val}))
        self.pool.start(worker)

    def get_controller_status(self):
        runtime = (datetime.datetime.now() - self.log_start_time).total_seconds() if self.log_start_time else None
        for parameter, function in {'Controller PV': self.controller.get_process_variable,
                                    'Setpoint': self.controller.get_working_setpoint,
                                    'Power': self.controller.get_working_output}.items():

            worker = Worker(function)
            worker.signals.over.connect(lambda val, par=parameter: sendMessage('engine.answer.status', status_values={
                par: (val, runtime)}))
            if self.is_logging:
                worker.signals.over.connect(lambda val, par=parameter: self.add_log_data_point(data={par: val}))
            self.pool.start(worker)

    def set_control_mode(self, mode):
        function = self.controller.set_manual_mode if mode == 'Manual' else self.controller.set_automatic_mode
        worker = Worker(function)
        self.pool.start(worker)

    def set_target_setpoint(self, setpoint):
        worker = Worker(lambda setp=setpoint: self.controller.set_target_setpoint(setp))
        self.pool.start(worker)

    def set_manual_output_power(self, power):
        worker = Worker(lambda powr=power: self.controller.set_manual_output_power(powr))
        self.pool.start(worker)

    def set_rate(self, rate):
        worker = Worker(lambda rat=rate: self.controller.set_rate(rat))
        self.pool.start(worker)

    def get_controller_parameters(self):
        for parameter, function in {'Setpoint': self.controller.get_target_setpoint,
                                    'Power': self.controller.get_working_output,
                                    'Rate': self.controller.get_rate,
                                    'Mode': self.controller.get_control_mode}.items():
            worker = Worker(function)
            worker.signals.over.connect(lambda val, par=parameter: sendMessage('engine.answer.control_parameters',
                                                                               control_parameters={par: val}))
            self.pool.start(worker)

    def start_logging(self):
        self.is_logging = True
        self.log_start_time = datetime.datetime.now() if not self.log_start_time else self.log_start_time

    def clear_log(self):
        self.is_logging = False
        self.log_start_time = None
        self.data = {'Sensor PV': [], 'Controller PV': [], 'Setpoint': [], 'Power': []}

    def export_log(self, filepath):
        """
        Tedious data aligning: The timestamps separate data series (time -> value) are rounded to whole seconds and
        transfered into one dict (time -> 4values), to align the 4 data series. This dict is the used to generate a
        csv file.
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
                    timestring = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
                    power = datapoint['Power'] if 'Power' in datapoint.keys() else math.nan
                    controller_pv = datapoint['Controller PV'] if 'Controller PV' in datapoint.keys() else math.nan
                    sensor_pv = datapoint['Sensor PV'] if 'Sensor PV' in datapoint.keys() else math.nan
                    file.write('{:s}, {:d}, {:.1f}, {:.1f}, {:.1f}\n'.
                               format(timestring, timestamp, controller_pv, power, sensor_pv))

        worker = Worker(_work)
        self.pool.start(worker)

    def add_log_data_point(self, data):
        for parameter, value in data.items():
            self.data[parameter].append((datetime.datetime.now(), value))

    def get_pid_parameters(self):
        for parameter, function in {'P1': self.controller.get_pid_p, 'P2': self.controller.get_pid_p2,
                                    'P3': self.controller.get_pid_p3, 'I1': self.controller.get_pid_i,
                                    'I2': self.controller.get_pid_i2, 'I3': self.controller.get_pid_i3,
                                    'D1': self.controller.get_pid_d, 'D2': self.controller.get_pid_d2,
                                    'D3': self.controller.get_pid_d3, 'B23': self.controller.get_boundary_23,
                                    'B12': self.controller.get_boundary_12, 'AS': self.controller.get_active_set,
                                    'GS': self.controller.get_gain_scheduling}.items():
            worker = Worker(function)
            worker.signals.over.connect(lambda val, par=parameter: sendMessage('engine.answer.pid_parameters',
                                                                               pid_parameters={par: val}))
            self.pool.start(worker)

    def set_pid_parameters(self, parameter, value):
        function = {'P1': self.controller.set_pid_p, 'P2': self.controller.set_pid_p2, 'P3': self.controller.set_pid_p3,
                    'I1': self.controller.set_pid_i, 'I2': self.controller.set_pid_i2, 'I3': self.controller.set_pid_i3,
                    'D1': self.controller.set_pid_d, 'D2': self.controller.set_pid_d2, 'D3': self.controller.set_pid_d3,
                    'B23': self.controller.set_boundary_23, 'B12': self.controller.set_boundary_12,
                    'GS': self.controller.set_gain_scheduling, 'AS': self.controller.set_active_set}[parameter]

        worker = Worker(lambda val=value: function(val))
        self.pool.start(worker)

    def start_programmer(self, program):
        if self.programmer:
            self.programmer.timer.stop()
        self.programmer = SetpointProgrammer(program, self)
        pubsub.pub.subscribe(self.stop_programmer, 'gui.set.stop_program')
        pubsub.pub.subscribe(self.skip_program_segment, 'gui.set.skip_program')

    def stop_programmer(self):
        if self.programmer:
            self.programmer.timer.stop()
            self.programmer = None

    def skip_program_segment(self):
        if self.programmer:
            self.programmer.current_segment += 1
            self.programmer.start_ramp()
