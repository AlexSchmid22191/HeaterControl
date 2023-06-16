import functools

import pubsub.pub
from PySide2.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QRadioButton, QVBoxLayout, QPushButton, QHBoxLayout, QGridLayout


class ElchProgramMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Refactor to use gridlayout
        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Rate', 'Setpoint', 'Hold']}
        self.entries = {segment: {'Rate': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=120, ),
                                  'Setpoint': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=120, ),
                                  'Hold': QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=120, )
                                  } for segment in range(1, 11)}
        self.buttons = {key: QPushButton(text=key, objectName=key) for key in ['Start', 'Stop']}

        self.buttons['Start'].clicked.connect(self.start_programm)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)

        hbox_header = QHBoxLayout()
        for label in self.labels.values():
            hbox_header.addWidget(label)
        vbox.addLayout(hbox_header)
        vbox.addSpacing(10)

        for segment, seg_dict in self.entries.items():
            line_box = QHBoxLayout()
            line_box.addWidget(seg_dict.get('Rate'))
            line_box.addSpacing(5)
            line_box.addWidget(seg_dict.get('Setpoint'))
            line_box.addSpacing(5)
            line_box.addWidget(seg_dict.get('Hold'))
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



    # @staticmethod
    # def set_control_value(value, control):
    #     {
    #         'Rate': functools.partial(pubsub.pub.sendMessage, 'gui.set.rate', rate=value),
    #         'Power': functools.partial(pubsub.pub.sendMessage, 'gui.set.power', power=value),
    #         'Setpoint': functools.partial(pubsub.pub.sendMessage, 'gui.set.setpoint', setpoint=value)
    #     }[control]()
    #
    # @staticmethod
    # def set_control_mode(checked, mode):
    #     if checked:
    #         pubsub.pub.sendMessage('gui.set.control_mode', mode=mode)
    #
    # def change_units(self, mode):
    #     self.entries['Setpoint'].setSuffix({'Temperature': ' \u00B0C', 'Voltage': ' mV'}[mode])
    #     self.entries['Rate'].setSuffix({'Temperature': ' \u00B0C/min', 'Voltage': ' mV/min'}[mode])
    #
    # def update_control_values(self, control_parameters):
    #     assert isinstance(control_parameters, dict), 'Illegal type recieved: {:s}'.format(str(type(control_parameters)))
    #     for key in control_parameters:
    #         assert key in self.entries or key == 'Mode', 'Illegal key recieved: {:s}'.format(key)
    #         if key == 'Mode':
    #             self.buttons[control_parameters[key]].blockSignals(True)
    #             self.buttons[control_parameters[key]].setChecked(True)
    #             self.buttons[control_parameters[key]].blockSignals(False)
    #         else:
    #             self.entries[key].blockSignals(True)
    #             self.entries[key].setValue(control_parameters[key])
    #             self.entries[key].blockSignals(False)
