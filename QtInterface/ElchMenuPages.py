import functools

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDoubleSpinBox, QLabel, QRadioButton, QComboBox, \
    QFormLayout, QSizeGrip


class ElchMenuPages(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(250)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.menus = {'Devices': ElchDeviceMenu(), 'Control': ElchControllerMenu(), 'PID': ElchPidMenu(),
                      'Plotting': ElchPlotMenu()}

        vbox = QVBoxLayout()

        for menu in self.menus:
            self.menus[menu].setVisible(False)
            vbox.addWidget(self.menus[menu])
        vbox.addStretch()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    def adjust_visibility(self, button, visibility):
        menu = button.objectName()
        self.menus[menu].setVisible(visibility)


class ElchPlotMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Stop', 'Resume', 'Clear', 'Export']
        self.buttons = {key: QPushButton(text=key, parent=self) for key in controls}

        vbox = QVBoxLayout()
        for key in controls:
            vbox.addWidget(self.buttons[key])

        self.setLayout(vbox)


class ElchLogMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Stop', 'Pause']
        self.buttons = {key: QPushButton(parent=self, text=key) for key in controls}

        vbox = QVBoxLayout()
        for key in controls:
            vbox.addWidget(self.buttons[key])

        self.setLayout(vbox)


class ElchControllerMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key) for key in ['Setpoint', 'Rate', 'Power']}
        self.entries = {key: QDoubleSpinBox(decimals=1, singleStep=10, minimum=0, maximum=10000) for key in self.labels}
        self.buttons = {key: QRadioButton(text=key) for key in ['Automatic', 'Manual']}

        vbox = QVBoxLayout()
        for label in self.labels:
            self.entries[label].setKeyboardTracking(False)
            self.entries[label].valueChanged.connect(functools.partial(self.dispaly_value, control=label))
            vbox.addWidget(self.labels[label], stretch=0)
            vbox.addWidget(self.entries[label], stretch=0, alignment=Qt.AlignLeft)
            vbox.addStretch(2)

        self.buttons['Automatic'].setChecked(True)
        vbox.addWidget(QLabel(text='Control mode'))
        for button in self.buttons:
            vbox.addWidget(self.buttons[button])

        vbox.setSpacing(5)
        self.setLayout(vbox)

    @staticmethod
    def dispaly_value(*args, **kwargs):
        print(args, kwargs)


class ElchDeviceMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key) for key in ['Controller', 'Sensor']}
        self.device_menus = {key: QComboBox() for key in self.labels}
        self.port_menus = {key: QComboBox() for key in self.labels}
        self.connect_buttons = {key: QPushButton(text='Connect', objectName=key) for key in self.labels}

        vbox = QVBoxLayout()
        for key in self.labels:
            vbox.addWidget(self.labels[key])
            vbox.addWidget(self.device_menus[key])
            vbox.addWidget(self.port_menus[key])
            vbox.addWidget(self.connect_buttons[key])
            vbox.addStretch(5)
        self.setLayout(vbox)

        self.populate_menus(['Eurotherm3216']*4, ['Thermolino6']*4)

    def populate_menus(self, controllers, sensors):
        """Populate the controller and sensor menus with lists of device names"""
        self.device_menus['Controller'].addItems(controllers)
        self.device_menus['Sensor'].addItems(sensors)


class ElchPidMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parameters = {'P1': 'Proportional 1', 'I1': 'Integral 1 (s)', 'D1': 'Derivative 1 (s)',
                      'P2': 'Proportional 2', 'I2': 'Integral 2 (s)', 'D2': 'Derivative 2 (s)',
                      'P3': 'Proportional 3', 'I3': 'Integral 3 (s)', 'D3': 'Derivative 3 (s)',
                      'GS': 'Gain scheduling', 'B12': 'Boundary 1/2', 'B23': 'Boundary 2/3'}

        self.labels = {key: QLabel(text=parameters[key]) for key in parameters}
        self.entries = {key: QComboBox() if key == 'GS' else QDoubleSpinBox() for key in parameters}

        grid = QFormLayout()
        grid.setSpacing(5)
        grid.setContentsMargins(0, 0, 0, 0)
        for key in parameters:
            grid.addRow(parameters[key], self.entries[key])

        self.setLayout(grid)