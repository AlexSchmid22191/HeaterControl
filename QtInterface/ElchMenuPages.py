import functools
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDoubleSpinBox, QLabel, QRadioButton, QComboBox, \
    QFormLayout, QButtonGroup


class ElchMenuPages(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO:Implement this with a stackedlayout
        self.setMinimumWidth(200)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.menus = {'Devices': ElchDeviceMenu(), 'Control': ElchControlMenu(), 'Plotting': ElchPlotMenu(),
                      'PID': ElchPidMenu()}

        self.setMinimumWidth(220)

        vbox = QVBoxLayout()
        for menu in self.menus:
            self.menus[menu].setVisible(False)
            vbox.addWidget(self.menus[menu])
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    def adjust_visibility(self, button, visibility):
        menu = button.objectName()
        self.menus[menu].setVisible(visibility)


class ElchDeviceMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key) for key in ['Controller', 'Sensor']}
        self.device_menus = {key: QComboBox() for key in self.labels}
        self.port_menus = {key: QComboBox() for key in self.labels}
        self.connect_buttons = {key: QPushButton(text='Connect', objectName=key) for key in self.labels}
        self.buttongroup = QButtonGroup()
        self.buttongroup.setExclusive(False)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        for key in self.labels:
            self.buttongroup.addButton(self.connect_buttons[key])
            self.connect_buttons[key].setCheckable(True)
            vbox.addWidget(self.labels[key])
            vbox.addWidget(self.device_menus[key])
            vbox.addWidget(self.port_menus[key])
            vbox.addWidget(self.connect_buttons[key])
            vbox.addSpacing(20)
        vbox.addStretch()
        self.setLayout(vbox)

        self.buttongroup.buttonToggled.connect(self.tell_me)

        self.populate_menus(['COM Test']*3, **{'Sensor': ['Sensor Test']*3, 'Controller': ['Controller Test']*3})

    def populate_menus(self, ports, **kwargs):
        """Populate the controller and sensor menus with lists of device names"""
        for key in self.port_menus:
            self.port_menus[key].clear()
            self.device_menus[key].clear()
            self.port_menus[key].addItems(ports)
            self.device_menus[key].addItems(kwargs[key])

    def tell_me(self, source, state):
        key = source.objectName()
        port = self.port_menus[key].currentText()
        device = self.device_menus[key].currentText()
        print(device, port, state)


class ElchControlMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.suffixes = {'Temperature': {'Setpoint': ' °C', 'Rate': ' °C/min', 'Power': ' %'},
                         'Voltage': {'Setpoint': ' mV', 'Rate': ' mV/min', 'Power': ' %'}}

        self.labels = {key: QLabel(text=key) for key in ['Setpoint', 'Rate', 'Power']}
        self.entries = {key: QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=10000) for key in self.labels}
        self.entries['Power'].setMaximum(100)
        self.buttons = {key: QRadioButton(text=key) for key in ['Automatic', 'Manual']}

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        for label in self.labels:
            self.entries[label].setKeyboardTracking(False)
            self.entries[label].valueChanged.connect(functools.partial(self.broadcast_control_value, control=label))
            vbox.addWidget(self.labels[label], stretch=0)
            vbox.addWidget(self.entries[label], stretch=0)
            vbox.addSpacing(10)
        vbox.addWidget(QLabel(text='Control mode'))
        for button in self.buttons:
            vbox.addWidget(self.buttons[button])
            self.buttons[button].toggled.connect(functools.partial(self.broadcast_control_mode, mode=button))
        vbox.addStretch()
        self.setLayout(vbox)

    @staticmethod
    def broadcast_control_value(value, control):
        print(control, value)

    @staticmethod
    def broadcast_control_mode(checked, mode):
        if checked:
            print(mode)

    def change_mode(self, mode):
        for entry in self.entries:
            self.entries[entry].setSuffix(self.suffixes[mode][entry])

    def update_control_values(self, values, control_mode):
        assert isinstance(values, dict), 'Illegal data type recieved: {:s}'.format(str(type(values)))
        for key in values:
            assert key in self.entries, 'Illegal key recieved: {:s}'.format(key)
            if not self.entries[key].hasFocus():
                self.entries[key].setValue(values[key])

        assert control_mode in self.buttons, 'Illegal control mode recieved: {:s}'.format(control_mode)
        self.buttons[control_mode].setChecked(True)


class ElchPlotMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Clear', 'Export']
        self.buttons = {key: QPushButton(parent=self, text=key, objectName=key) for key in controls}
        self.buttons['Start'].setCheckable(True)

        vbox = QVBoxLayout()
        for key in controls:
            self.buttons[key].clicked.connect(functools.partial(self.broadcast_plot_command, key))
            vbox.addWidget(self.buttons[key])
        vbox.addStretch()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(vbox)

    def broadcast_plot_command(self, button):
        state = self.buttons[button].isChecked()
        print(button, state)


class ElchPidMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Split into 4 parts and use headings
        self.suffixes = {'Temperature': ' °C', 'Voltage': ' mV'}
        parameters = {'P1': 'Proportional 1', 'I1': 'Integral 1 (s)', 'D1': 'Derivative 1 (s)',
                      'P2': 'Proportional 2', 'I2': 'Integral 2 (s)', 'D2': 'Derivative 2 (s)',
                      'P3': 'Proportional 3', 'I3': 'Integral 3 (s)', 'D3': 'Derivative 3 (s)',
                      'B12': 'Boundary 1/2', 'B23': 'Boundary 2/3', 'GS': 'Gain scheduling'}

        self.labels = {key: QLabel(text=parameters[key]) for key in parameters}
        self.entries = {key: QComboBox() if key == 'GS' else QDoubleSpinBox(decimals=1, singleStep=10, minimum=0,
                                                                            maximum=10000) for key in parameters}
        self.entries['GS'].addItems(['None', 'Set', 'PV', 'Setpoint'])

        form = QFormLayout()
        form.setSpacing(10)
        form.setContentsMargins(10, 10, 10, 10)
        for key in parameters:
            form.addRow(parameters[key], self.entries[key])
            if key == 'GS':
                self.entries[key].currentTextChanged.connect(functools.partial(self.broadcast_pid_param, control=key))
            else:
                self.entries[key].valueChanged.connect(functools.partial(self.broadcast_pid_param, control=key))
        self.setLayout(form)

    @staticmethod
    def broadcast_pid_param(value, control):
        print(control, value)

    def change_mode(self, mode):
        for entry in ['B12', 'B23']:
            self.entries[entry].setSuffix(self.suffixes[mode])
