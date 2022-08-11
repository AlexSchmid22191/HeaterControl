import functools

import pubsub.pub
from PySide2.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QRadioButton, QVBoxLayout, QPushButton


class ElchControlMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Setpoint', 'Rate', 'Power']}
        self.entries = {key: QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=10000) for key in self.labels}
        self.entries['Power'].setMaximum(100)
        self.entries['Power'].setSuffix(' %')
        self.buttons = {key: QRadioButton(text=key) for key in ['Automatic', 'Manual']}

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        for label in self.labels:
            self.entries[label].setKeyboardTracking(False)
            self.entries[label].valueChanged.connect(functools.partial(self.set_control_value, control=label))
            vbox.addWidget(self.labels[label], stretch=0)
            vbox.addWidget(self.entries[label], stretch=0)
            vbox.addSpacing(10)

        vbox.addWidget(QLabel(text='Control mode', objectName='Header'))
        for button in self.buttons:
            vbox.addWidget(self.buttons[button])
            self.buttons[button].toggled.connect(functools.partial(self.set_control_mode, mode=button))

        refresh_button = QPushButton(text='Refresh', objectName='Refresh')
        refresh_button.clicked.connect(lambda: pubsub.pub.sendMessage('gui.request.control_parameters'))
        vbox.addSpacing(10)
        vbox.addWidget(refresh_button)

        vbox.addStretch()
        self.setLayout(vbox)

        pubsub.pub.subscribe(self.update_control_values, 'engine.answer.control_parameters')

    @staticmethod
    def set_control_value(value, control):
        {
            'Rate': functools.partial(pubsub.pub.sendMessage, 'gui.set.rate', rate=value),
            'Power': functools.partial(pubsub.pub.sendMessage, 'gui.set.power', power=value),
            'Setpoint': functools.partial(pubsub.pub.sendMessage, 'gui.set.setpoint', setpoint=value)
        }[control]()

    @staticmethod
    def set_control_mode(checked, mode):
        if checked:
            pubsub.pub.sendMessage('gui.set.control_mode', mode=mode)

    def change_units(self, mode):
        self.entries['Setpoint'].setSuffix({'Temperature': ' \u00B0C', 'Voltage': ' mV'}[mode])
        self.entries['Rate'].setSuffix({'Temperature': ' \u00B0C/min', 'Voltage': ' mV/min'}[mode])

    def update_control_values(self, control_parameters):
        assert isinstance(control_parameters, dict), 'Illegal type recieved: {:s}'.format(str(type(control_parameters)))
        for key in control_parameters:
            assert key in self.entries or key == 'Mode', 'Illegal key recieved: {:s}'.format(key)
            if key == 'Mode':
                self.buttons[control_parameters[key]].blockSignals(True)
                self.buttons[control_parameters[key]].setChecked(True)
                self.buttons[control_parameters[key]].blockSignals(False)
            else:
                self.entries[key].blockSignals(True)
                self.entries[key].setValue(control_parameters[key])
                self.entries[key].blockSignals(False)
