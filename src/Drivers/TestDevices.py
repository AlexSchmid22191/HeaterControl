import time
import threading
from src.Drivers.BaseClasses import AbstractSensor, AbstractController


class TestSensor(AbstractSensor):
    """Mock Sensor to test engine to GUI connection"""
    mode = 'Temperature'

    def __init__(self, *args, **kwargs):
        print('Test Sensor connected!')
        self.com_lock = threading.Lock()
        print(args, kwargs)

    def get_sensor_value(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60

    def close(self):
        print('Test Sensor disconnected!')


class TestSensorVoltage(AbstractSensor):
    """Mock Sensor to test engine to GUI connection"""
    mode = 'Voltage'

    def __init__(self, *args, **kwargs):
        print('Test Sensor Voltage connected!')
        self.com_lock = threading.Lock()
        print(args, kwargs)

    def get_sensor_value(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60

    def close(self):
        print('Test Sensor disconnected!')


class TestController(AbstractController):
    """Mock controller to test engine to GUI connection"""

    mode = 'Temperature'

    def __init__(self, *args, **kwargs):
        self.com_lock = threading.Lock()
        print('Test Controller connected!')
        print(args, kwargs)

    def get_process_variable(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60 + 1

    def get_target_setpoint(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60 + 2

    def get_working_output(self):
        with self.com_lock:
            time.sleep(0.01)
            return 100 - time.time() % 100

    def get_working_setpoint(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60 + 4

    def get_control_mode(self):
        with self.com_lock:
            time.sleep(0.01)
            return 'Automatic' if time.time() % 60 > 30 else 'Manual'

    def get_rate(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 15

    def set_target_setpoint(self, setpoint):
        with self.com_lock:
            print('Test Controller: Set target setpoint {:f}'.format(setpoint))

    def set_manual_output_power(self, output):
        with self.com_lock:
            print('Test Controller: Set output power {:f}'.format(output))

    def set_automatic_mode(self):
        with self.com_lock:
            print('Test Controller: Set to automatic mode')

    def set_manual_mode(self):
        with self.com_lock:
            print('Test Controller: Set to manual mode')

    def set_rate(self, rate):
        with self.com_lock:
            print('Test Controller: Set rate {:f}'.format(rate))

    def close(self):
        print('Test Sensor disconnected!')


class NiceTestController(TestController):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self.tsp = 0
        self.wsp = 0
        self.pv = 0
        self.rt = 5

    def get_process_variable(self):
        with self.com_lock:
            time.sleep(0.01)
            self.pv = 0.9*self.pv + 0.1*self.wsp
            return self.pv

    def set_rate(self, rate):
        with self.com_lock:
            self.rt = rate
            print('Test Controller: Set rate {:f}'.format(rate))

    def set_target_setpoint(self, setpoint):
        with self.com_lock:
            self.tsp = setpoint
            print('Test Controller: Set target setpoint {:f}'.format(setpoint))

    def get_target_setpoint(self):
        with self.com_lock:
            return self.tsp

    def get_rate(self):
        with self.com_lock:
            return self.rt

    def get_working_setpoint(self):
        with self.com_lock:
            self.wsp += self.rt/60
            if self.wsp > self.tsp:
                self.wsp = self.tsp
            return self.wsp

    def close(self):
        print('Test Sensor disconnected!')