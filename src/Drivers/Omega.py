import threading

import minimalmodbus

from src.Drivers.BaseClasses import AbstractController


class OmegaPt(AbstractController):
    mode = 'Temperature'

    def __init__(self, _port_name, _slave_address):
        self.instrument = minimalmodbus.Instrument(_port_name, _slave_address)

        self.com_lock = threading.Lock()

        # Due to the way the Omega Pt works (no Rate setting, just ramp/soak mode), the driver needs to be aware of
        # setpoint and ramp setting
        self.rate = 15  # In °C per minute
        self.setpoint = self.instrument.read_float(618)  # In °C

        # For conversion into alternate representation (Proportional band, Integration time and derivative time), the
        # driver needs to be aware of the PID P parameter
        self.kp = 1
        self.get_pid_p()

        # Set SP1 to be controlled by the ramp soak cycle
        self.instrument.write_register(736, 4)
        # Select constant soak time mode
        self.instrument.write_register(615, 1)

    def close(self):
        self.instrument.serial.close()

    def adjust_ramp_soak(self):
        current_temp = self.get_process_variable()
        # Calculate ramp time is ms from the difference between real and set temp., multiply by 60 for s and 1000 for ms
        time = int(abs((self.setpoint - current_temp) / self.rate) * 60 * 1000)

        with self.com_lock:
            # Select ramp soak profile 99 to edit
            self.instrument.write_register(610, 99)
            # 1 Segment in the profile
            self.instrument.write_register(612, 1)
            # Select segment 1
            self.instrument.write_register(611, 1)
            # Change the setpoint to the target setpoint
            self.instrument.write_float(618, self.setpoint)
            # Set ramp time to calculated time
            self.instrument.write_long(620, time)
            # Set soak time to 600 s (a fake value since it keeps heating after the soak time has run out)
            self.instrument.write_long(622, 600000)
            # Hold the last level at the end of soak
            self.instrument.write_register(614, 1)
            # Select soak profile 99 to use
            self.instrument.write_register(609, 99)
            # Stop and restart soak profile
            self.instrument.write_register(576, 8)
            self.instrument.write_register(576, 6)

    def set_target_setpoint(self, temperature):
        """Set the target setpoint, in degree Celsius. Start heating to this setpoint with the set rate"""
        self.setpoint = temperature
        self.adjust_ramp_soak()

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint i.e., the max heating/cooling rate"""
        self.rate = rate
        self.adjust_ramp_soak()

    def get_working_output(self):
        """Return the current power output of the instrument"""
        with self.com_lock:
            return self.instrument.read_float(554)

    def get_process_variable(self):
        """Return the current temperature of the internal thermocouple"""
        with self.com_lock:
            return self.instrument.read_float(640)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.instrument.read_float(548)

    def get_target_setpoint(self):
        return self.setpoint

    def get_rate(self):
        return self.rate

    def get_control_mode(self):
        with self.com_lock:
            return 'Manual' if self.instrument.read_register(576) == 3 else 'Automatic'

    def set_manual_output_power(self, output):
        with self.com_lock:
            self.instrument.write_float(554, output)

    def set_automatic_mode(self):
        with self.com_lock:
            self.instrument.write_register(576, 6)

    def set_manual_mode(self):
        with self.com_lock:
            self.instrument.write_register(576, 3)

    def get_pid_p(self):
        with self.com_lock:
            self.kp = self.instrument.read_float(676)
        return 100 / self.kp

    def set_pid_p(self, p):
        self.kp = 100 / p
        with self.com_lock:
            self.instrument.write_float(676, self.kp)

    def get_pid_i(self):
        self.get_pid_p()
        with self.com_lock:
            return 100 * self.kp / self.instrument.read_float(678)

    def set_pid_i(self, i):
        self.get_pid_p()
        with self.com_lock:
            self.instrument.write_float(678, 100 * self.kp / i)

    def get_pid_d(self):
        self.get_pid_p()
        with self.com_lock:
            return 100 * self.instrument.read_float(680) / self.kp

    def set_pid_d(self, d):
        self.get_pid_p()
        with self.com_lock:
            self.instrument.write_float(680, self.kp * d / 100)
