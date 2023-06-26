import pubsub.pub
from PySide2.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QRadioButton, QVBoxLayout, QPushButton, QHBoxLayout, QGridLayout, QButtonGroup

from Signals import engine_signals




class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget
from PySide2.QtGui import QPalette, QColor





class ElchProgramMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Refactor to use gridlayout
        self.labels = {key: QLabel(text=key) for key in ['Rate', 'Setpoint', 'Hold']}
        self.entries = {segment: {'Rate': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=120),
                                  'Setpoint': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=1200),
                                  'Hold': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=100)
                                  } for segment in range(1, 11)}

        self.radios = {key: [QRadioButton(), QRadioButton()] for key in self.entries}

        radiogroup = QButtonGroup()
        radiogroup.setExclusive(True)
        for segment, radio in self.radios.items():
            radiogroup.addButton(radio[0])
            radiogroup.addButton(radio[1])
            radio[0].setEnabled(False)
            radio[1].setEnabled(False)

        engine_signals.ramp_segment_started.connect(self.mark_ramp_segment)
        engine_signals.hold_segment_started.connect(self.mark_hold_segment)

        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(self.labels['Rate'], 0, 1)
        grid.addWidget(self.labels['Setpoint'], 0, 2)
        grid.addWidget(self.labels['Hold'], 0, 3)

        for segment, seg_dict in self.entries.items():
            grid.addWidget(self.radios[segment][0], segment, 0)
            grid.addWidget(seg_dict['Rate'], segment, 1)
            grid.addWidget(seg_dict['Setpoint'], segment, 2)
            grid.addWidget(seg_dict['Hold'], segment, 3)
            grid.addWidget(self.radios[segment][1], segment, 4)

        self.start_button = QPushButton(text='Start', objectName='Start')
        self.start_button.setCheckable(True)
        self.start_button.toggled.connect(self.start_programm)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)

        vbox.addLayout(grid)
        vbox.addSpacing(10)
        vbox.addWidget(self.start_button)
        vbox.addStretch()

        self.setLayout(vbox)

    def start_programm(self):
        if self.start_button.isChecked():
            program = {segment: {parameter: entry.value() for parameter, entry in seg_dict.items()}
                       for segment, seg_dict in self.entries.items()}

            pubsub.pub.sendMessage(topicName='gui.set.start_program', program=program)
        else:
            print('STOP!!!')
            #TODO: Implement stop message to engine

    def mark_ramp_segment(self, segment):
        self.radios[segment][0].setChecked(True)

    def mark_hold_segment(self, segment):
        self.radios[segment][1].setChecked(True)
