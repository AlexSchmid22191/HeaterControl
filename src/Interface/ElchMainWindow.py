import functools

from PySide2.QtCore import Qt
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizeGrip

from src.Interface.ElchMenu.ElchMenu import ElchMenu
from src.Interface.ElchPlot import ElchPlot
from src.Interface.ElchRibbon import ElchRibbon
from src.Interface.ElchTitleBar import ElchTitlebar
from src.Interface.ElchiStatusBar import ElchStatusBar
from src.Interface.ElchNotificationBar import ElchNotificationBar


class ElchMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.FramelessWindowHint)

        QFontDatabase.addApplicationFont('Fonts/Roboto-Light.ttf')
        QFontDatabase.addApplicationFont('Fonts/Roboto-Regular.ttf')

        with open('Styles/window_style.qss') as style_file:
            self.setStyleSheet(style_file.read())

        self.controlmenu = ElchMenu()
        self.ribbon = ElchRibbon(menus=self.controlmenu.menus)
        self.matplotframe = ElchPlot()
        self.titlebar = ElchTitlebar()
        self.statusbar = ElchStatusBar()
        self.notificbar = ElchNotificationBar()

        panel_spacing = 20

        vbox_innermost = QVBoxLayout()
        vbox_innermost.addWidget(self.matplotframe, stretch=1)
        vbox_innermost.addWidget(self.notificbar, stretch=0)

        hbox_inner = QHBoxLayout()
        hbox_inner.addLayout(vbox_innermost)
        hbox_inner.addWidget(self.controlmenu, stretch=0)
        hbox_inner.setSpacing(panel_spacing)
        hbox_inner.setContentsMargins(0, 0, 0, 0)

        vbox_inner = QVBoxLayout()
        vbox_inner.addWidget(self.statusbar, stretch=0)
        vbox_inner.addLayout(hbox_inner, stretch=1)
        vbox_inner.setSpacing(panel_spacing)
        vbox_inner.setContentsMargins(panel_spacing, panel_spacing, panel_spacing - 13, panel_spacing)

        sizegrip = QSizeGrip(self)
        hbox_mid = QHBoxLayout()
        hbox_mid.addLayout(vbox_inner, stretch=1)
        hbox_mid.addWidget(sizegrip, alignment=Qt.AlignBottom | Qt.AlignRight)
        hbox_mid.setContentsMargins(0, 0, 0, 0)
        hbox_mid.setSpacing(0)

        vbox_outer = QVBoxLayout()
        vbox_outer.addWidget(self.titlebar, stretch=0)
        vbox_outer.addLayout(hbox_mid, stretch=1)
        vbox_outer.setContentsMargins(0, 0, 0, 0)
        vbox_outer.setSpacing(0)

        hbox_outer = QHBoxLayout()
        hbox_outer.addWidget(self.ribbon, stretch=0)
        hbox_outer.addLayout(vbox_outer, stretch=1)
        hbox_outer.setContentsMargins(0, 0, 0, 0)
        hbox_outer.setSpacing(0)

        self.ribbon.buttongroup.buttonToggled.connect(self.controlmenu.adjust_visibility)
        self.ribbon.menu_buttons['Devices'].setChecked(True)

        self.controlmenu.menus['Plotting'].buttons['Start'].clicked.connect(self.matplotframe.start_plotting)
        self.controlmenu.menus['Plotting'].buttons['Clear'].clicked.connect(self.matplotframe.clear_plot)
        self.controlmenu.menus['Plotting'].buttons['Zoom'].clicked.connect(self.matplotframe.toolbar.zoom)
        self.controlmenu.menus['Plotting'].buttons['Autoscale'].clicked.connect(self.matplotframe.toggle_autoscale)
        self.controlmenu.menus['Plotting'].check_group.buttonToggled.connect(self.matplotframe.set_plot_visibility)

        for key, button in self.controlmenu.menus['Devices'].unit_buttons.items():
            button.clicked.connect(functools.partial(self.statusbar.change_units, key))
            button.clicked.connect(functools.partial(self.matplotframe.set_units, key))
            button.clicked.connect(functools.partial(self.controlmenu.menus['Programmer'].change_units, key))

        self.controlmenu.menus['Devices'].unit_buttons['Temperature'].click()

        self.setLayout(hbox_outer)
        self.show()
