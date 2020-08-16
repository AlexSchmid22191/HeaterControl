from datetime import datetime
from threading import Timer
import time
import pubsub.pub
from serial import SerialException, SerialTimeoutException
from pubsub.pub import sendMessage, subscribe, unsubscribe

from Drivers.AbstractSensorController import AbstractController, AbstractSensor
from Drivers.TestDevices import TestSensor, TestController
from Drivers.Eurotherms import Eurotherm3216, Eurotherm3508, Eurotherm2408, Eurotherm3508S
from Drivers.ElchWorks import Thermolino, Thermoplatino
from Drivers.Keithly import Keithly2000Temp, Keithly2000Volt
from Drivers.Pyrometer import Pyrometer
from Drivers.Omega import OmegaPt

from ThreadDecorators import in_new_thread, in_qthread, OtherThread


class HeaterControlEngine:
    def __init__(self):
        self.controller_types = {'Eurotherm2408': Eurotherm2408, 'Eurotherm3216': Eurotherm3216,
                                 'Eurotherm3508': Eurotherm3508, 'Omega Pt': OmegaPt, 'Test Controller': TestController}

        self.sensor_types = { 'Test Sensor': TestSensor, 'Pyrometer': Pyrometer, 'Thermolino': Thermolino, 'Thermoplatino': Thermoplatino,
                             'Keithly2000 Temperature': Keithly2000Temp, 'Keithly2000 Voltage': Keithly2000Volt,
                             'Eurotherm3508': Eurotherm3508S,}

        self.available_ports = ['COM Test']

        self.sensor = AbstractSensor()
        self.sensor_port = None
        self.controller = AbstractController()
        self.controller_port = None
        self.controller_slave_address = 1

        self.status_values = {'Sensor PV': None, 'Controller PV': None, 'Setpoint': None, 'Power': None}

        self.is_logging = False

        subscribe(self.add_controller, 'gui.con.connect_controller')
        subscribe(self.add_sensor, 'gui.con.connect_sensor')

        self.broadcast_available_devices()

    def broadcast_available_devices(self):
        pubsub.pub.sendMessage(topicName='engine.broadcast.devices', ports=self.available_ports,
                               devices={'Controller': self.controller_types.keys(), 'Sensor': self.sensor_types.keys()})

    def add_controller(self, controller_type, controller_port):
        try:
            self.controller = self.controller_types[controller_type](portname=controller_port,
                                                                     slaveadress=self.controller_slave_address)

            unsubscribe(self.add_controller, 'gui.con.connect_controller')
            subscribe(self.remove_heater, 'gui.con.disconnect_controller')

            subscribe(self.set_target_setpoint, 'gui.set.target_setpoint')
            subscribe(self.set_manual_output_power, 'gui.set.manual_power')
            subscribe(self.set_rate, 'gui.set.rate')
            subscribe(self.set_pid_p, 'gui.set.pid_p')
            subscribe(self.set_pid_p2, 'gui.set.pid_p2')
            subscribe(self.set_pid_p3, 'gui.set.pid_p3')
            subscribe(self.set_pid_i, 'gui.set.pid_i')
            subscribe(self.set_pid_i2, 'gui.set.pid_i2')
            subscribe(self.set_pid_i3, 'gui.set.pid_i3')
            subscribe(self.set_pid_d, 'gui.set.pid_d')
            subscribe(self.set_pid_d2, 'gui.set.pid_d2')
            subscribe(self.set_pid_d3, 'gui.set.pid_d3')
            subscribe(self.set_boundary12, 'gui.set.boundary12')
            subscribe(self.set_boundary23, 'gui.set.boundary23')
            subscribe(self.set_gain_scheduling, 'gui.set.gs_mode')
            subscribe(self.get_pid_parameters, 'gui.request.pid')

        except SerialException:
            sendMessage(topicName='engine.status', text='Connection error!')

    def remove_heater(self):

        subscribe(self.add_controller, 'gui.con.connect_controller')
        unsubscribe(self.remove_heater, 'gui.con.disconnect_controller')
        unsubscribe(self.set_target_setpoint, 'gui.set.target_setpoint')
        unsubscribe(self.set_manual_output_power, 'gui.set.manual_power')
        unsubscribe(self.set_rate, 'gui.set.rate')
        unsubscribe(self.set_pid_p, 'gui.set.pid_p')
        unsubscribe(self.set_pid_p2, 'gui.set.pid_p2')
        unsubscribe(self.set_pid_p3, 'gui.set.pid_p3')
        unsubscribe(self.set_pid_i, 'gui.set.pid_i')
        unsubscribe(self.set_pid_i2, 'gui.set.pid_i2')
        unsubscribe(self.set_pid_i3, 'gui.set.pid_i3')
        unsubscribe(self.set_pid_d, 'gui.set.pid_d')
        unsubscribe(self.set_pid_d2, 'gui.set.pid_d2')
        unsubscribe(self.set_pid_d3, 'gui.set.pid_d3')
        unsubscribe(self.set_boundary12, 'gui.set.boundary12')
        unsubscribe(self.set_boundary23, 'gui.set.boundary23')
        unsubscribe(self.set_gain_scheduling, 'gui.set.gs_mode')
        unsubscribe(self.get_pid_parameters, 'gui.request.pid')

        self.controller = None

    def add_sensor(self, sensor_type, sensor_port):
        try:
            self.sensor = self.sensor_types[sensor_type](port=sensor_port)
        except SerialException:
            sendMessage(topicName='engine.status', text='Connection error!')

        self.get_sensor_status()

        subscribe(self.remove_sensor, 'gui.con.disconnect_sensor')
        unsubscribe(self.add_sensor, 'gui.con.connect_sensor')

    def remove_sensor(self):
        self.sensor.close()
        unsubscribe(self.remove_sensor, 'gui.con.disconnect_sensor')
        subscribe(self.add_sensor, 'gui.con.connect_sensor')

    def broadcast_status_values(self):
        pubsub.pub.sendMessage(topicName='engine.broadcast.status', status=self.status_values)

    @in_new_thread
    def get_controller_status(self):
        try:
            self.status_values['Controller PV'] = self.controller.get_process_variable()
            self.status_values['Setpoint'] = self.controller.get_working_setpoint()
            self.status_values['Power'] = self.controller.get_working_output()
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    def get_sensor_status(self):
        self.thread = OtherThread(self.sensor.get_sensor_value)
        self.thread.start()
        self.thread.over.connect(lambda res: sendMessage(topicName='engine.spam', sens=res))


    @in_new_thread
    def set_control_mode(self, mode):
        try:
            self.controller.set_manual_mode() if mode == 'Manual' else self.controller.set_automatic_mode()
            sendMessage(topicName='engine.status', text='Heater set to {:s} mode!'.format(mode.lower()))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_target_setpoint(self, setpoint):
        try:
            self.controller.set_target_setpoint(setpoint)
            sendMessage(topicName='engine.status', text='Heater setpoint set to {:5.1f}!'.format(setpoint))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_manual_output_power(self, power):
        try:
            self.controller.set_manual_output_power(power)
            sendMessage(topicName='engine.status', text='Heater power set to {:5.1f} %!'.format(power))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

    @in_new_thread
    def set_rate(self, rate):
        try:
            self.controller.set_rate(rate)
            sendMessage(topicName='engine.status', text='Heater rate set to {:5.1f}!'.format(rate))
        except NotImplementedError as exception:
            print(exception)
        except SerialException:
            sendMessage(topicName='engine.status', text='Serial communication error!')

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
