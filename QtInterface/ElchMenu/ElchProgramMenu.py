import pubsub.pub
from PySide2.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QRadioButton, QVBoxLayout, QPushButton, QHBoxLayout, QGridLayout, QButtonGroup

from Signals import engine_signals


class ElchProgramMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Refactor to use gridlayout
        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Rate', 'Setpoint', 'Hold']}
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

        self.buttons = {key: QPushButton(text=key, objectName=key) for key in ['Start', 'Stop']}
        self.buttons['Start'].clicked.connect(self.start_programm)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)

        hbox_header = QHBoxLayout()
        for label in self.labels.values():
            hbox_header.addWidget(label)
            hbox_header.addStretch(1)
        vbox.addLayout(hbox_header)
        vbox.addSpacing(10)

        for segment, seg_dict in self.entries.items():
            line_box = QHBoxLayout()
            line_box.addWidget(self.radios[segment][0])
            line_box.addSpacing(5)
            line_box.addWidget(seg_dict.get('Rate'))
            line_box.addSpacing(5)
            line_box.addWidget(seg_dict.get('Setpoint'))
            line_box.addSpacing(5)
            line_box.addWidget(seg_dict.get('Hold'))
            line_box.addSpacing(5)
            line_box.addWidget(self.radios[segment][1])
            vbox.addLayout(line_box)
            vbox.addSpacing(10)

        vbox.addSpacing(20)

        for button in self.buttons.values():
            vbox.addWidget(button)
            vbox.addSpacing(10)

        vbox.addStretch()
        self.setLayout(vbox)

    def start_programm(self):
        program = {segment: {parameter: entry.value() for parameter, entry in seg_dict.items()}
                   for segment, seg_dict in self.entries.items()}

        pubsub.pub.sendMessage(topicName='gui.set.start_program', program=program)

    def mark_ramp_segment(self, segment):
        self.radios[segment][0].setChecked(True)

    def mark_hold_segment(self, segment):
        self.radios[segment][1].setChecked(True)
