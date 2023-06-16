import time

import pubsub.pub
import pubsub.pub
from PySide2.QtCore import QTimer


class SetpointProgrammer:
    def __init__(self, segments, engine):
        self.segments = segments
        self.is_ramping = True
        self.current_segment = 1
        self.hold_starttime = int(time.time())
        self.hold_endtime = int(time.time())

        self.pv = 0
        pubsub.pub.subscribe(self.set_pv, topicName='engine.answer.status')

        self.timer = QTimer()
        self.timer.timeout.connect(self.execute)
        self.timer.start(1000)

        pubsub.pub.sendMessage('gui.set.control_mode', mode='Automatic')
        self.start_ramp()
        # TODO: Add setpoint commands for the first ramp segment

    def execute(self):
        if self.is_ramping:
            # Check if target temperature is reached, then switch to hold
            if abs(self.pv-self.segments[self.current_segment].get('Setpoint')) < 0.1:
                self.start_hold(self.segments[self.current_segment].get('Hold'))
        else:
            # Check if hold time has elapsed, then switch to next segment
            if int(time.time() > self.hold_endtime):
                self.current_segment = min(len(self.segments)-1, self.current_segment+1)
                self.start_ramp()

    def set_pv(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type recieved: {:s}'.format(str(type(status_values)))
        if 'Controller PV' in status_values.keys():
            self.pv = status_values['Controller PV'][0]

    def start_ramp(self):
        self.is_ramping = True
        print(f'Starting {self.current_segment}')
        pubsub.pub.sendMessage('gui.set.rate', rate=self.segments[self.current_segment].get('Rate'))
        pubsub.pub.sendMessage('gui.set.setpoint', setpoint=self.segments[self.current_segment].get('Setpoint'))

    def start_hold(self, hold_time):
        self.is_ramping = False
        self.hold_starttime = int(time.time())
        self.hold_endtime = self.hold_starttime+hold_time
