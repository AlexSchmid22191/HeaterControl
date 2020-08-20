import functools
import pubsub.pub
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDoubleSpinBox, QLabel, QRadioButton, QComboBox, \
    QFormLayout, QButtonGroup, QSpinBox, QFileDialog


class ElchMenuPages(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: Implement this with a stackedlayout
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

        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Controller', 'Sensor']}
        self.device_menus = {key: QComboBox() for key in self.labels}
        self.port_menus = {key: QComboBox() for key in self.labels}
        self.connect_buttons = {key: QPushButton(text='Connect', objectName=key) for key in self.labels}
        self.refresh_buttons = {key: QPushButton(text='Refresh', objectName='Refresh') for key in self.labels}

        self.buttongroup = QButtonGroup()
        self.buttongroup.setExclusive(False)
        self.buttongroup.buttonToggled.connect(self.connect_device)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        for key in self.labels:
            self.buttongroup.addButton(self.connect_buttons[key])
            self.connect_buttons[key].setCheckable(True)
            self.refresh_buttons[key].clicked.connect(lambda: pubsub.pub.sendMessage('gui.request.devices'))
            vbox.addWidget(self.labels[key])
            vbox.addWidget(self.device_menus[key])
            vbox.addWidget(self.port_menus[key])
            vbox.addWidget(self.connect_buttons[key])
            vbox.addWidget(self.refresh_buttons[key])
            vbox.addSpacing(20)
        vbox.addStretch()
        self.setLayout(vbox)

        pubsub.pub.subscribe(listener=self.populate_menus, topicName='engine.broadcast.devices')

    def populate_menus(self, ports, devices):
        """Populate the controller and sensor menus with lists of device names and ports"""
        for key in self.port_menus:
            self.port_menus[key].clear()
            self.device_menus[key].clear()
            self.port_menus[key].addItems(ports)
            self.device_menus[key].addItems(devices[key])

    def connect_device(self, source, state):
        key = source.objectName()
        port = self.port_menus[key].currentText()
        device = self.device_menus[key].currentText()

        if state:
            if key == 'Controller':
                pubsub.pub.sendMessage('gui.con.connect_controller', controller_type=device, controller_port=port)
            elif key == 'Sensor':
                pubsub.pub.sendMessage('gui.con.connect_sensor', sensor_type=device, sensor_port=port)
        else:
            if key == 'Controller':
                pubsub.pub.sendMessage('gui.con.disconnect_controller')
            elif key == 'Sensor':
                pubsub.pub.sendMessage('gui.con.disconnect_sensor')


class ElchControlMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.suffixes = {'Temperature': {'Setpoint': ' °C', 'Rate': ' °C/min', 'Power': ' %'},
                         'Voltage': {'Setpoint': ' mV', 'Rate': ' mV/min', 'Power': ' %'}}

        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Setpoint', 'Rate', 'Power']}
        self.entries = {key: QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=10000) for key in self.labels}
        self.entries['Power'].setMaximum(100)
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
        functions = {'Rate': functools.partial(pubsub.pub.sendMessage, 'gui.set.rate', rate=value),
                     'Power': functools.partial(pubsub.pub.sendMessage, 'gui.set.power', power=value),
                     'Setpoint': functools.partial(pubsub.pub.sendMessage, 'gui.set.setpoint', setpoint=value)}
        functions[control]()

    @staticmethod
    def set_control_mode(checked, mode):
        if checked:
            pubsub.pub.sendMessage('gui.set.control_mode', mode=mode)

    def change_units(self, mode):
        for entry in self.entries:
            self.entries[entry].setSuffix(self.suffixes[mode][entry])

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


class ElchPlotMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Clear', 'Export']
        self.buttons = {key: QPushButton(parent=self, text=key, objectName=key) for key in controls}
        self.buttons['Start'].setCheckable(True)

        vbox = QVBoxLayout()
        for key in controls:
            vbox.addWidget(self.buttons[key])
            self.buttons[key].clicked.connect({'Start': functools.partial(self.start_stop_plotting),
                                               'Clear': self.clear_pplot, 'Export': self.export_data}[key])
        vbox.addStretch()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(vbox)

    def broadcast_plot_command(self, button):
        if button == 'Clear' and self.buttons['Start'].isChecked():
            self.buttons['Start'].click()

    def start_stop_plotting(self):
        pubsub.pub.sendMessage('gui.plot.start' if self.buttons['Start'].isChecked() else 'gui.plot.stop')

    def clear_pplot(self):
        pubsub.pub.sendMessage('gui.plot.clear')
        if self.buttons['Start'].isChecked():
            self.buttons['Start'].click()

    def export_data(self):
        if (file_path := QFileDialog.getSaveFileName(self, 'Save as...', 'Logs/Log.csv', 'CSV (*.csv)')[0]) != '':
            pubsub.pub.sendMessage('gui.plot.export', filepath=file_path)


class ElchPidMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suffixes = {'Temperature': ' °C', 'Voltage': ' mV'}
        parameters = {'Gain Scheduling': {'GS': 'Gain scheduling', 'AS': 'Active Set', 'B12': 'Boundary 1/2',
                                          'B23': 'Boundary 2/3'},
                      'Set 1': {'P1': 'Proportional 1', 'I1': 'Integral 1 (s)', 'D1': 'Derivative 1 (s)'},
                      'Set 2': {'P2': 'Proportional 2', 'I2': 'Integral 2 (s)', 'D2': 'Derivative 2 (s)'},
                      'Set 3': {'P3': 'Proportional 3', 'I3': 'Integral 3 (s)', 'D3': 'Derivative 3 (s)'}}

        self.entries = {key: QComboBox() if key == 'GS' else QSpinBox(minimum=1, maximum=3) if key == 'AS'
                        else QDoubleSpinBox(decimals=1, singleStep=10, minimum=0, maximum=10000)
                        for subset in parameters for key in parameters[subset]}
        self.entries['GS'].addItems(['None', 'Set', 'Process Variable', 'Setpoint', 'Output'])

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

        for key in self.entries:
            if key == 'GS':
                self.entries[key].currentTextChanged.connect(functools.partial(self.set_pid_parameter, control=key))
            else:
                self.entries[key].valueChanged.connect(functools.partial(self.set_pid_parameter, control=key))

        pubsub.pub.subscribe(self.update_pid_parameters, 'engine.answer.pid_parameters')

    @staticmethod
    def set_pid_parameter(value, control):
        pubsub.pub.sendMessage('gui.set.pid_parameters', parameter=control, value=value)

    def update_pid_parameters(self, pid_parameters):
        for key in pid_parameters:
            if key == 'GS':
                self.entries[key].blockSignals(True)
                self.entries[key].setCurrentText(pid_parameters[key])
                self.entries[key].blockSignals(False)
            else:
                self.entries[key].blockSignals(True)
                self.entries[key].setValue(pid_parameters[key])
                self.entries[key].blockSignals(False)

    def change_mode(self, mode):
        for entry in ['B12', 'B23']:
            self.entries[entry].setSuffix(self.suffixes[mode])
