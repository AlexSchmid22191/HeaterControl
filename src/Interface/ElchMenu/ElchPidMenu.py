import functools

from PySide2.QtWidgets import QWidget, QComboBox, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLabel, QFormLayout, \
    QPushButton

from src.Signals import gui_signals, engine_signals


class ElchPidMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parameters = {'Gain Scheduling': {'GS': 'Gain scheduling', 'AS': 'Active Set', 'B12': 'Boundary 1/2',
                                          'B23': 'Boundary 2/3'},
                      'Set 1': {'P1': 'Proportional 1', 'I1': 'Integral 1', 'D1': 'Derivative 1'},
                      'Set 2': {'P2': 'Proportional 2', 'I2': 'Integral 2', 'D2': 'Derivative 2'},
                      'Set 3': {'P3': 'Proportional 3', 'I3': 'Integral 3', 'D3': 'Derivative 3'}}

        self.units = {'I1': ' s', 'I2': ' s', 'I3': ' s', 'D1': ' s', 'D2': ' s', 'D3': ' s'}
        self.entries = {key: QComboBox() if key == 'GS' else QSpinBox() if key == 'AS' else QDoubleSpinBox()
                        for subset in parameters for key in parameters[subset]}

        for key, entry in self.entries.items():
            if key == 'GS':
                entry.addItems(['None', 'Set', 'Process Variable', 'Setpoint', 'Output'])
            elif key == 'AS':
                entry.setMinimum(1)
                entry.setMaximum(3)
            else:
                entry.setMinimum(0)
                entry.setMaximum(100000)
                entry.setSingleStep(10)
                entry.setDecimals(0)

        for entry, suffix in self.units.items():
            self.entries[entry].setSuffix(suffix)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)
        for subset in parameters:
            label = QLabel(text=subset)
            label.setObjectName('Header')
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

        refresh_button = QPushButton(text='Refresh')
        refresh_button.setObjectName('Refresh')
        # noinspection PyUnresolvedReferences
        refresh_button.clicked.connect(gui_signals.refresh_pid.emit)
        vbox.addWidget(refresh_button)

        vbox.addStretch()
        self.setLayout(vbox)

        for key, entry in self.entries.items():
            if key == 'GS':
                # noinspection PyUnresolvedReferences
                entry.currentTextChanged.connect(functools.partial(self.set_pid_parameter, control=key))
            else:
                entry.setKeyboardTracking(False)
                # noinspection PyUnresolvedReferences
                entry.valueChanged.connect(functools.partial(self.set_pid_parameter, control=key))

        engine_signals.pid_parameters_update.connect(self.update_pid_parameters)

    @staticmethod
    def set_pid_parameter(value, control):
        gui_signals.set_pid_parameters.emit(control, value)

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
