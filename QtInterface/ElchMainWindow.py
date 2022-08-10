import functools

import pubsub.pub
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QPixmap, QFontDatabase
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QButtonGroup, \
    QLabel, QToolButton, QSizeGrip

from QtInterface.ElchMenuPages import ElchMenuPages
from QtInterface.ElchPlot import ElchPlot


class ElchMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.FramelessWindowHint)

        QFontDatabase.addApplicationFont('Fonts/Roboto-Light.ttf')
        QFontDatabase.addApplicationFont('Fonts/Roboto-Regular.ttf')

        with open('QtInterface/style.qss') as stylefile:
            self.setStyleSheet(stylefile.read())

        self.controlmenu = ElchMenuPages()
        self.ribbon = ElchRibbon(menus=self.controlmenu.menus)
        self.matplotframe = ElchPlot()
        self.titlebar = ElchTitlebar()
        self.statusbar = ElchStatusBar()

        panel_spacing = 20

        hbox_inner = QHBoxLayout()
        hbox_inner.addWidget(self.matplotframe, stretch=1)
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

        for key, button in self.controlmenu.menus['Devices'].unitbuttons.items():
            button.clicked.connect(functools.partial(self.statusbar.change_units, key))
            button.clicked.connect(functools.partial(self.matplotframe.set_units, key))

        self.controlmenu.menus['Devices'].unitbuttons['Temperature'].click()

        self.setLayout(hbox_outer)
        self.show()


class ElchTitlebar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(50)
        buttons = {key: QToolButton(self, objectName=key) for key in ['Minimize', 'Close']}

        hbox = QHBoxLayout()
        hbox.addStretch(1)
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


class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.unit = '°C'

        parameters = ['Sensor PV', 'Controller PV', 'Setpoint', 'Power']
        icons = {key: QLabel() for key in parameters}
        labels = {key: QLabel(text=key, objectName='label') for key in parameters}
        self.values = {key: QLabel(text='- - -', objectName='value') for key in parameters}
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
            icons[key].setPixmap(QPixmap('Icons/Ring_{:s}.png'.format(key)))
        hbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(hbox)

        self.timer = QTimer(parent=self)
        self.timer.timeout.connect(lambda: pubsub.pub.sendMessage(topicName='gui.request.status'))
        self.timer.start(1000)
        pubsub.pub.subscribe(self.update_values, topicName='engine.answer.status')

    def update_values(self, status_values):
        assert isinstance(status_values, dict), 'Illegal data type recieved: {:s}'.format(str(type(status_values)))

        for key, value in status_values.items():
            assert key in self.values, 'Illegal key recieved: {:s}'.format(key)
            if key == 'Power':
                self.values[key].setText('{:.1f} %'.format(value[0]))
            else:
                self.values[key].setText('{:.1f} {:s}'.format(value[0], self.unit))

    def change_units(self, mode):
        self.unit = {'Temperature': '°C', 'Voltage': 'mV'}[mode]
