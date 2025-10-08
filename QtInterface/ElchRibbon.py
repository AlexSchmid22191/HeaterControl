from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QPushButton, QButtonGroup, QLabel, QVBoxLayout


class ElchRibbon(QWidget):
    def __init__(self, menus=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.menus = menus if menus is not None else ['Devices', 'Control', 'Setpoints', 'PID', 'Plotting', 'Logging']
        self.menu_buttons = {key: QPushButton(parent=self, objectName=key) for key in self.menus}
        self.buttongroup = QButtonGroup()
        elchicon = QLabel()
        elchicon.setPixmap(QPixmap('Icons/ElchiHead.png'))

        vbox = QVBoxLayout()
        vbox.addWidget(elchicon, alignment=Qt.AlignHCenter)
        for key in self.menus:
            vbox.addWidget(self.menu_buttons[key])
            self.buttongroup.addButton(self.menu_buttons[key])
            self.menu_buttons[key].setCheckable(True)
            self.menu_buttons[key].setFixedSize(150, 100)

        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.setMinimumWidth(150)
        self.setLayout(vbox)
