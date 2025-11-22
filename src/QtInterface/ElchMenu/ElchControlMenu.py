import functools

import matplotlib.font_manager as fm
import matplotlib.style
import matplotlib.ticker
import pubsub.pub
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QRadioButton, QVBoxLayout, QPushButton, QDialog, \
    QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from src.Signals import gui_signals


class ElchControlMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Setpoint', 'Rate', 'Power']}
        self.entries = {key: QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=10000) for key in self.labels}
        self.entries['Power'].setMaximum(100)
        self.entries['Power'].setSuffix(' %')
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
        vbox.addSpacing(10)

        enable_button = QPushButton(text='Output Enable', objectName='Enable')
        enable_button.setCheckable(True)
        enable_button.clicked.connect(lambda: gui_signals.enable_output.emit(enable_button.isChecked()))
        aiming_beam_button = QPushButton(text='Aiming Beam', objectName='Enable')
        aiming_beam_button.setCheckable(True)
        aiming_beam_button.clicked.connect(lambda: gui_signals.toggle_aiming.emit(aiming_beam_button.isChecked()))
        vbox.addWidget(enable_button)
        vbox.addWidget(aiming_beam_button)

        vbox.addSpacing(10)

        res_conf_button = QPushButton(text='Resistive Heater Config', objectName='Config')
        res_conf_button.clicked.connect(self.resistive_heater_config)
        vbox.addWidget(res_conf_button)

        vbox.addStretch()
        self.setLayout(vbox)

        pubsub.pub.subscribe(self.update_control_values, 'engine.answer.control_parameters')

    @staticmethod
    def set_control_value(value, control):
        {
            'Rate': functools.partial(pubsub.pub.sendMessage, 'gui.set.rate', rate=value),
            'Power': functools.partial(pubsub.pub.sendMessage, 'gui.set.power', power=value),
            'Setpoint': functools.partial(pubsub.pub.sendMessage, 'gui.set.setpoint', setpoint=value)
        }[control]()

    @staticmethod
    def set_control_mode(checked, mode):
        if checked:
            pubsub.pub.sendMessage('gui.set.control_mode', mode=mode)

    def change_units(self, mode):
        self.entries['Setpoint'].setSuffix({'Temperature': ' \u00B0C', 'Voltage': ' mV'}[mode])
        self.entries['Rate'].setSuffix({'Temperature': ' \u00B0C/min', 'Voltage': ' mV/min'}[mode])

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
        vbox.addWidget(QLabel('Resistive heater configuration', objectName='Header'), alignment=Qt.AlignHCenter)
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

        pubsub.pub.subscribe(self.update_params, 'engine.answer.resistive_heater_config')
        pubsub.pub.subscribe(self.dispaly_calibration_results, 'engine.answer.calibration')
        pubsub.pub.sendMessage('gui.request.resistive_heater_config')

        vbox.addLayout(g_box)
        vbox.addWidget(button3 := QPushButton('Calibrate'))
        button3.clicked.connect(functools.partial(pubsub.pub.sendMessage, topicName='gui.request.calibration'))
        vbox.addWidget(button := QPushButton('Save config'))
        button.clicked.connect(self.save_config)
        vbox.addWidget(button2 := QPushButton('Close'))
        button2.clicked.connect(self.close)

        self.setLayout(vbox)

    def save_config(self):
        pubsub.pub.sendMessage('gui.set.resistive_heater_config',
                               parameters={_field: _spin_box.value() for (_field, _spin_box) in self.boxes.items()})
        self.close()

    def update_params(self, parameters):
        for key, value in parameters.items():
            self.boxes[key].setValue(float(value))

    def dispaly_calibration_results(self, calibration_data):
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
            vbox.addWidget(QLabel('Calibration failed!\n Check if the circuit is clsoed\n and the output is enabled.',
                                  objectName='Header'), alignment=Qt.AlignHCenter)
            vbox.addWidget(button2 := QPushButton('Close'))
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
            vbox.addWidget(QLabel('Calibration results', objectName='Header'), alignment=Qt.AlignHCenter)
            vbox.addSpacing(20)
            vbox.addWidget(plot)
            g_box = QGridLayout()
            g_box.addWidget(QLabel('Cold resistance'), 0, 0)
            g_box.addWidget(QLabel(f'{data["R"]:.3f} Ohm'), 0, 1)
            g_box.addWidget(QLabel('Intercept'), 1, 0)
            g_box.addWidget(QLabel(f'{data["OS"]:.3f} V'), 1, 1)
            g_box.addWidget(QLabel('Correlation Coeff.'), 2, 0)
            g_box.addWidget(QLabel(f'{data["R2"]:.3f}'), 2, 1)
            vbox.addLayout(g_box)

            vbox.addSpacing(20)
            vbox.addWidget(button := QPushButton('Accept calibration'))
            button.clicked.connect(self.accept)
            vbox.addWidget(button2 := QPushButton('Discard calibration'))
            button2.clicked.connect(self.reject)

            self.setLayout(vbox)
