from PySide6.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QRadioButton, QVBoxLayout, QPushButton, QGridLayout, \
    QButtonGroup

from src.Signals import engine_signals, gui_signals


class ElchProgramMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        engine_signals.ramp_segment_started.connect(self.mark_ramp_segment)
        engine_signals.hold_segment_started.connect(self.mark_hold_segment)

        self.labels = {'Rate': QLabel(text='Rate\n(\u00B0C/min)'),
                       'Setpoint': QLabel(text='Setpoint\n(\u00B0C)'),
                       'Hold': QLabel(text='Hold\n(min)')}

        self.entries = {segment: self.make_entry_row() for segment in range(1, 3)}
        self.radios = {key: {'ramp': QRadioButton(), 'hold': QRadioButton()} for key in self.entries}

        radiogroup = QButtonGroup()
        radiogroup.setExclusive(True)
        for segment, radio in self.radios.items():
            for radiobutton in radio.values():
                radiogroup.addButton(radiobutton)
                radiobutton.setEnabled(False)

        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        self.grid.addWidget(self.labels['Rate'], 0, 1)
        self.grid.addWidget(self.labels['Setpoint'], 0, 2)
        self.grid.addWidget(self.labels['Hold'], 0, 3)

        for segment, seg_dict in self.entries.items():
            self.grid.addWidget(self.radios[segment]['ramp'], segment, 0)
            self.grid.addWidget(seg_dict['Rate'], segment, 1)
            self.grid.addWidget(seg_dict['Setpoint'], segment, 2)
            self.grid.addWidget(seg_dict['Hold'], segment, 3)
            self.grid.addWidget(self.radios[segment]['hold'], segment, 4)

        self.add_button = QPushButton('Add row')
        self.add_button.clicked.connect(self.add_row)
        self.remove_button = QPushButton('Remove row')
        self.remove_button.clicked.connect(self.remove_row)

        self.start_button = QPushButton('Start')
        self.start_button.setObjectName('Start')
        self.start_button.setCheckable(True)
        self.start_button.toggled.connect(self.start_program)

        self.skip_button = QPushButton('Skip segment')
        self.skip_button.clicked.connect(self.skip_segment)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)

        vbox.addWidget(l := QLabel(text='Setpoint Programmer'))
        l.setObjectName('Header')
        vbox.addSpacing(10)
        vbox.addLayout(self.grid)
        vbox.addStretch(1)
        vbox.addSpacing(5)
        vbox.addWidget(self.add_button)
        vbox.addSpacing(5)
        vbox.addWidget(self.remove_button)
        vbox.addSpacing(10)
        vbox.addWidget(self.start_button)
        vbox.addSpacing(5)
        vbox.addWidget(self.skip_button)
        vbox.addStretch()

        self.setLayout(vbox)

    def add_row(self):
        n_row = max(self.entries.keys()) + 1
        self.entries.update({n_row: self.make_entry_row()})
        self.radios.update({n_row: {'ramp': QRadioButton(), 'hold': QRadioButton()}})
        self.grid.addWidget(self.radios[n_row]['ramp'], n_row, 0)
        self.grid.addWidget(self.entries[n_row]['Rate'], n_row, 1)
        self.grid.addWidget(self.entries[n_row]['Setpoint'], n_row, 2)
        self.grid.addWidget(self.entries[n_row]['Hold'], n_row, 3)
        self.grid.addWidget(self.radios[n_row]['hold'], n_row, 4)

    def remove_row(self):
        n_row = max(self.entries.keys())
        for widget in self.entries[n_row].values():
            self.grid.removeWidget(widget)
            widget.deleteLater()
        for widget in self.radios[n_row].values():
            self.grid.removeWidget(widget)
            widget.deleteLater()
        self.entries.pop(n_row)
        self.radios.pop(n_row)

    @staticmethod
    def make_entry_row():
        row = {'Rate': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=120, value=5),
               'Setpoint': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=1200),
               'Hold': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=10000)
               }
        return row

    def start_program(self):
        if self.start_button.isChecked():
            program = {segment: {parameter: entry.value() for parameter, entry in seg_dict.items()}
                       for segment, seg_dict in self.entries.items()}
            gui_signals.start_program.emit(program)
        else:
            gui_signals.stop_program.emit()

    def mark_ramp_segment(self, segment):
        self.radios[segment]['ramp'].setChecked(True)

    def mark_hold_segment(self, segment):
        self.radios[segment]['hold'].setChecked(True)

    def change_units(self, mode):
        self.labels['Rate'].setText({'Temperature': 'Rate\n(\u00B0C/min)', 'Voltage': 'Rate\n(mV/min)'}[mode])
        self.labels['Setpoint'].setText({'Temperature': 'Setpoint\n(\u00B0C)', 'Voltage': 'Setpoint\n(mV)'}[mode])

    @staticmethod
    def skip_segment():
        gui_signals.skip_program.emit()
