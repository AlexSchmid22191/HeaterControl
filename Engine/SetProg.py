import time

import pubsub.pub
import pubsub.pub
from PySide2.QtCore import QTimer


class SetpointProgrammer:
    def __init__(self, segments, engine):
        self.segments = segments
        self.is_ramping = True
        self.current_segment = 0
        self.hold_starttime = int(time.time())

        self.pv = None
        pubsub.pub.subscribe(self.set_pv, topicName='engine.answer.status')

        self.timer = QTimer(parent=self)
        self.timer.timeout.connect(self.execute)
        self.timer.start(1000)

        # Todo Timer functionality for setpoint

    def execute(self):
        if self.is_ramping:
            # Check if target temperature is reached, then switch to hold
            if abs(self.pv-self.segments[self.current_segment].get('Setpoint')) < 0.1:
                self.start_hold(self.segments[self.current_segment].get('Time'))
        else:
            # Check if hold time has elapsed, then swiutch to next segment
            if int(time.time() > self.hold_endtime):
                self.current_segment = min(len(self.segments)-1, self.current_segment+1)
                self.start_ramp(self.segments[self.current_segment])

    def set_pv(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type recieved: {:s}'.format(str(type(status_values)))
        if 'Controller PV' in status_values.keys():
            self.pv = status_values['Controller PV']

    def start_ramp(self, segment):
        self.is_ramping = True
        pubsub.pub.sendMessage('gui.set.rate', rate=self.segments[self.current_segment].get('Ramp'))
        pubsub.pub.sendMessage('gui.set.setpoint', setpoint=self.segments[self.current_segment].get('Setpoint'))

    def start_hold(self, hold_time):
        self.is_ramping = False
        self.hold_starttime = int(time.time())
        self.hold_endtime = self.hold_starttime+hold_time
