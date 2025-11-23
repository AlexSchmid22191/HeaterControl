import functools

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout

from src.Interface.ElchMenu.ElchControlMenu import ElchControlMenu
from src.Interface.ElchMenu.ElchDeviceMenu import ElchDeviceMenu
from src.Interface.ElchMenu.ElchPlotMenu import ElchPlotMenu
from src.Interface.ElchMenu.ElchPidMenu import ElchPidMenu
from src.Interface.ElchMenu.ElchProgramMenu import ElchProgramMenu


class ElchMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(260)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.menus = {'Devices': ElchDeviceMenu(), 'Control': ElchControlMenu(), 'Plotting': ElchPlotMenu(),
                      'PID': ElchPidMenu(), 'Programmer': ElchProgramMenu()}

        vbox = QVBoxLayout()
        for menu in self.menus:
            self.menus[menu].setVisible(False)
            vbox.addWidget(self.menus[menu])
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

        for key, button in self.menus['Devices'].unit_buttons.items():
            button.clicked.connect(functools.partial(self.menus['Control'].change_units, key))
            button.clicked.connect(functools.partial(self.menus['PID'].set_unit, key))

    def adjust_visibility(self, button, visibility):
        menu = button.objectName()
        self.menus[menu].setVisible(visibility)
