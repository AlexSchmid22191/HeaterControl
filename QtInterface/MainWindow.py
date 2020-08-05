import functools

import matplotlib.pyplot as plt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QGridLayout, \
    QButtonGroup, QDoubleSpinBox, QLabel, QRadioButton, QComboBox
from PySide2.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure


class ElchMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.controlmenu = ElchMenuPages(parent=self)
        self.ribbon = ElchRibbon(parent=self, menus=self.controlmenu.menus)
        self.matplotframe = ElchMatplot()

        hbox = QHBoxLayout()
        hbox.addWidget(self.ribbon, stretch=0)
        hbox.addWidget(self.matplotframe, stretch=1)
        hbox.addWidget(self.controlmenu, stretch=0)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        # with open('style.qss') as stylefile:
        #     self.setStyleSheet(stylefile.read())

        self.ribbon.buttongroup.buttonToggled.connect(self.controlmenu.adjust_visibility)
        self.ribbon.menu_buttons['Control'].setChecked(True)
        self.setLayout(hbox)
        self.show()


class ElchRibbon(QWidget):
    def __init__(self, menus=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.menus = menus if menus is not None else ['Devices', 'Control', 'Setpoints', 'PID', 'Plotting', 'Logging']
        self.menu_buttons = {key: QPushButton(parent=self, text=key) for key in self.menus}
        icons = {key: QIcon('../Icons/Logging.png') for key in self.menus}
        self.buttongroup = QButtonGroup()
        self.buttongroup.setExclusive(True)
        vbox = QVBoxLayout()

        for key in self.menus:
            vbox.addWidget(self.menu_buttons[key])
            self.buttongroup.addButton(self.menu_buttons[key])
            self.menu_buttons[key].setCheckable(True)
            self.menu_buttons[key].setIcon(icons[key])

        vbox.addStretch()
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(5)
        self.setMinimumWidth(200)
        self.setLayout(vbox)


class ElchMenuPages(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.menus = {'Devices': ElchDeviceMenu(), 'Control': ElchControllerMenu(), 'Logging': ElchLogMenu(),
                      'Plotting': ElchPlotMenu()}
        self.setMinimumWidth(120)
        vbox = QVBoxLayout()

        for menu in self.menus:
            self.menus[menu].setVisible(False)
            vbox.addWidget(self.menus[menu])

        vbox.addStretch()
        self.setLayout(vbox)

    def adjust_visibility(self, button, visibility):
        menu = button.text()
        self.menus[menu].setVisible(visibility)


class ElchMatplot(FigureCanvas):
    def __init__(self, *args, **kwargs):
        super().__init__(Figure(figsize=(6, 6)), *args, **kwargs)
        self.ax = self.figure.subplots()
        self.figure.set_facecolor('#242537')
        self.ax.set_facecolor('#242537')
        self.ax.plot([1, 2])


class ElchPlotMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Stop', 'Resume', 'Clear']
        self.buttons = {key: QPushButton(text=key, parent=self) for key in controls}

        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        for idx, control in enumerate(controls):
            grid.addWidget(self.buttons[control], idx // 2, idx % 2)

        self.setLayout(grid)
        self.setMinimumHeight(100)


class ElchLogMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Stop', 'Pause']
        self.buttons = {key: QPushButton(parent=self, text=key) for key in controls}

        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        for idx, control in enumerate(controls):
            grid.addWidget(self.buttons[control], idx // 2, idx % 2)

        self.setLayout(grid)
        self.setMinimumHeight(100)


class ElchControllerMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key) for key in ['Setpoint', 'Rate', 'Power']}
        self.entries = {key: QDoubleSpinBox(decimals=1, singleStep=10, minimum=0, maximum=10000) for key in self.labels}
        self.buttons = {key: QRadioButton(text=key) for key in ['Automatic', 'Manual']}

        vbox = QVBoxLayout()
        for label in self.labels:
            self.entries[label].setKeyboardTracking(False)
            self.entries[label].valueChanged.connect(functools.partial(self.dispaly_value, control=label))
            vbox.addWidget(self.labels[label], stretch=0)
            vbox.addWidget(self.entries[label], stretch=0, alignment=Qt.AlignLeft)
            vbox.addStretch(1)

        self.buttons['Automatic'].setChecked(True)
        vbox.addWidget(QLabel(text='Control mode'))
        for button in self.buttons:
            vbox.addWidget(self.buttons[button])

        vbox.addStretch(5)
        vbox.setSpacing(5)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    @staticmethod
    def dispaly_value(*args, **kwargs):
        print(args, kwargs)


class ElchDeviceMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key) for key in ['Controller', 'Sensor']}
        self.device_menus = {key: QComboBox() for key in self.labels}
        self.port_menus = {key: QComboBox() for key in self.labels}
        self.connect_buttons = {key: QPushButton(text='Connect') for key in self.labels}

        vbox = QVBoxLayout()
        for key in self.labels:
            vbox.addWidget(self.labels[key])
            vbox.addWidget(self.device_menus[key])
            vbox.addWidget(self.port_menus[key])
            vbox.addWidget(self.connect_buttons[key])
            vbox.addStretch(1)

        vbox.addStretch(5)
        self.setLayout(vbox)

class ElchPidMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)





app = QApplication()
gui = ElchMainWindow()
app.exec_()
