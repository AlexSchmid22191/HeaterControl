import pubsub.pub
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout


class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.unit = '\u00B0C'

        parameters = ['Sensor PV', 'Controller PV', 'Setpoint', 'Power']
        icons = {key: QLabel() for key in parameters}
        self.labels = {key: QLabel(text=key+'\n ---', objectName='label') for key in parameters}
        self.values = {key: QLabel(text='- - -', objectName='value') for key in parameters}
        vboxes = {key: QVBoxLayout() for key in parameters}

        hbox = QHBoxLayout()
        for key in parameters:
            vboxes[key].addWidget(self.values[key])
            vboxes[key].addWidget(self.labels[key])
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

        self.exp_labels = {'Sensor PV': {'Temperature': 'Sample Temperature', 'Voltage': 'Pump Voltage'},
                           'Controller PV': {'Temperature': 'Oven Temperature', 'Voltage': '\u03bb Probe Voltage'},
                           'Setpoint': {'Temperature': 'Target Oven Temperature', 'Voltage': 'Target \u03bb Probe Voltage'},
                           'Power':{'Temperature': 'Oven Power', 'Voltage': 'Pump Power'}}

    def update_values(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type recieved: {:s}'.format(str(type(status_values)))

        for key, value in status_values.items():
            assert key in self.values, 'Illegal key recieved: {:s}'.format(key)
            if key == 'Power':
                self.values[key].setText('{:.1f} %'.format(value[0]))
            else:
                self.values[key].setText('{:.1f} {:s}'.format(value[0], self.unit))

    def change_units(self, mode):
        match mode:
            case 'Temperature':
                self.unit = '\u00B0C'
            case 'Voltage':
                self.unit = 'mV'
        for key, label in self.exp_labels.items():
            self.labels[key].setText(key + '\n' + label[mode])
