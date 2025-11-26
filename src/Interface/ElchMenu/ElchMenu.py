import functools

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedLayout

from src.Interface.ElchMenu.ElchControlMenu import ElchControlMenu
from src.Interface.ElchMenu.ElchDeviceMenu import ElchDeviceMenu
from src.Interface.ElchMenu.ElchPidMenu import ElchPidMenu
from src.Interface.ElchMenu.ElchPlotMenu import ElchPlotMenu
from src.Interface.ElchMenu.ElchProgramMenu import ElchProgramMenu


class ElchMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(260)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Create submenus
        self.menus = {
            'Devices': ElchDeviceMenu(parent=self),
            'Control': ElchControlMenu(parent=self),
            'Plotting': ElchPlotMenu(parent=self),
            'PID': ElchPidMenu(parent=self),
            'Programmer': ElchProgramMenu(parent=self)
        }

        self.stacked = QStackedLayout()
        self.stacked.setSpacing(0)
        self.stacked.setContentsMargins(0, 0, 0, 0)

        for widget in self.menus.values():
            self.stacked.addWidget(widget)

        self.setLayout(self.stacked)

    def adjust_visibility(self, button, visibility):
        menu = button.objectName()
        self.stacked.setCurrentWidget(self.menus[menu])
