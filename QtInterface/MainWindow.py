from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFrame, QApplication, QGridLayout
from PySide2.QtGui import QIcon, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import functools
import matplotlib.pyplot as plt
import mplcyberpunk


class Elchcontrol(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ribbon = ElchRibbon(parent=self)
        matplotframe = QMatplot()
        hbox = QHBoxLayout()
        hbox.addWidget(ribbon, stretch=0)
        hbox.addWidget(matplotframe, stretch=1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)

        # with open('style.qss') as stylefile:
        #     self.setStyleSheet(stylefile.read())

        self.setLayout(hbox)
        self.show()


class QMatplot(FigureCanvas):
    def __init__(self, *args, **kwargs):
        super().__init__(Figure(figsize=(6, 6)), *args, **kwargs)
        plt.style.use('cyberpunk')
        self.ax = self.figure.subplots()
        self.figure.set_facecolor(self.ax.get_facecolor())
        self.ax.plot([1, 2])
        mplcyberpunk.add_glow_effects(self.ax)


class ElchRibbon(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menus = ['Devices', 'Control', 'Setpoints', 'PID', 'Plotting', 'Logging']
        self.menu_buttons = {key: QPushButton(parent=self, text=key) for key in self.menus}
        self.menu_frames = {key: QFrame(parent=self) for key in self.menus}
        vbox = QVBoxLayout()

        self.menu_frames['Plotting'] = ElchPlotMenu(parent=self)
        self.menu_frames['Logging'] = ElchLogMenu(parent=self)

        for key in self.menus:
            vbox.addWidget(self.menu_buttons[key])
            vbox.addWidget(self.menu_frames[key])
            self.menu_frames[key].setVisible(False)
            self.menu_frames[key].setMinimumHeight(50)
            self.menu_buttons[key].clicked.connect(functools.partial(self.select_menu, key))

        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.setMinimumWidth(200)
        self.setLayout(vbox)

    def select_menu(self, menu):
        for frame in self.menu_frames:
            self.menu_frames[frame].setVisible(menu == frame)


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
        self.buttons = {key: QPushButton(text=key, parent=self) for key in controls}

        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        for idx, control in enumerate(controls):
            grid.addWidget(self.buttons[control], idx // 2, idx % 2)

        self.setLayout(grid)
        self.setMinimumHeight(100)


class ElchControlMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


app = QApplication()
gui = Elchcontrol()
app.exec_()
