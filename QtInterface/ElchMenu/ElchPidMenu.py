import functools

import pubsub.pub
from PySide2.QtWidgets import QWidget, QComboBox, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLabel, QFormLayout, \
    QPushButton


class ElchPidMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parameters = {'Gain Scheduling': {'GS': 'Gain scheduling', 'AS': 'Active Set', 'B12': 'Boundary 1/2',
                                          'B23': 'Boundary 2/3'},
                      'Set 1': {'P1': 'Proportional 1', 'I1': 'Integral 1', 'D1': 'Derivative 1'},
                      'Set 2': {'P2': 'Proportional 2', 'I2': 'Integral 2', 'D2': 'Derivative 2'},
                      'Set 3': {'P3': 'Proportional 3', 'I3': 'Integral 3', 'D3': 'Derivative 3'}}

        self.units = {'I1': ' s', 'I2': ' s', 'I3': ' s', 'D1': ' s', 'D2': ' s', 'D3': ' s'}
        self.entries = {key: QComboBox() if key == 'GS' else QSpinBox(minimum=1, maximum=3) if key == 'AS'
                        else QDoubleSpinBox(decimals=0, singleStep=10, minimum=0, maximum=100000)
                        for subset in parameters for key in parameters[subset]}
        self.entries['GS'].addItems(['None', 'Set', 'Process Variable', 'Setpoint', 'Output'])

        for entry, suffix in self.units.items():
            self.entries[entry].setSuffix(suffix)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)
        for subset in parameters:
            label = QLabel(text=subset, objectName='Header')
            vbox.addWidget(label)
            vbox.addSpacing(10)
            form = QFormLayout()
            form.setSpacing(5)
            form.setHorizontalSpacing(20)
            form.setContentsMargins(0, 0, 0, 0)
            for key in parameters[subset]:
                form.addRow(parameters[subset][key], self.entries[key])
            vbox.addLayout(form)
            vbox.addSpacing(20)

        refresh_button = QPushButton(text='Refresh', objectName='Refresh')
        refresh_button.clicked.connect(lambda: pubsub.pub.sendMessage('gui.request.pid_parameters'))
        vbox.addWidget(refresh_button)

        vbox.addStretch()
        self.setLayout(vbox)

        for key, entry in self.entries.items():
            if key == 'GS':
                entry.currentTextChanged.connect(functools.partial(self.set_pid_parameter, control=key))
            else:
                entry.setKeyboardTracking(False)
                entry.valueChanged.connect(functools.partial(self.set_pid_parameter, control=key))

        pubsub.pub.subscribe(self.update_pid_parameters, 'engine.answer.pid_parameters')

    @staticmethod
    def set_pid_parameter(value, control):
        pubsub.pub.sendMessage('gui.set.pid_parameters', parameter=control, value=value)

    def update_pid_parameters(self, pid_parameters):
        for key in pid_parameters:
            self.entries[key].blockSignals(True)
            if key == 'GS':
                self.entries[key].setCurrentText(pid_parameters[key])
            else:
                self.entries[key].setValue(pid_parameters[key])
            self.entries[key].blockSignals(False)

    def set_unit(self, unit):
        for entry in ['B12', 'B23', 'P1', 'P2', 'P3']:
            self.entries[entry].setSuffix({'Temperature': ' \u00B0C', 'Voltage': ' mv'}[unit])
