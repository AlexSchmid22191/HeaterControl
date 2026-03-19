from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

from src.Drivers.BaseClasses import UnitType
from src.Signals import engine_signals


class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.unit = '\u00B0C'

        parameters = ['Sensor PV', 'Controller PV', 'Setpoint', 'Power']
        icons = {key: QLabel() for key in parameters}
        self.labels = {key: QLabel(text=key + '\n ---') for key in parameters}
        self.values = {key: QLabel(text='- - -') for key in parameters}
        v_boxes = {key: QVBoxLayout() for key in parameters}
        for key, label in self.labels.items():
            label.setObjectName('label')
        for key, label in self.values.items():
            label.setObjectName('value')

        hbox = QHBoxLayout()
        for key in parameters:
            v_boxes[key].addWidget(self.values[key])
            v_boxes[key].addWidget(self.labels[key])
            v_boxes[key].setContentsMargins(0, 0, 0, 0)
            v_boxes[key].setSpacing(5)
            hbox.addWidget(icons[key])
            hbox.addStretch(1)
            hbox.addLayout(v_boxes[key])
            hbox.addStretch(10)
            icons[key].setPixmap(QPixmap('Icons/Ring_{:s}.png'.format(key)))
        hbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(hbox)

        engine_signals.controller_status_update.connect(self.update_values)
        engine_signals.sensor_status_update.connect(self.update_values)

        self.exp_labels = {'Sensor PV': {UnitType.TEMPERATURE: 'Sample Temperature', UnitType.VOLTAGE: 'Pump Voltage'},
                           'Controller PV': {UnitType.TEMPERATURE: 'Oven Temperature', UnitType.VOLTAGE: '\u03bb Probe Voltage'},
                           'Setpoint': {UnitType.TEMPERATURE: 'Target Oven Temperature',
                                        UnitType.VOLTAGE: 'Target \u03bb Probe Voltage'},
                           'Power': {UnitType.TEMPERATURE: 'Oven Power', UnitType.VOLTAGE: 'Pump Power'}}

    def update_values(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type received: {:s}'.format(str(type(status_values)))

        for key, value in status_values.items():
            assert key in self.values, 'Illegal key received: {:s}'.format(key)
            if key == 'Power':
                self.values[key].setText('{:.1f} %'.format(value))
            else:
                self.values[key].setText('{:.1f} {:s}'.format(value, self.unit))

    def change_units(self, utype):
        match utype:
            case UnitType.TEMPERATURE:
                self.unit = '\u00B0C'
            case UnitType.VOLTAGE:
                self.unit = 'mV'
        for key, label in self.exp_labels.items():
            self.labels[key].setText(key + '\n' + label[utype])
