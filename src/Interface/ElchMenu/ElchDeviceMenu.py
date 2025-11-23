import functools

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QButtonGroup, QRadioButton, QVBoxLayout

from src.Signals import gui_signals, engine_signals


class ElchDeviceMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Controller', 'Sensor']}
        self.device_menus = {key: QComboBox() for key in self.labels}
        self.port_menus = {key: QComboBox() for key in self.labels}
        self.connect_buttons = {key: QPushButton(text='Connect', objectName=key) for key in self.labels}

        self.buttongroup = QButtonGroup()
        self.buttongroup.setExclusive(False)
        self.buttongroup.buttonToggled.connect(self.connect_device)

        self.unit_buttons = {key: QRadioButton(text=key) for key in ['Temperature', 'Voltage']}
        self.refresh_button = QPushButton(text='Refresh Serial', objectName='Refresh')

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)

        vbox.addWidget(QLabel(text='Process Variable', objectName='Header'))
        for key, button in self.unit_buttons.items():
            vbox.addWidget(button)
            button.toggled.connect(functools.partial(self.set_measurement_unit, unit=key))
        vbox.addSpacing(20)

        for key in self.labels:
            self.buttongroup.addButton(self.connect_buttons[key])
            self.connect_buttons[key].setCheckable(True)
            vbox.addWidget(self.labels[key])
            vbox.addWidget(self.device_menus[key])
            vbox.addWidget(self.port_menus[key])
            vbox.addWidget(self.connect_buttons[key])
            vbox.addSpacing(20)

        vbox.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(gui_signals.request_ports.emit)
        vbox.addStretch()
        self.setLayout(vbox)

        engine_signals.available_ports.connect(self.update_ports)
        engine_signals.available_devices.connect(self.update_devices)
        gui_signals.request_ports.emit()

    def update_ports(self, ports):
        """Populate the controller and sensor menus with lists of device names and ports"""
        for key, menu in self.port_menus.items():
            menu.clear()
            menu.addItems(ports)
            for port, description in ports.items():
                index = menu.findText(port)
                menu.setItemData(index, description, Qt.ToolTipRole)

    def update_devices(self, devices):
        for key in self.device_menus:
            self.device_menus[key].clear()
            self.device_menus[key].addItems(devices[key])

    def connect_device(self, source, state):
        key = source.objectName()
        port = self.port_menus[key].currentText()
        device = self.device_menus[key].currentText()

        if state:
            if key == 'Controller':
                gui_signals.connect_controller.emit(device, port)
            elif key == 'Sensor':
                gui_signals.connect_sensor.emit(device, port)
        else:
            if key == 'Controller':
                gui_signals.disconnect_controller.emit()
            elif key == 'Sensor':
                gui_signals.disconnect_sensor.emit()

    @staticmethod
    def set_measurement_unit(checked, unit):
        if checked:
            gui_signals.set_units.emit(unit)
