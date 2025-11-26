from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QToolButton

from src.Signals import engine_signals


class ElchNotificationBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._messages = []
        self._current_index = -1

        self._label = QLabel("")
        self._label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self._btn_up = QToolButton()
        self._btn_up.setObjectName('up')
        self._btn_down = QToolButton()
        self._btn_down.setObjectName('down')
        self._btn_clear = QToolButton()
        self._btn_clear.setObjectName('clear')

        self._btn_up.clicked.connect(self.show_previous)
        self._btn_down.clicked.connect(self.show_next)
        self._btn_clear.clicked.connect(self.clear_history)

        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        layout.addWidget(self._btn_up)
        layout.addWidget(self._btn_down)
        layout.addWidget(self._label, 1)
        layout.addWidget(self._btn_clear)

        self.setLayout(layout)

        self.engine_signals = engine_signals
        self.engine_signals.controller_connected.connect(self.display_controller_connected)
        self.engine_signals.controller_disconnected.connect(self.display_controller_disconnected)
        self.engine_signals.sensor_connected.connect(self.display_sensor_connected)
        self.engine_signals.sensor_disconnected.connect(self.display_sensor_disconnected)
        self.engine_signals.connection_failed.connect(self.display_connection_fail)
        self.engine_signals.ramp_segment_started.connect(self.display_ramp_started)
        self.engine_signals.hold_segment_started.connect(self.display_hold_started)
        self.engine_signals.message.connect(self.display_message)
        self.engine_signals.error.connect(self.display_message)

        self.engine_signals.com_failed.connect(self.display_message)
        self.engine_signals.non_imp.connect(self.display_message)

    def display_message(self, text: str):
        text = f"{datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")} - {text}"
        self._messages.append(text)
        self._current_index = len(self._messages) - 1
        self._show_current()

    def _show_current(self):
        if 0 <= self._current_index < len(self._messages):
            self._label.setText(self._messages[self._current_index])
        else:
            self._label.setText("")

    def show_previous(self):
        if not self._messages:
            return
        self._current_index = max(0, self._current_index - 1)
        self._show_current()

    def show_next(self):
        if not self._messages:
            return
        self._current_index = min(len(self._messages) - 1,
                                  self._current_index + 1)
        self._show_current()

    def clear_history(self):
        self._messages.clear()
        self._current_index = -1
        self._label.clear()

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

    def display_ramp_started(self, segment):
        self.display_message(f'Ramp segment {segment} started!')

    def display_hold_started(self, segment):
        self.display_message(f'Hold segment {segment} started!')
