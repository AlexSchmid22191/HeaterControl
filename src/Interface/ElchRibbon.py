from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QPushButton, QButtonGroup, QLabel, QVBoxLayout
from src.Signals import gui_signals


class ElchRibbon(QWidget):
    def __init__(self, menus=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.menus = menus if menus is not None else ['Devices', 'Control', 'Setpoints', 'PID', 'Plotting', 'Logging']
        self.menu_buttons = {key: QPushButton(parent=self) for key in self.menus}
        self.menu_buttons.update({'Kill': QPushButton(parent=self)})
        for key, button in self.menu_buttons.items():
            button.setObjectName(key)
        self.buttongroup = QButtonGroup()
        elchi_icon = QLabel()
        elchi_icon.setPixmap(QPixmap('Icons/ElchiHead.png'))

        vbox = QVBoxLayout()
        vbox.addWidget(elchi_icon, alignment=Qt.AlignHCenter)
        for key in self.menu_buttons:
            vbox.addWidget(self.menu_buttons[key])
            if key != 'Kill':
                self.buttongroup.addButton(self.menu_buttons[key])
                self.menu_buttons[key].setCheckable(True)
            self.menu_buttons[key].setFixedSize(150, 100)

        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.setMinimumWidth(150)
        self.setLayout(vbox)

        self.menu_buttons['Kill'].clicked.connect(gui_signals.emergency_shutdown.emit)
