import functools

import matplotlib.font_manager as fm
import matplotlib.style
import matplotlib.ticker
from PySide6.QtCore import Qt, QSignalBlocker, QTimer
from PySide6.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QVBoxLayout, QPushButton, QDialog, \
    QGridLayout, QFormLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from src.Signals import gui_signals, engine_signals


class ElchControlMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.timer = QTimer(interval=1000)
        self.timer.timeout.connect(gui_signals.refresh_parameters.emit)
        self.timer.start()

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)

        label = QLabel(text='Controller')
        label.setObjectName('Header')
        vbox.addWidget(label)

        self.labels = {'Setpoint': 'Target setpoint', 'Rate': 'Rate', 'Power': 'Manual power', 'Mode': 'Control mode',
                       'External_PV': 'Sensor as PV', 'Enable': 'Output Enable', 'Aiming': 'Aiming beam',
                       'controller_tc': 'Thermocouple', 'sensor_tc': 'Thermocouple',
                       'Sensor_Aiming': 'Aiming beam', 'res_config': 'Configure resistive heater'}

        self.entries = {key: QDoubleSpinBox() for key in ['Setpoint', 'Rate', 'Power']}
        for key, param in self.entries.items():
            param.setMaximum(1500)
            param.setMinimum(0)
            param.setSingleStep(1)
            param.setDecimals(1)

        self.entries['Setpoint'].setSuffix(' \u00B0C')
        self.entries['Rate'].setSuffix(' \u00B0C/min')

        self.entries['Power'].setMaximum(100)
        self.entries['Power'].setSuffix(' %')

        self.entries.update({key: QComboBox() for key in ['Mode', 'controller_tc', 'sensor_tc']})

        self.entries['Mode'].addItems(['Manual', 'Automatic'])
        self.entries['controller_tc'].addItems(['S', 'K', 'J', 'T', 'E', 'N', 'R', 'B'])
        self.entries['sensor_tc'].addItems(['S', 'K', 'J', 'T', 'E', 'N', 'R', 'B'])

        self.buttons = {key: QPushButton(text=self.labels[key]) for key in ['External_PV', 'Enable', 'Aiming',
                                                                            'Sensor_Aiming', 'res_config']}

        form = QFormLayout()
        form.setSpacing(5)
        form.setHorizontalSpacing(20)
        form.setContentsMargins(0, 0, 0, 0)

        for param in ['Setpoint', 'Rate', 'Power', 'Mode', 'controller_tc']:
            form.addRow(self.labels[param], self.entries[param])
            match param:
                case 'Mode':
                    self.entries[param].currentTextChanged.connect(gui_signals.set_control_mode.emit)
                case 'controller_tc':
                    self.entries[param].currentTextChanged.connect(gui_signals.set_heater_tc.emit)
                case 'Setpoint' | 'Rate' | 'Power':
                    self.entries[param].setKeyboardTracking(False)
                    # noinspection PyUnresolvedReferences
                    self.entries[param].valueChanged.connect(functools.partial(self.set_control_value, control=label))

        vbox.addLayout(form)
        vbox.addSpacing(20)

        for param in ['External_PV', 'Enable', 'Aiming', 'res_config']:
            vbox.addWidget(self.buttons[param])
            match param:
                case 'External_PV':
                    self.buttons[param].setCheckable(True)
                    self.buttons[param].clicked.connect(lambda state: gui_signals.set_external_pv_mode.emit(state))
                case 'Enable':
                    self.buttons[param].setCheckable(True)
                    self.buttons[param].clicked.connect(lambda state: gui_signals.enable_output.emit(state))
                case 'Aiming':
                    self.buttons[param].setCheckable(True)
                    self.buttons[param].clicked.connect(lambda state: gui_signals.toggle_aiming.emit(state))
                case 'res_config':
                    self.buttons[param].clicked.connect(self.resistive_heater_config)

        vbox.addLayout(form)
        vbox.addSpacing(20)

        label = QLabel(text='Sensor')
        label.setObjectName('Header')
        vbox.addWidget(label)

        form = QFormLayout()
        form.setSpacing(5)
        form.setHorizontalSpacing(20)
        form.setContentsMargins(0, 0, 0, 0)

        form.addRow(self.labels['sensor_tc'], self.entries['sensor_tc'])

        vbox.addLayout(form)

        vbox.addWidget(self.buttons['Sensor_Aiming'])
        self.buttons['Sensor_Aiming'].setCheckable(True)
        self.buttons['Sensor_Aiming'].clicked.connect(lambda state: gui_signals.switch_sensor_aiming_beam.emit(state))

        vbox.addStretch()
        self.setLayout(vbox)

        engine_signals.controller_parameters_update.connect(self.update_control_values)

    @staticmethod
    def set_control_value(value, control):
        match control:
            case 'Setpoint':
                gui_signals.set_target_setpoint.emit(value)
            case 'Rate':
                gui_signals.set_rate.emit(value)
            case 'Power':
                gui_signals.set_manual_output_power.emit(value)

    def change_units(self, mode):
        self.entries['Setpoint'].setSuffix({'Temperature': ' \u00B0C', 'Voltage': ' mV'}[mode])
        self.entries['Rate'].setSuffix({'Temperature': ' \u00B0C/min', 'Voltage': ' mV/min'}[mode])

    def update_control_values(self, control_parameters):
        assert isinstance(control_parameters, dict), 'Illegal type received: {:s}'.format(str(type(control_parameters)))
        for key in control_parameters:
            assert key in self.entries, 'Illegal key received: {:s}'.format(key)
            if key == 'Mode':
                with QSignalBlocker(self.entries[key]):
                    self.entries[key].setCurrentText(control_parameters[key])
            else:
                with QSignalBlocker(self.entries[key]):
                    self.entries[key].setValue(control_parameters[key])

    def resistive_heater_config(self):
        dlg = ResConfDialog(self)
        dlg.exec_()


class ResConfDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Resistive heater configuration')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_StyledBackground, True)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(10)
        vbox.addWidget(l := QLabel('Resistive heater configuration'), alignment=Qt.AlignHCenter)
        l.setObjectName('Header')
        vbox.addWidget(QLabel('Warning: Do not change any values here\nunless you know exactly what you are doing!'))

        g_box = QGridLayout()
        fields = ['cold resistance', 'maximum current', 'maximum voltage', 'minimum output']
        self.boxes = {}

        for i, field in enumerate(fields):
            g_box.addWidget(QLabel(field.title()), i, 0)
            spin_box = QDoubleSpinBox()
            spin_box.setRange(0.0, 100.0)
            g_box.addWidget(spin_box, i, 1)
            self.boxes.update({field: spin_box})

        engine_signals.resistive_heater_config_update.connect(self.update_params)
        engine_signals.calibration_data_update.connect(self.display_calibration_results)
        gui_signals.get_resistive_heater_config.emit()

        vbox.addLayout(g_box)
        vbox.addWidget(button3 := QPushButton('Calibrate'))
        # noinspection PyUnresolvedReferences
        button3.clicked.connect(gui_signals.get_calibration_data.emit)
        vbox.addWidget(button := QPushButton('Save config'))
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.save_config)
        vbox.addWidget(button2 := QPushButton('Close'))
        # noinspection PyUnresolvedReferences
        button2.clicked.connect(self.close)

        self.setLayout(vbox)

    def save_config(self):
        gui_signals.set_resistive_heater_config.emit({_field: _spin_box.value()
                                                      for (_field, _spin_box) in self.boxes.items()})
        self.close()

    def update_params(self, parameters):
        for key, value in parameters.items():
            self.boxes[key].setValue(float(value))

    def display_calibration_results(self, calibration_data):
        dlg = CalDialog(data=calibration_data, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            self.boxes['cold resistance'].setValue(calibration_data['R'])


class CalDialog(QDialog):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Calibration results')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("CalDialog")

        if data['State'] == 'Fail':
            vbox = QVBoxLayout()
            vbox.setContentsMargins(20, 20, 20, 20)
            vbox.setSpacing(10)
            vbox.addWidget(l := QLabel('Calibration failed!\nCheck if the circuit is closed\n'
                                       'and the output is enabled!'), alignment=Qt.AlignHCenter)
            l.setObjectName('Header')
            vbox.addWidget(button2 := QPushButton('Close'))
            # noinspection PyUnresolvedReferences
            button2.clicked.connect(self.reject)
            self.setLayout(vbox)
        else:
            plot = FigureCanvasQTAgg(Figure(figsize=(3, 3)))

            ax = plot.figure.subplots()

            line_x = [0, max(data['I'])]
            line_y = [i * data['R'] + data['OS'] for i in line_x]

            ax.plot(data['I'], data['U'], marker='o', ls='None', color='#86f8ab')
            ax.plot(line_x, line_y, marker='None', ls='-', color='#86b3f9')

            ax.set_xlabel('Current (A)', fontproperties=fm.FontProperties(fname='Fonts/Roboto-Regular.ttf', size=11))
            ax.set_ylabel('Voltage (V)', fontproperties=fm.FontProperties(fname='Fonts/Roboto-Regular.ttf', size=11))
            ax.xaxis.set_major_locator(matplotlib.ticker.AutoLocator())
            ax.yaxis.set_major_locator(matplotlib.ticker.AutoLocator())
            ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

            plot.autoscale = True
            plot.figure.tight_layout()

            vbox = QVBoxLayout()
            vbox.setContentsMargins(20, 20, 20, 20)
            vbox.setSpacing(10)
            vbox.addWidget(l := QLabel('Calibration results'), alignment=Qt.AlignHCenter)
            l.setObjectName('Header')
            vbox.addSpacing(20)
            vbox.addWidget(plot)
            g_box = QGridLayout()
            g_box.addWidget(QLabel('Cold resistance'), 0, 0)
            g_box.addWidget(QLabel(f'{data["R"]:.3f} Ohm'), 0, 1)
            g_box.addWidget(QLabel('Intercept'), 1, 0)
            g_box.addWidget(QLabel(f'{data["OS"]:.3f} V'), 1, 1)
            g_box.addWidget(QLabel('Correlation Coef.'), 2, 0)
            g_box.addWidget(QLabel(f'{data["R2"]:.3f}'), 2, 1)
            vbox.addLayout(g_box)

            vbox.addSpacing(20)
            vbox.addWidget(button := QPushButton('Accept calibration'))
            # noinspection PyUnresolvedReferences
            button.clicked.connect(self.accept)
            vbox.addWidget(button2 := QPushButton('Discard calibration'))
            # noinspection PyUnresolvedReferences
            button2.clicked.connect(self.reject)

            self.setLayout(vbox)
