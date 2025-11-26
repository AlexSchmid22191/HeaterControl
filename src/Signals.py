from PySide6.QtCore import QObject, Signal


class GuiSignals(QObject):
    request_ports = Signal()
    request_sensors = Signal()
    request_controllers = Signal()
    set_units = Signal(str)
    connect_sensor = Signal(str, str)
    disconnect_sensor = Signal()
    connect_controller = Signal(str, str)
    disconnect_controller = Signal()

    set_target_setpoint = Signal(float)
    set_rate = Signal(float)
    set_manual_output_power = Signal(float)
    set_control_mode = Signal(str)
    enable_output = Signal(bool)
    toggle_aiming = Signal(bool)
    refresh_parameters = Signal()
    refresh_pid = Signal()
    set_pid_parameters = Signal(str, str)

    start_log = Signal()
    stop_log = Signal()
    clear_log = Signal()
    export_log = Signal()

    start_program = Signal(object)
    skip_program = Signal()
    stop_program = Signal()

    get_calibration_data = Signal()
    get_resistive_heater_config = Signal()
    set_resistive_heater_config = Signal(dict)

    set_external_pv_mode = Signal(bool)


class EngineSignals(QObject):
    available_ports = Signal(dict)
    available_devices = Signal(dict)

    controller_connected = Signal(str, str)
    controller_disconnected = Signal()
    sensor_connected = Signal(str, str)
    sensor_disconnected = Signal()
    connection_failed = Signal(Exception)

    ramp_segment_started = Signal(int)
    hold_segment_started = Signal(int)

    controller_status_update = Signal(dict, float)
    controller_parameters_update = Signal(dict)
    sensor_status_update = Signal(dict, float)
    pid_parameters_update = Signal(dict)
    calibration_data_update = Signal(dict)
    resistive_heater_config_update = Signal(dict)

    error = Signal(str)
    message = Signal(str)

    com_failed = Signal(str)
    non_imp = Signal(str)


gui_signals = GuiSignals()
engine_signals = EngineSignals()
