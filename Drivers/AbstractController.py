class AbstractController:
    """
    Abstract base class for controllers. Drivers for specific devices inherit this class and implement the methods.
    Raises a NotImplementedException if the methods are not overwritten in derived subclasses.
    """

    def get_process_variable(self):
        """Return the current process variable of the controller (often this is the oven thermocouple temperature)"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_process_variable',
                                                                                      self.__class__.__name__))

    def set_target_setpoint(self, temperature):
        """Set the target setpoint"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_target_setpoint',
                                                                                      self.__class__.__name__))

    def get_target_setpoint(self, temperature):
        """Get the target setpoint (this is not always the working setpoint"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_target_setpoint',
                                                                                      self.__class__.__name__))

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_manual_output_power',
                                                                                      self.__class__.__name__))

    def get_working_output(self):
        """Return the current power output of the controller in percent"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get__working_output',
                                                                                      self.__class__.__name__))

    def get_working_setpoint(self):
        """Get the current working setpoint of the controller (this is not always the target setpoint)"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_working_setpoint',
                                                                                      self.__class__.__name__))

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint e.g. the heating/cooling rate"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_rate',
                                                                                      self.__class__.__name__))

    def get_rate(self, rate):
        """Get the rate of change for the working setpoint e.g. the heating/cooling rate"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_rate',
                                                                                      self.__class__.__name__))

    def set_automatic_mode(self):
        """Set controller to automatic mode, output power is controlled by PID"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_automatic_mode',
                                                                                      self.__class__.__name__))

    def set_manual_mode(self):
        """Set controller to manual mode, output power is held constant at defined percentage"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_manual_mode',
                                                                                      self.__class__.__name__))

    def get_control_mode(self):
        """Get the active control mode"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('get_control_mode',
                                                                                      self.__class__.__name__))

    def write_external_target_setpoint(self, temperature):
        """Set an external target setpoint"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('write_external_target_setpoint',
                                                                                      self.__class__.__name__))

    def write_external_sensor_value(self, temperature):
        """Write process variable from an external sensor to the controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('write_external_sensor_value',
                                                                                      self.__class__.__name__))

    def enable_external_sensor_value(self):
        """Enable controlling by the external sensor value instead of internal (e.g. pyrometer instead of oven TC)"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('enable_external_sensor_value',
                                                                                      self.__class__.__name__))

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_p',
                                                                                      self.__class__.__name__))

    def set_pid_i(self, i):
        """Set the I (Integral time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_i',
                                                                                      self.__class__.__name__))

    def set_pid_d(self, d):
        """Set the D (Derivative time) for the PID controller"""
        raise NotImplementedError('Operation {:s} not supported for {:s} yet!'.format('set_pid_d',
                                                                                      self.__class__.__name__))
