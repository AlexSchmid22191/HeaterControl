import random
import threading
import time

import serial

from src.Drivers.BaseClasses import AbstractController, AbstractSensor, ControllerFeatures, SensorFeatures, UnitType


class TestSensor(AbstractSensor):
    """Mock Sensor to test engine to GUI connection"""
    type = UnitType.TEMPERATURE

    def __init__(self, *args, **kwargs):
        print('Test Sensor connected!')
        self.com_lock = threading.Lock()
        print(f'Called with args {args} and kwargs {kwargs}')

    def get_sensor_value(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60

    def close(self):
        print('Test Sensor disconnected!')


class ExtendedTestSensor(TestSensor):
    """ Mock Sensor to test engine to GUI connection Supports all optional sensor features"""
    features = {SensorFeatures.TC_SELECT, SensorFeatures.AIMING_BEAM}

    def __init__(self, *args, **kwargs):
        self.tc = 'K'
        super().__init__(*args, **kwargs)

    def switch_aiming_beam(self, state):
        with self.com_lock:
            print(f'Test sensor aiming beam switched {'on' if state else 'off'}!')

    def set_sensor_tc(self, tc):
        with self.com_lock:
            self.tc = tc
            print(f'Test sensor TC set to {tc}!')

    def get_sensor_tc(self):
        with self.com_lock:
            return self.tc


class TestSensorVoltage(AbstractSensor):
    """Mock Sensor to test engine to GUI connection"""
    type = UnitType.VOLTAGE

    def __init__(self, *args, **kwargs):
        print('Test Sensor Voltage connected!')
        self.com_lock = threading.Lock()
        print(f'Called with args {args} and kwargs {kwargs}')

    def get_sensor_value(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60

    def close(self):
        print('Test Sensor disconnected!')


class TestController(AbstractController):
    """
    Mock controller to test engine to GUI connection, minimal PID and manual control functions
    Rate is implemented; the working setpoint approaches the target setpoint with the set rate
    PID is mocked; the process variable always approaches the target setpoint asymptotically
    """

    type = UnitType.TEMPERATURE
    features = {ControllerFeatures.MANUAL_POWER, ControllerFeatures.SIMPLE_PID}

    def __init__(self, *args, **kwargs):
        self.com_lock = threading.Lock()
        print('Test Controller connected!')
        print(f'Called with args {args} and kwargs {kwargs}')

        self.target_sp = 0
        self.working_sp = 0
        self.pv = 0
        self.rate = 5

        self.pid_p = 1
        self.pid_i = 1
        self.pid_d = 1

        self.mode = 'Automatic'
        self.manual_power = 0

    def set_rate(self, rate):
        with self.com_lock:
            self.rate = rate
            print('Test Controller: Set rate {:f}'.format(rate))

    def set_target_setpoint(self, setpoint):
        with self.com_lock:
            self.target_sp = setpoint
            print('Test Controller: Set target setpoint {:f}'.format(setpoint))

    def get_process_variable(self):
        with self.com_lock:
            time.sleep(0.01)
            self.pv = 0.9 * self.pv + 0.1 * self.working_sp
            return self.pv

    def get_target_setpoint(self):
        with self.com_lock:
            return self.target_sp

    def get_rate(self):
        with self.com_lock:
            return self.rate

    def get_working_setpoint(self):
        with self.com_lock:
            self.working_sp += self.rate / 60
            if self.working_sp > self.target_sp:
                self.working_sp = self.target_sp
            return self.working_sp

    def get_pid_p(self):
        with self.com_lock:
            return self.pid_p

    def get_pid_i(self):
        with self.com_lock:
            return self.pid_i

    def get_pid_d(self):
        with self.com_lock:
            return self.pid_d

    def set_pid_p(self, p):
        with self.com_lock:
            self.pid_p = p
            print('Test Controller: Set PID P {:f}'.format(p))

    def set_pid_i(self, i):
        with self.com_lock:
            self.pid_i = i
            print('Test Controller: Set PID I {:f}'.format(i))

    def set_pid_d(self, d):
        with self.com_lock:
            self.pid_d = d
            print('Test Controller: Set PID D {:f}'.format(d))

    def close(self):
        print('Test Controller disconnected!')

    def emergency_stop(self):
        self.set_manual_mode()
        self.set_manual_output_power(0)
        print('Test Controller emergency stop!')

    def get_control_mode(self):
        with self.com_lock:
            return self.mode

    def set_manual_mode(self):
        with self.com_lock:
            self.mode = 'Manual'
            print('Test Controller set to manual mode!')

    def set_automatic_mode(self):
        with self.com_lock:
            self.mode = 'Automatic'
            print('Test Controller set to automatic mode!')

    def set_manual_output_power(self, output):
        with self.com_lock:
            self.manual_power = output
            print('Test Controller set manual output power to {:f}'.format(output))

    def get_manual_output_power(self):
        with self.com_lock:
            return self.manual_power

    def get_working_output(self):
        return self.manual_power * (1 + 0.2 * random.random())


class ExtendedTestController(TestController):
    features = {ControllerFeatures.MANUAL_POWER, ControllerFeatures.OUTPUT_ENABLE, ControllerFeatures.GAIN_SCHEDULING,
                ControllerFeatures.TC_SELECT, ControllerFeatures.AIMING_BEAM}

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self.pid_p2 = 2
        self.pid_i2 = 2
        self.pid_d2 = 2
        self.pid_p3 = 2
        self.pid_i3 = 2
        self.pid_d3 = 2

        self.gain_sched = ''
        self.active_set = 1
        self.boundary_12 = 12.12
        self.boundary_23 = 23.23

        self.tc = 'J'

        self.output = False
        self.aiming_beam = False

    def get_pid_p2(self):
        with self.com_lock:
            return self.pid_p2

    def get_pid_i2(self):
        with self.com_lock:
            return self.pid_i2

    def get_pid_d2(self):
        with self.com_lock:
            return self.pid_d2

    def get_pid_p3(self):
        with self.com_lock:
            return self.pid_p3

    def get_pid_i3(self):
        with self.com_lock:
            return self.pid_i3

    def get_pid_d3(self):
        with self.com_lock:
            return self.pid_d3

    def set_pid_p2(self, p):
        with self.com_lock:
            self.pid_p2 = p
            print('Test Controller: Set PID P2 {:f}'.format(p))

    def set_pid_i2(self, i):
        with self.com_lock:
            self.pid_i2 = i
            print('Test Controller: Set PID I2 {:f}'.format(i))

    def set_pid_d2(self, d):
        with self.com_lock:
            self.pid_d2 = d
            print('Test Controller: Set PID D2 {:f}'.format(d))

    def set_pid_p3(self, p):
        with self.com_lock:
            self.pid_p3 = p
            print('Test Controller: Set PID P3 {:f}'.format(p))

    def set_pid_i3(self, i):
        with self.com_lock:
            self.pid_i3 = i
            print('Test Controller: Set PID I3 {:f}'.format(i))

    def set_pid_d3(self, d):
        with self.com_lock:
            self.pid_d3 = d
            print('Test Controller: Set PID D3 {:f}'.format(d))

    def get_gain_scheduling(self):
        with self.com_lock:
            return self.gain_sched

    def set_gain_scheduling(self, sched):
        with self.com_lock:
            self.gain_sched = sched
            print('Test Controller: Set gain scheduling to {:s}'.format(sched))

    def get_active_set(self):
        with self.com_lock:
            return self.active_set

    def set_active_set(self, active_set):
        with self.com_lock:
            self.active_set = active_set
            print('Test Controller: Set active set to {:d}'.format(active_set))

    def get_boundary_12(self):
        with self.com_lock:
            return self.boundary_12

    def set_boundary_12(self, boundary):
        with self.com_lock:
            self.boundary_12 = boundary
            print('Test Controller: Set boundary 12 to {:f}'.format(boundary))

    def get_boundary_23(self):
        with self.com_lock:
            return self.boundary_23

    def set_boundary_23(self, boundary):
        with self.com_lock:
            self.boundary_23 = boundary
            print('Test Controller: Set boundary 23 to {:f}'.format(boundary))

    def enable_aiming_beam(self):
        with self.com_lock:
            self.aiming_beam = True
            print('Test Controller: Enable aiming beam!')

    def disable_aiming_beam(self):
        with self.com_lock:
            self.aiming_beam = False
            print('Test Controller: Disable aiming beam!')

    def enable_output(self):
        with self.com_lock:
            self.output = True
            print('Test Controller: Enable output!')

    def disable_output(self):
        with self.com_lock:
            self.output = False
            print('Test Controller: Disable output!')

    def set_tc_type(self, tc):
        with self.com_lock:
            self.tc = tc
            print('Test Controller: Set TC type to {:s}'.format(self.tc))

    def get_tc_type(self):
        with self.com_lock:
            return self.tc


class FaultyTestController(TestController):
    def _faulty_reading(self, function):
        """ 5 % chance of simulated serial failure"""
        if random.random() < 0.05:
            with self.com_lock:
                time.sleep(0.01)
                raise serial.SerialException('Simulated serial port failure!')
        else:
            return function

    def get_process_variable(self):
        return self._faulty_reading(super().get_process_variable())

    def get_working_setpoint(self):
        return self._faulty_reading(super()).get_working_setpoint()

    def get_working_output(self):
        return self._faulty_reading(super().get_working_output())

    def get_target_setpoint(self):
        return self._faulty_reading(super().get_target_setpoint())

    def get_rate(self):
        return self._faulty_reading(super().get_rate())
