import pubsub.pub
from PySide2.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QRadioButton, QVBoxLayout, QPushButton, QGridLayout, \
    QButtonGroup

from src.Signals import engine_signals


class ElchProgramMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {'Rate': QLabel(text='Rate\n(\u00B0C/min)'),
                       'Setpoint': QLabel(text='Setpoint\n(\u00B0C)'),
                       'Hold': QLabel(text='Hold\n(min)')}
        self.entries = {segment: {'Rate': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=120, value=5),
                                  'Setpoint': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=1200),
                                  'Hold': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=10000)
                                  } for segment in range(1, 11)}

        self.radios = {key: {'ramp': QRadioButton(), 'hold': QRadioButton()} for key in self.entries}

        radiogroup = QButtonGroup()
        radiogroup.setExclusive(True)
        for segment, radio in self.radios.items():
            for radiobutton in radio.values():
                radiogroup.addButton(radiobutton)
                radiobutton.setEnabled(False)

        engine_signals.ramp_segment_started.connect(self.mark_ramp_segment)
        engine_signals.hold_segment_started.connect(self.mark_hold_segment)

        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(self.labels['Rate'], 0, 1)
        grid.addWidget(self.labels['Setpoint'], 0, 2)
        grid.addWidget(self.labels['Hold'], 0, 3)

        for segment, seg_dict in self.entries.items():
            grid.addWidget(self.radios[segment]['ramp'], segment, 0)
            grid.addWidget(seg_dict['Rate'], segment, 1)
            grid.addWidget(seg_dict['Setpoint'], segment, 2)
            grid.addWidget(seg_dict['Hold'], segment, 3)
            grid.addWidget(self.radios[segment]['hold'], segment, 4)

        self.start_button = QPushButton(text='Start', objectName='Start')
        self.start_button.setCheckable(True)
        self.start_button.toggled.connect(self.start_programm)

        self.skip_button = QPushButton(text='Skip segment')
        self.skip_button.clicked.connect(self.skip_segment)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)

        vbox.addWidget(QLabel(text='Setpoint Programmer', objectName='Header'))
        vbox.addSpacing(10)
        vbox.addLayout(grid)
        vbox.addSpacing(10)
        vbox.addWidget(self.start_button)
        vbox.addSpacing(5)
        vbox.addWidget(self.skip_button)
        vbox.addStretch()

        self.setLayout(vbox)

    def start_programm(self):
        if self.start_button.isChecked():
            program = {segment: {parameter: entry.value() for parameter, entry in seg_dict.items()}
                       for segment, seg_dict in self.entries.items()}

            pubsub.pub.sendMessage(topicName='gui.set.start_program', program=program)
        else:
            pubsub.pub.sendMessage(topicName='gui.set.stop_program')

    def mark_ramp_segment(self, segment):
        self.radios[segment]['ramp'].setChecked(True)

    def mark_hold_segment(self, segment):
        self.radios[segment]['hold'].setChecked(True)

    def change_units(self, mode):
        self.labels['Rate'].setText({'Temperature': 'Rate\n(\u00B0C/min)', 'Voltage': 'Rate\n(mV/min)'}[mode])
        self.labels['Setpoint'].setText({'Temperature': 'Setpoint\n(\u00B0C)', 'Voltage': 'Setpoint\n(mV)'}[mode])

    @staticmethod
    def skip_segment():
        pubsub.pub.sendMessage(topicName='gui.set.skip_program')
