import minimalmodbus
import threading


class OmegaPt(minimalmodbus.Instrument):
    mode = 'Temperature'

    def __init__(self, portname, slaveadress, *args, **kwargs):
        super().__init__(portname, slaveadress, *args, **kwargs)

        # Due to the way the Omega Pt works (no Rate setting, just ramp/soak mode) the driver needs to be aware of
        # setpoint and ramp setting
        self.rate = 15  # In °C per minute
        self.setpoint = 0  # In °C

        # Set SP1 to be controlled by ramp soak cycle
        self.write_register(736, 4)
        # Select constant soak time mode
        self.write_register(615, 1)

        self.com_lock = threading.Lock()

    def adjust_ramp_soak(self):
        current_temp = self.get_oven_temp()
        # Calculate ramp time is ms from difference between real and set temp., multiply by 60 for s and 1000 for ms
        time = int(abs((self.setpoint-current_temp)/self.rate)*60*1000)

        with self.com_lock:
            # Select ramp soak profile 99 to edit
            self.write_register(610, 99)
            # 1 Segment in the profile
            self.write_register(612, 1)
            # Select segment 1
            self.write_register(611, 1)
            # Change setpoint to target setpoint
            self.write_float(618, self.setpoint)
            # Set ramp time to calculated time
            self.write_long(620, time)
            # Set soak time to 600 s (a dummy value since it keeps heating after the soak time has run out)
            self.write_long(622, 600000)
            # Hold last level at end of soak
            self.write_register(614, 1)
            # Select soak profile 99 to use
            self.write_register(609, 99)
            # Stop and restart soak profile
            self.write_register(576, 8)
            self.write_register(576, 6)

    def set_target_setpoint(self, temperature):
        """Set the target setpoint, in degree Celsius. Start heating to this setpoint with the set rate"""
        self.setpoint = temperature
        self.adjust_ramp_soak()

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint i.e. the max heating/cooling rate"""
        self.rate = rate
        self.adjust_ramp_soak()

    def get_working_output(self):
        """Return the current power output of the instrument"""
        with self.com_lock:
            output = self.read_float(554)
        return output

    def get_oven_temp(self):
        """Return the current temperature of the internal thermocouple"""
        with self.com_lock:
            temp = self.read_float(640)
        return temp

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            setpoint = self.read_float(548)
        return setpoint
