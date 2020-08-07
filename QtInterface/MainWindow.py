import functools

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QButtonGroup, \
    QDoubleSpinBox, QLabel, QRadioButton, QComboBox, QFormLayout, QToolButton, QSizeGrip
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure


class ElchMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.controlmenu = ElchMenuPages()
        self.ribbon = ElchRibbon(menus=self.controlmenu.menus)
        self.matplotframe = ElchMatplot()
        self.titlebar = ElchTitlebar()

        hbox_inner = QHBoxLayout()
        hbox_inner.addWidget(self.matplotframe, stretch=1)
        hbox_inner.addWidget(self.controlmenu, stretch=0)

        vbox = QVBoxLayout()
        vbox.addWidget(self.titlebar, stretch=0)
        vbox.addLayout(hbox_inner, stretch=1)

        hbox_outer = QHBoxLayout()
        hbox_outer.addWidget(self.ribbon, stretch=0)
        hbox_outer.addLayout(vbox, stretch=1)

        for box in [hbox_inner, hbox_outer, vbox]:
            box.setSpacing(0)
            box.setContentsMargins(0, 0, 0, 0)

        self.ribbon.buttongroup.buttonToggled.connect(self.controlmenu.adjust_visibility)
        self.ribbon.menu_buttons['Devices'].setChecked(True)
        self.setLayout(hbox_outer)
        self.show()


class ElchRibbon(QWidget):
    def __init__(self, menus=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('ElchRibbon{background-color:#2A2D56}')
        self.menus = menus if menus is not None else ['Devices', 'Control', 'Setpoints', 'PID', 'Plotting', 'Logging']
        self.menu_buttons = {key: QPushButton(parent=self, text=key) for key in self.menus}
        self.buttongroup = QButtonGroup()
        self.buttongroup.setExclusive(True)
        elchicon = QLabel()
        elchicon.setPixmap(QPixmap('../Icons/ElchiHead.png').scaled(100, 100))

        vbox = QVBoxLayout()
        vbox.addWidget(elchicon)
        for key in self.menus:
            vbox.addWidget(self.menu_buttons[key])
            self.buttongroup.addButton(self.menu_buttons[key])
            self.menu_buttons[key].setCheckable(True)
            self.menu_buttons[key].setMinimumHeight(100)
            self.menu_buttons[key].setStyleSheet('QPushButton{border-image: url(../Icons/Logging_Gray.png)}'
                                                 'QPushButton:hover{border-image: url(../Icons/Logging_Glow.png)}')

        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(5)
        self.setMinimumWidth(80)
        self.setLayout(vbox)

    def tell(self, *args):
        print(args)


class ElchMenuPages(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.menus = {'Devices': ElchDeviceMenu(), 'Control': ElchControllerMenu(), 'PID': ElchPidMenu(),
                      'Logging': ElchLogMenu(), 'Plotting': ElchPlotMenu()}

        self.setMinimumWidth(120)
        vbox = QVBoxLayout()

        sizegrip = QSizeGrip(self)
        for menu in self.menus:
            self.menus[menu].setVisible(False)
            vbox.addWidget(self.menus[menu])
        vbox.addStretch()
        vbox.addWidget(sizegrip, alignment=Qt.AlignBottom | Qt.AlignRight)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    0.16470588235, 0.17647058824, 0.33725490196

    def adjust_visibility(self, button, visibility):
        menu = button.text()
        self.menus[menu].setVisible(visibility)


class ElchMatplot(FigureCanvas):
    def __init__(self, *args, **kwargs):
        super().__init__(Figure(figsize=(6, 6)), *args, **kwargs)
        self.ax = self.figure.subplots()
        self.figure.set_facecolor('#181C3F')
        self.ax.set_facecolor('#181C3F')
        self.ax.plot([1, 2])


class ElchPlotMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Stop', 'Resume', 'Clear']
        self.buttons = {key: QPushButton(text=key, parent=self) for key in controls}

        vbox = QVBoxLayout()
        for key in controls:
            vbox.addWidget(self.buttons[key])

        self.setLayout(vbox)


class ElchLogMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Stop', 'Pause']
        self.buttons = {key: QPushButton(parent=self, text=key) for key in controls}

        vbox = QVBoxLayout()
        for key in controls:
            vbox.addWidget(self.buttons[key])

        self.setLayout(vbox)


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
            vbox.addStretch(2)

        self.buttons['Automatic'].setChecked(True)
        vbox.addWidget(QLabel(text='Control mode'))
        for button in self.buttons:
            vbox.addWidget(self.buttons[button])

        vbox.setSpacing(5)
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
            vbox.addStretch(5)
        self.setLayout(vbox)


class ElchPidMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parameters = {'P1': 'Proportional 1', 'I1': 'Integral 1 (s)', 'D1': 'Derivative 1 (s)',
                      'P2': 'Proportional 2', 'I2': 'Integral 2 (s)', 'D2': 'Derivative 2 (s)',
                      'P3': 'Proportional 3', 'I3': 'Integral 3 (s)', 'D3': 'Derivative 3 (s)',
                      'GS': 'Gain scheduling', 'B12': 'Boundary 1/2', 'B23': 'Boundary 2/3'}

        self.labels = {key: QLabel(text=parameters[key]) for key in parameters}
        self.entries = {key: QComboBox() if key == 'GS' else QDoubleSpinBox() for key in parameters}

        grid = QFormLayout()
        grid.setSpacing(5)
        grid.setContentsMargins(0, 0, 0, 0)
        for key in parameters:
            grid.addRow(parameters[key], self.entries[key])

        self.setLayout(grid)


class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ElchTitlebar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('ElchTitlebar{background-color: #181C3F}\n QToolButton{background-color: gray; border:none}\n')

        self.setMinimumHeight(50)
        label = QLabel(text='Elchi Control')
        buttons = {key: ElchButton(self) for key in ['Minimize', 'Close']}

        hbox = QHBoxLayout()
        hbox.addWidget(label)
        hbox.addStretch(-1)
        for key in buttons:
            buttons[key].setIcon(QIcon('../Icons/Logging.png'))
            buttons[key].setFixedSize(50, 50)
            hbox.addWidget(buttons[key])

        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        self.setLayout(hbox)

        self.dragPosition = None
        buttons['Minimize'].clicked.connect(self.minimize)
        buttons['Close'].clicked.connect(self.close)

    def mouseMoveEvent(self, event):
        # Enable mouse dragging
        if event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.dragPosition)
            event.accept()

    def mousePressEvent(self, event):
        # Enable mouse dragging
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.parent().frameGeometry().topLeft()
            event.accept()

    def minimize(self):
        self.parent().showMinimized()

    def close(self):
        self.parent().close()


class ElchButton(QToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def enterEvent(self, *args):
        self.setStyleSheet('ElchButton{background-color: blue}')

    def leaveEvent(self, *args):
        self.setStyleSheet('ElchButton{background-color: green}')


app = QApplication()
gui = ElchMainWindow()
app.exec_()