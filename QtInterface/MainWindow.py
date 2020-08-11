from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QButtonGroup, \
    QLabel, QToolButton, QSizeGrip
from QtInterface.ElchMenuPages import ElchMenuPages
from QtInterface.ElchPlot import ElchPlot


class ElchMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.FramelessWindowHint)
        with open('style.qss') as stylefile:
            self.setStyleSheet(stylefile.read())

        self.controlmenu = ElchMenuPages()
        self.ribbon = ElchRibbon(menus=self.controlmenu.menus)
        self.matplotframe = ElchPlot()
        self.titlebar = ElchTitlebar()
        self.statusbar = ElchStatusBar()

        hbox_inner = QHBoxLayout()
        hbox_inner.addWidget(self.matplotframe, stretch=1)
        hbox_inner.addWidget(self.controlmenu, stretch=0)
        hbox_inner.setSpacing(30)
        hbox_inner.setContentsMargins(0, 0, 0, 0)

        vbox_inner = QVBoxLayout()
        vbox_inner.addWidget(self.statusbar, stretch=0)
        vbox_inner.addLayout(hbox_inner, stretch=1)
        vbox_inner.setSpacing(30)
        vbox_inner.setContentsMargins(30, 30, 17, 30)

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
        self.setLayout(hbox_outer)
        self.show()


class ElchRibbon(QWidget):
    def __init__(self, menus=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.menus = menus if menus is not None else ['Devices', 'Control', 'Setpoints', 'PID', 'Plotting', 'Logging']
        self.menu_buttons = {key: QPushButton(parent=self, objectName=key) for key in self.menus}
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
            self.menu_buttons[key].setFixedSize(150, 100)

        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.setMinimumWidth(150)
        self.setLayout(vbox)


class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        parameters = ['Sensor PV', 'Controller PV', 'Setpoint', 'Power']
        icons = {key: QLabel() for key in parameters}
        labels = {key: QLabel(text=key, objectName='label') for key in parameters}
        self.values = {key: QLabel(text='0.00 °C', objectName='value') for key in parameters}

        vboxes = {key: QVBoxLayout() for key in parameters}

        hbox = QHBoxLayout()
        for key in parameters:
            vboxes[key].addWidget(self.values[key])
            vboxes[key].addWidget(labels[key])
            vboxes[key].setContentsMargins(0, 0, 0, 0)
            vboxes[key].setSpacing(5)
            hbox.addWidget(icons[key])
            hbox.addStretch(1)
            hbox.addLayout(vboxes[key])
            hbox.addStretch(10)
            icons[key].setPixmap(QPixmap('../Icons/Ring_{:s}.png'.format(key)))
        hbox.setContentsMargins(10, 10, 10, 10)

        self.setLayout(hbox)


class ElchTitlebar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(50)
        #label = QLabel(text='Elchi Control')
        buttons = {key: QToolButton(self, objectName=key) for key in ['Minimize', 'Close']}

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        #hbox.addWidget(label)
        hbox.addStretch(10)
        for key in buttons:
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


app = QApplication()
gui = ElchMainWindow()
app.exec_()