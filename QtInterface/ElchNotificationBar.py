from PySide2.QtCore import Qt, QTimer
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout
from Signals import engine_signals


class ElchNotificationBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.label = QLabel('', parent=self)
        self.engine_signals = engine_signals
        self.engine_signals.controller_connected.connect(self.display_controller_connected)
        self.engine_signals.controller_disconnected.connect(self.display_controller_disconnected)
        self.engine_signals.sensor_connected.connect(self.display_sensor_connected)
        self.engine_signals.sensor_disconnected.connect(self.display_sensor_disconnected)
        self.engine_signals.connection_failed.connect(self.display_connection_fail)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        self.setLayout(hbox)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clear_message)

    def display_message(self, message: str):
        self.label.setText(message)
        self.timer.start(5000)

    def clear_message(self):
        self.label.setText('')

    def display_controller_connected(self, device, port):
        self.display_message(f'Controller {device} connected at port {port}!')

    def display_controller_disconnected(self):
        self.display_message('Controller disconnected!')

    def display_sensor_connected(self, device, port):
        self.display_message(f'Sensor {device} connected at port {port}!')

    def display_sensor_disconnected(self):
        self.display_message('Sensor disconnected!')

    def display_connection_fail(self):
        self.display_message('Connection failed!')