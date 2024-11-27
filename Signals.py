from PySide6.QtCore import QObject, Signal


class GuiSignals(QObject):
    request_ports = Signal()
    connect_device = Signal(str)
    disconnect_device = Signal()
    enable_output = Signal(bool)
    toggle_aiming = Signal(bool)


class EngineSignals(QObject):
    available_ports = Signal(dict)

    controller_connected = Signal((str, str))
    controller_disconnected = Signal()
    sensor_connected = Signal((str, str))
    sensor_disconnected = Signal()
    connection_failed = Signal()

    ramp_segment_started = Signal(int)
    hold_segment_started = Signal(int)


gui_signals = GuiSignals()
engine_signals = EngineSignals()
