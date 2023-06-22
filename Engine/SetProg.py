import time

import pubsub.pub
import pubsub.pub
from PySide2.QtCore import QTimer


class SetpointProgrammer:
    def __init__(self, segments, engine):
        self.segments = segments
        self.is_ramping = False
        self.current_segment = 0
        self.hold_starttime = int(time.time())
        self.hold_endtime = int(time.time())

        # Maybe the segments thing can be solved with an iterator?

        self.working_setpoint = 0
        pubsub.pub.subscribe(self.set_working_setpoint, topicName='engine.answer.status')

        self.timer = QTimer()
        self.timer.timeout.connect(self.execute)
        self.timer.start(1000)

        pubsub.pub.sendMessage('gui.set.control_mode', mode='Automatic')

    def execute(self):
        if self.is_ramping:
            # Check if the working setpoint of the controller has reached the target setpoint, then switch to hold
            if abs(self.working_setpoint - self.segments[self.current_segment].get('Setpoint')) < 0.1:
                self.start_hold(self.segments[self.current_segment].get('Hold'))

        else:
            # Check if hold time has elapsed, then switch to next segment
            if int(time.time()) > self.hold_endtime and self.current_segment < len(self.segments):
                self.current_segment += 1
                self.start_ramp()

    def set_working_setpoint(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type recieved: {:s}'.format(str(type(status_values)))
        if 'Setpoint' in status_values.keys():
            self.working_setpoint = status_values['Setpoint'][0]

    def start_ramp(self):
        self.is_ramping = True
        pubsub.pub.sendMessage('gui.set.rate', rate=self.segments[self.current_segment].get('Rate'))
        pubsub.pub.sendMessage('gui.set.setpoint', setpoint=self.segments[self.current_segment].get('Setpoint'))
        pubsub.pub.sendMessage('engine.status', text=f'Ramp segment {self.current_segment} started.')

    def start_hold(self, hold_time):
        self.is_ramping = False
        self.hold_starttime = int(time.time())
        self.hold_endtime = self.hold_starttime+hold_time*60
        pubsub.pub.sendMessage('engine.status', text=f'Hold segment {self.current_segment} started.')