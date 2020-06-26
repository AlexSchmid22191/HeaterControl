from datetime import datetime
from threading import Lock
from threading import Timer
from time import sleep
from time import time
from serial import SerialException, SerialTimeoutException
from pubsub.pub import sendMessage, subscribe, unsubscribe

from Drivers.Eurotherms import Eurotherm3216
from Drivers.Pyrometer import Pyrometer
from Drivers.Thermolino import Thermolino
from Drivers.Thermoplatino import Thermoplatino
from Drivers.Keithly import Keithly
from Drivers.OmegaPt import OmegaPt

from ThreadDecorators import in_new_thread


class HeaterControlEngine:
    def __init__(self):

        # To prevent multiple devices writing to the same variable
        self.com_lock = Lock()

        self.heater_types = {'Eurotherm3216': Eurotherm3216, 'Eurotherm3200': Eurotherm3216,
                             'Eurotherm3210': Eurotherm3216, 'Omega Pt': OmegaPt}
        self.sensor_types = {'Pyrometer': Pyrometer, 'Thermolino': Thermolino, 'Thermoplatino': Thermoplatino,
                             'Keithly 2000': Keithly}

        self.sensor = None
        self.sensor_port = None

        self.heater = None
        self.heater_port = None
        self.heater_slave_adress = 1

        self.sensor_temperature = 0

        self.heater_temperature = 0
        self.heater_working_output = 0
        self.heater_working_setpoint = 0

        self.heater_mode = 'manual'
        self.heater_tagert_temp = 0
        self.heater_rate = 15
        self.heater_power = 0

        self.datalogger = Datalogger(master=self)

        subscribe(self.add_heater, 'gui.con.connect_heater')
        subscribe(self.add_sensor, 'gui.con.connect_sensor')

        subscribe(self.remove_heater, 'gui.con.disconnect_heater')
        subscribe(self.remove_sensor, 'gui.con.disconnect_sensor')

    def set_heater_port(self, port):
        self.sensor_port = port

    def set_sensor_port(self, port):
        self.sensor_port = port

    def set_heater_slave_adress(self, adress):
        self.heater_slave_adress = adress

    def add_heater(self, heater_type, heater_port):
        self.heater = self.heater_types[heater_type](portname=heater_port, slaveadress=self.heater_slave_adress)
        self.heater.set_manual_mode()
        subscribe(self.get_oven_temp, 'gui.request.oven_temp')
        subscribe(self.get_working_output, 'gui.request.working_output')
        subscribe(self.get_working_setpoint, 'gui.request.working_setpoint')

        subscribe(self.set_automatic_mode, 'gui.set.automatic_mode')
        subscribe(self.set_manual_mode, 'gui.set.manual_mode')
        subscribe(self.set_target_setpoint, 'gui.set.target_setpoint')
        subscribe(self.set_manual_output_power, 'gui.set.manual_power')
        subscribe(self.set_rate, 'gui.set.rate')
        subscribe(self.set_pid_p, 'gui.set.pid_p')
        subscribe(self.set_pid_i, 'gui.set.pid_i')
        subscribe(self.set_pid_d, 'gui.set.pid_d')

    def remove_heater(self):
        unsubscribe(self.get_oven_temp, 'gui.request.oven_temp')
        unsubscribe(self.get_working_output, 'gui.request.working_output')
        unsubscribe(self.get_working_setpoint, 'gui.request.working_setpoint')

        unsubscribe(self.set_automatic_mode, 'gui.set.automatic_mode')
        unsubscribe(self.set_manual_mode, 'gui.set.manual_mode')
        unsubscribe(self.set_target_setpoint, 'gui.set.target_setpoint')
        unsubscribe(self.set_manual_output_power, 'gui.set.manual_power')
        unsubscribe(self.set_rate, 'gui.set.rate')
        unsubscribe(self.set_pid_p, 'gui.set.pid_p')
        unsubscribe(self.set_pid_i, 'gui.set.pid_i')
        unsubscribe(self.set_pid_d, 'gui.set.pid_d')
        
        self.heater = None

    def add_sensor(self, sensor_type, sensor_port):
        self.sensor = self.sensor_types[sensor_type](port=sensor_port)
        sleep(2)
        subscribe(self.get_sensor_temp, 'gui.request.sensor_temp')

    def remove_sensor(self):
        self.sensor.close()
        unsubscribe(self.get_sensor_temp, 'gui.request.sensor_temp')

    @in_new_thread
    def get_oven_temp(self):
        with self.com_lock:
            self.heater_temperature = self.heater.get_oven_temp()
            sendMessage(topicName='engine.answer.oven_temp', temp=self.heater_temperature)

    @in_new_thread
    def get_working_output(self):
        with self.com_lock:
            self.heater_working_output = self.heater.get_working_output()
            sendMessage(topicName='engine.answer.oven_working_output', output=self.heater_working_output)

    @in_new_thread
    def get_working_setpoint(self):
        with self.com_lock:
            self.heater_working_setpoint = self.heater.get_working_setpoint()
            sendMessage(topicName='engine.answer.oven_working_setpoint', setpoint=self.heater_working_setpoint)

    @in_new_thread
    def set_automatic_mode(self):
        with self.com_lock:
            self.heater.set_automatic_mode()
            sendMessage(topicName='engine.status', text='Heater set to automatic mode!')

    @in_new_thread
    def set_manual_mode(self):
        with self.com_lock:
            self.heater.set_manual_mode()
            sendMessage(topicName='engine.status', text='Heater set to manual mode!')

    @in_new_thread
    def set_target_setpoint(self, temp):
        with self.com_lock:
            self.heater.set_target_setpoint(temp)
            sendMessage(topicName='engine.status', text='Heater setpoint set to {:5.1f} °C!'.format(temp))

    @in_new_thread
    def set_manual_output_power(self, power):
        with self.com_lock:
            self.heater.set_manual_output_power(power)
            sendMessage(topicName='engine.status', text='Heater power set to {:5.1f} %!'.format(power))

    @in_new_thread
    def set_rate(self, rate):
        with self.com_lock:
            self.heater.set_rate(rate)
            sendMessage(topicName='engine.status', text='Heater rate set to {:5.1f} °C/min!'.format(rate))

    @in_new_thread
    def get_sensor_temp(self):
        try:
            self.sensor_temperature = self.sensor.read_temperature()
            sendMessage(topicName='engine.answer.sensor_temp', temp=self.sensor_temperature)
        except (ValueError, SerialException, SerialTimeoutException):
            sendMessage(topicName='engine.status', text='Sensor error!')

    @in_new_thread
    def set_pid_p(self, p):
        with self.com_lock:
            self.heater.set_pid_p(p)

    @in_new_thread
    def set_pid_i(self, i):
        with self.com_lock:
            self.heater.set_pid_p(i)

    @in_new_thread
    def set_pid_d(self, d):
        with self.com_lock:
            self.heater.set_pid_p(d)


class Datalogger:
    def __init__(self, master):
        self.master = master

        self.logfile_path = 'Default.txt'
        self.is_logging = False

        subscribe(self.start_log, 'gui.log.start')
        subscribe(self.stop_log, 'gui.log.stop')
        subscribe(self.continue_log, 'gui.log.continue')
        subscribe(self.set_logfile, 'gui.log.filename')

    def write_log(self):
        abs_time = datetime.now()
        timestring = abs_time.strftime('%d.%m.%Y - %H:%M:%S')
        unixtime = int(time())

        with open(self.logfile_path, 'a') as logfile:
            logfile.write('{:s}\t{:d}\t{:5.1f}\t{:5.1f}\t{:5.2f}\n'.format(timestring, unixtime,
                                                                         self.master.heater_temperature,
                                                                         self.master.heater_working_output,
                                                                         self.master.sensor_temperature))

        if self.is_logging:
            log_timer = Timer(interval=1, function=self.write_log)
            log_timer.start()

    def set_logfile(self, filename):
        self.logfile_path = filename

    def start_log(self):
        if not self.is_logging:
            self.is_logging = True
            with open(self.logfile_path, 'a') as logfile:
                logfile.write('Time\tUnixtime\tHeater Temperature (°C)\tHeater Power (%)\tSensor Temperature (°C)\n')

            log_timer = Timer(interval=1, function=self.write_log)
            log_timer.start()

    def stop_log(self):
        self.is_logging = False

    def continue_log(self):
        self.is_logging = True
        self.write_log()


if __name__ == '__main__':
    a = HeaterControlEngine()
    a.datalogger.start_log()
