import time

from PySide2.QtCore import QTimer
from src.Signals import engine_signals


class SetpointProgrammer:
    def __init__(self, segments, engine):
        self.engine = engine
        self.segments = segments
        self.is_ramping = False
        self.current_segment = 0
        self.hold_start_time = int(time.time())
        self.hold_endtime = int(time.time())

        self.working_setpoint = 0
        engine_signals.controller_status_update.connect(self.set_working_setpoint)

        self.timer = QTimer()
        self.timer.timeout.connect(self.execute)
        self.timer.start(1000)

        engine.controller.set_automatic_mode()

    def execute(self):
        if self.is_ramping:
            # Check if the working setpoint of the controller has reached the target setpoint, then switch to hold
            if abs(self.working_setpoint - self.segments[self.current_segment].get('Setpoint')) < 0.1:
                self.start_hold(self.segments[self.current_segment].get('Hold'))

        else:
            # Check if hold time has elapsed, then switch to next segment
            if int(time.time()) > self.hold_endtime and self.current_segment < len(self.segments) and self.hold_endtime>0:
                self.current_segment += 1
                self.start_ramp()

    def set_working_setpoint(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type recieved: {:s}'.format(str(type(status_values)))
        if 'Setpoint' in status_values.keys():
            self.working_setpoint = status_values['Setpoint']

    def start_ramp(self):
        self.is_ramping = True
        self.engine.controller.set_rate(self.segments[self.current_segment].get('Rate'))
        self.engine.controller.set_target_setpoint(self.segments[self.current_segment].get('Setpoint'))
        engine_signals.ramp_segment_started.emit(self.current_segment)

    def start_hold(self, hold_time):
        self.is_ramping = False
        self.hold_start_time = int(time.time())
        self.hold_endtime = self.hold_start_time + hold_time * 60

        # Option for indefinite hold
        if hold_time == -1:
            self.hold_endtime = -1
        engine_signals.hold_segment_started.emit(self.current_segment)
