import time
import threading
import serial.tools.list_ports
from datetime import datetime
from threading import Timer
import functools

import pubsub.pub
from PySide2.QtCore import QThreadPool
from pubsub.pub import sendMessage, subscribe, unsubscribe
from serial import SerialException

from Drivers.AbstractSensorController import AbstractController, AbstractSensor
from Drivers.ElchWorks import Thermolino, Thermoplatino
from Drivers.Eurotherms import Eurotherm3216, Eurotherm3508, Eurotherm2408, Eurotherm3508S
from Drivers.Keithly import Keithly2000Temp, Keithly2000Volt
from Drivers.Omega import OmegaPt
from Drivers.Pyrometer import Pyrometer
from Drivers.TestDevices import TestSensor, TestController
from Engine.ThreadDecorators import in_new_thread, Worker, WorkThread

# TODO: Implement some notification system for serial failures and not implemented functions
TEST_MODE = True


class HeaterControlEngine:
    def __init__(self):
        self.available_ports = {port[1]: port[0] for port in serial.tools.list_ports.comports()}
        self.controller_types = {'Eurotherm2408': Eurotherm2408, 'Eurotherm3216': Eurotherm3216,
                                 'Eurotherm3508': Eurotherm3508, 'Omega Pt': OmegaPt, 'Test Controller': TestController}
        self.sensor_types = {'Pyrometer': Pyrometer, 'Thermolino': Thermolino, 'Thermoplatino': Thermoplatino,
                             'Keithly2000 Temperature': Keithly2000Temp, 'Keithly2000 Voltage': Keithly2000Volt,
                             'Eurotherm3508': Eurotherm3508S}

        self.controller_functions = {'gui.request.status': (self.get_controller_status, True),
                                     'gui.con.disconnect_controller': (self.remove_controller, True),
                                     'gui.con.connect_controller': (self.add_controller, False),
                                     'gui.set.power': (self.set_manual_output_power, True),
                                     'gui.set.setpoint': (self.set_target_setpoint, True),
                                     'gui.set.rate': (self.set_rate, True),
                                     'gui.set.control_mode': (self.set_control_mode, True)}
        self.sensor_functions = {'gui.request.status': (self.get_sensor_status, True),
                                 'gui.con.disconnect_sensor': (self.remove_sensor, True),
                                 'gui.con.connect_sensor': (self.add_sensor, False)}

        if TEST_MODE:
            self.sensor_types['Test Sensor'] = TestSensor
            self.controller_types['Test Controller'] = TestController
            self.available_ports['COM Test'] = 'Test Port'

        self.sensor = AbstractSensor()
        self.controller = AbstractController()
        self.controller_slave_address = 1

        self.is_logging = False
        self.status_values = {'Sensor PV': [], 'Controller PV': [], 'Setpoint': [], 'Power': []}

        subscribe(self.add_controller, 'gui.con.connect_controller')
        subscribe(self.add_sensor, 'gui.con.connect_sensor')
        self.broadcast_available_devices()
        self.pool = QThreadPool()

    def broadcast_available_devices(self):
        pubsub.pub.sendMessage(topicName='engine.broadcast.devices', ports=self.available_ports,
                               devices={'Controller': self.controller_types.keys(), 'Sensor': self.sensor_types.keys()})

    def add_controller(self, controller_type, controller_port):
        try:
            self.controller = self.controller_types[controller_type](portname=self.available_ports[controller_port],
                                                                     slaveadress=self.controller_slave_address)

            self.get_controller_parameters()
            for topic, function in self.controller_functions.items():
                if function[1]:
                    pubsub.pub.subscribe(function[0], topic)
                else:
                    pubsub.pub.unsubscribe(function[0], topic)

        except SerialException:
            sendMessage(topicName='engine.status', text='Connection error!')

    def remove_controller(self):
        self.controller = None
        for topic, function in self.controller_functions.items():
            if not function[1]:
                pubsub.pub.subscribe(function[0], topic)
            else:
                pubsub.pub.unsubscribe(function[0], topic)

    def add_sensor(self, sensor_type, sensor_port):
        try:
            self.sensor = self.sensor_types[sensor_type](port=self.available_ports[sensor_port])
            for topic, function in self.sensor_functions.items():
                if function[1]:
                    pubsub.pub.subscribe(function[0], topic)
                else:
                    pubsub.pub.unsubscribe(function[0], topic)
        except SerialException:
            sendMessage(topicName='engine.status', text='Connection error!')

    def remove_sensor(self):
        for topic, function in self.sensor_functions.items():
            if not function[1]:
                pubsub.pub.subscribe(function[0], topic)
            else:
                pubsub.pub.unsubscribe(function[0], topic)
        self.sensor.close()

    def get_sensor_status(self):
        worker = Worker(self.sensor.get_sensor_value)
        worker.signals.over.connect(lambda val: sendMessage('engine.answer.status', status_values={'Sensor PV': val}))
        self.pool.start(worker)

    def get_controller_status(self):
        for parameter, function in {'Controller PV': self.controller.get_process_variable,
                                    'Setpoint': self.controller.get_working_setpoint,
                                    'Power': self.controller.get_working_output}.items():
            worker = Worker(function)
            worker.signals.over.connect(lambda val, par=parameter: sendMessage('engine.answer.status',
                                                                               status_values={par: val}))
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

    # TODO: Implement PID functionality properly

    @in_new_thread
    def set_pid_p(self, p):
        try:
            self.controller.set_pid_p(p)
            sendMessage(topicName='engine.status', text='PID P set to {:f}'.format(p))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_p2(self, p):
        try:
            self.controller.set_pid_p2(p)
            sendMessage(topicName='engine.status', text='PID P2 set to {:f}'.format(p))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_p3(self, p):
        try:
            self.controller.set_pid_p3(p)
            sendMessage(topicName='engine.status', text='PID P3 set to {:f}'.format(p))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_i(self, i):
        try:
            self.controller.set_pid_i(i)
            sendMessage(topicName='engine.status', text='PID I set to {:f}'.format(i))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_i2(self, i):
        try:
            self.controller.set_pid_i2(i)
            sendMessage(topicName='engine.status', text='PID I2 set to {:f}'.format(i))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_i3(self, i):
        try:
            self.controller.set_pid_i3(i)
            sendMessage(topicName='engine.status', text='PID I3 set to {:f}'.format(i))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_d(self, d):
        try:
            self.controller.set_pid_d(d)
            sendMessage(topicName='engine.status', text='PID D set to {:f}'.format(d))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_d2(self, d):
        try:
            self.controller.set_pid_d2(d)
            sendMessage(topicName='engine.status', text='PID D2 set to {:f}'.format(d))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_d3(self, d):
        try:
            self.controller.set_pid_d3(d)
            sendMessage(topicName='engine.status', text='PID D3 set to {:f}'.format(d))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_boundary12(self, boundary):
        try:
            self.controller.set_boundary_12(boundary)
            sendMessage(topicName='engine.status', text='Boundary 1/2 set to {:f}'.format(boundary))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_boundary23(self, boundary):
        try:
            self.controller.set_boundary_23(boundary)
            sendMessage(topicName='engine.status', text='Boundary 2/3 set to {:f}'.format(boundary))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_gain_scheduling(self, mode):
        try:
            self.controller.set_gain_scheduling(mode)
            sendMessage(topicName='engine.status', text='Gain scheduling mode set to {:s}'.format(mode))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_pid_parameter(self, parameteter, value):
        pass

    @in_new_thread
    def get_pid_parameters(self):
        try:
            pid_parameters = {'P': self.controller.get_pid_p(), 'P2': self.controller.get_pid_p2(),
                              'P3': self.controller.get_pid_p3(), 'I': self.controller.get_pid_i(),
                              'I2': self.controller.get_pid_i2(), 'I3': self.controller.get_pid_i3(),
                              'D': self.controller.get_pid_d(), 'D2': self.controller.get_pid_d2(),
                              'D3': self.controller.get_pid_d3(), 'B23': self.controller.get_boundary_23(),
                              'B12': self.controller.get_boundary_12(), 'GS': self.controller.get_gain_scheduling()}

            sendMessage(topicName='engine.answer.pid', pid_parameters=pid_parameters)
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')


class Datalogger:
    def __init__(self, master):
        self.master = master

        self.logfile_path = 'Default.txt'
        self.is_logging = False

        subscribe(self.start_log, 'gui.log.start')
        subscribe(self.stop_log, 'gui.log.stop')
        subscribe(self.continue_log, 'gui.log.cont')
        subscribe(self.set_logfile, 'gui.log.filename')

    def write_log(self):
        abs_time = datetime.now()
        time_string = abs_time.strftime('%d.%m.%Y - %H:%M:%S')
        unix_time = int(time.time())
        with open(self.logfile_path, 'a') as logfile:
            logfile.write('{:s}\t{:d}\t{:5.1f}\t{:5.1f}\t{:5.2f}\n'.format(time_string, unix_time,
                                                                           self.master.controller_process_value,
                                                                           self.master.controller_working_output,
                                                                           self.master.sensor_value))
        if self.is_logging:
            log_timer = Timer(interval=1, function=self.write_log)
            log_timer.start()

    def set_logfile(self, filename):
        self.logfile_path = filename

    def start_log(self):
        if not self.is_logging:
            self.is_logging = True
            with open(self.logfile_path, 'a') as logfile:
                logfile.write('Time\tUnixtime\tProcess Variable\tOutput Power (%)\tSensor Value\n')
            log_timer = Timer(interval=1, function=self.write_log)
            log_timer.start()

    def stop_log(self):
        self.is_logging = False

    def continue_log(self):
        self.is_logging = True
        self.write_log()
