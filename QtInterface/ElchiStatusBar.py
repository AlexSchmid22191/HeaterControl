import pubsub.pub
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout


class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.unit = '\u00B0C'

        parameters = ['Sensor PV', 'Controller PV', 'Setpoint', 'Power']
        icons = {key: QLabel() for key in parameters}
        labels = {key: QLabel(text=key, objectName='label') for key in parameters}
        self.values = {key: QLabel(text='- - -', objectName='value') for key in parameters}
        vboxes = {key: QVBoxLayout() for key in parameters}

        hbox = QHBoxLayout()
        for key in parameters:
            vboxes[key].addWidget(self.values[key])
            vboxes[key].addWidget(labels[key])
            vboxes[key].setContentsMargins(0, 0, 0, 0)
            vboxes[key].setSpacing(5)
            hbox.addWidget(icons[key])
            hbox.addStretch(1)
            hbox.addLayout(vboxes[key])
            hbox.addStretch(10)
            icons[key].setPixmap(QPixmap('Icons/Ring_{:s}.png'.format(key)))
        hbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(hbox)

        self.timer = QTimer(parent=self)
        self.timer.timeout.connect(lambda: pubsub.pub.sendMessage(topicName='gui.request.status'))
        self.timer.start(1000)
        pubsub.pub.subscribe(self.update_values, topicName='engine.answer.status')

    def update_values(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type recieved: {:s}'.format(str(type(status_values)))

        for key, value in status_values.items():
            assert key in self.values, 'Illegal key recieved: {:s}'.format(key)
            if key == 'Power':
                self.values[key].setText('{:.1f} %'.format(value[0]))
            else:
                self.values[key].setText('{:.1f} {:s}'.format(value[0], self.unit))

    def change_units(self, mode):
        self.unit = {'Temperature': '\u00B0C', 'Voltage': 'mV'}[mode]
