import minimalmodbus
from Drivers.AbstractController import AbstractController
from threading import Lock


class Eurotherm3216(AbstractController, minimalmodbus.Instrument):
    """Instrument class for Eurotherm 3216 process controller.
    Args:
    * portname (str): port name
    * slaveaddress (int): slave address in the range 1 to 247
    """

    def __init__(self, portname, slaveadress):
        super().__init__(portname, slaveadress)
        self.serial.baudrate = 9600
        self.com_lock = Lock()
        self.decimal_precision = 0

    def get_oven_temp(self):
        """Return the current temperature of the internal thermocouple"""
        with self.com_lock:
            return self.read_register(1, number_of_decimals=self.decimal_precision)

    def set_target_setpoint(self, temperature):
        """Set the tagert setpoint, in degree Celsius"""
        with self.com_lock:
            self.write_register(2, temperature, number_of_decimals=self.decimal_precision)

    def set_manual_output_power(self, output):
        """Set the power output of the instrument in percent"""
        with self.com_lock:
            self.write_register(3, output, number_of_decimals=1)

    def get_working_output(self):
        """Return the current power output of the instrument"""
        with self.com_lock:
            return self.read_register(4, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.read_register(5, number_of_decimals=self.decimal_precision)

    def set_rate(self, rate):
        """Set the maximum rate of change for the working setpoint i.e. the max heating/cooling rate"""
        with self.com_lock:
            self.write_register(35, rate, number_of_decimals=1)

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.write_register(273, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.write_register(273, 1)

    def write_external_target_temperature(self, temperature):
        """Set an external target setpoint tenperature (for complex temperature programs)"""
        with self.com_lock:
            self.write_register(26, temperature, number_of_decimals=self.decimal_precision)

    def write_external_sensor_temperature(self, temperature):
        """Write temperature control variable from an external sensor to the instrument """
        with self.com_lock:
            self.write_register(203, temperature, number_of_decimals=self.decimal_precision)

    def enabele_external_sensor_temperature(self):
        """Enable controlling by the external sensor temperature"""
        with self.com_lock:
            self.write_register(1, 1)

    def set_pid_p(self, p):
        with self.com_lock:
            self.write_register(6, p)

    def set_pid_i(self, i):
        with self.com_lock:
            self.write_register(8, i)

    def set_pid_d(self, d):
        with self.com_lock:
            self.write_register(9, d)


class Eurotherm3508(minimalmodbus.Instrument):
    def __init__(self, portname, slaveadress):
        super().__init__(portname, slaveadress)
        self.serial.baudrate = 9600
        self.com_lock = Lock()

    def get_oven_temp(self):
        """Return the current process value (i.e. the "internal" eurotherm sensor)"""
        with self.com_lock:
            return self.read_register(1, number_of_decimals=4, signed=True)

    def set_target_setpoint(self, temperature):
        """Set the tagert setpoint, in degree Celsius"""
        with self.com_lock:
            self.write_register(2, temperature, number_of_decimals=4, signed=True)

    def set_manual_output_power(self, output):
        """Set the power output of the instrument in percent"""
        with self.com_lock:
            self.write_register(3, output, number_of_decimals=1, signed=True)

    def get_working_output(self):
        """Return the current power output of the instrument"""
        with self.com_lock:
            return self.read_register(3, number_of_decimals=1)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.read_register(5, number_of_decimals=4, signed=True)

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.write_register(273, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.write_register(273, 1)

    def set_pid_p(self, p):
        with self.com_lock:
            self.write_register(6, p)

    def set_pid_i(self, i):
        with self.com_lock:
            self.write_register(8, i)

    def set_pid_d(self, d):
        with self.com_lock:
            self.write_register(9, d)