import time
from Drivers.AbstractSensorController import AbstractSensor, AbstractController


class TestSensor(AbstractSensor):
    """Mock Sensor to test engine to GUI connection"""
    def __init__(self, *args, **kwargs):
        print('Test Sensor connected!')
        print(kwargs)

    def get_sensor_value(self):
        return time.time() % 60

    def close(self):
        pass


class TestController(AbstractController):
    """Mock controller to test engine to GUI connection"""
    def __init__(self, *args, **kwargs):
        print('Test Controller connected!')
        print(kwargs)

    def get_process_variable(self):
        return time.time() % 60 + 1

    def get_target_setpoint(self, setpoint):
        return time.time() % 60 + 2

    def get_working_output(self):
        return time.time() % 100 + 3

    def get_working_setpoint(self):
        return time.time() % 60 + 4

    def get_control_mode(self):
        return 'Automatic' if time.time() % 60 > 30 else 'Manual'

    def get_rate(self):
        return time.time() % 15
