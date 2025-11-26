import functools

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizeGrip

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

        self.control_menu = ElchMenu(parent=self)
        self.ribbon = ElchRibbon(menus=self.control_menu.menus)
        self.matplot_frame = ElchPlot()
        self.titlebar = ElchTitlebar()
        self.statusbar = ElchStatusBar()
        self.notification_bar = ElchNotificationBar()

        panel_spacing = 20

        vbox_innermost = QVBoxLayout()
        vbox_innermost.addWidget(self.matplot_frame, stretch=1)
        vbox_innermost.addWidget(self.notification_bar, stretch=0)

        hbox_inner = QHBoxLayout()
        hbox_inner.addLayout(vbox_innermost, stretch=1)
        hbox_inner.addWidget(self.control_menu, stretch=0)
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

        self.ribbon.buttongroup.buttonToggled.connect(self.control_menu.adjust_visibility)
        self.ribbon.menu_buttons['Devices'].setChecked(True)

        self.control_menu.menus['Plotting'].buttons['Start'].clicked.connect(self.matplot_frame.start_plotting)
        self.control_menu.menus['Plotting'].buttons['Clear'].clicked.connect(self.matplot_frame.clear_plot)
        self.control_menu.menus['Plotting'].buttons['Zoom'].clicked.connect(self.matplot_frame.toolbar.zoom)
        self.control_menu.menus['Plotting'].buttons['Autoscale'].clicked.connect(self.matplot_frame.toggle_autoscale)
        self.control_menu.menus['Plotting'].check_group.buttonToggled.connect(self.matplot_frame.set_plot_visibility)

        for key, button in self.control_menu.menus['Devices'].unit_buttons.items():
            button.clicked.connect(functools.partial(self.statusbar.change_units, key))
            button.clicked.connect(functools.partial(self.matplot_frame.set_units, key))
            button.clicked.connect(functools.partial(self.control_menu.menus['Programmer'].change_units, key))

        self.control_menu.menus['Devices'].unit_buttons['Temperature'].click()

        self.setLayout(hbox_outer)
