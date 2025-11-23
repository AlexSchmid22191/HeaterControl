import functools

from PySide2.QtWidgets import QWidget, QPushButton, QCheckBox, QButtonGroup, QVBoxLayout, QLabel, QFileDialog

from src.Signals import gui_signals


class ElchPlotMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Clear', 'Export', 'Autoscale', 'Zoom']
        self.buttons = {key: QPushButton(parent=self, text=key, objectName=key) for key in controls}
        self.buttons['Start'].setCheckable(True)
        self.buttons['Autoscale'].setCheckable(True)
        self.buttons['Autoscale'].setChecked(True)
        self.buttons['Zoom'].setCheckable(True)
        self.checks = {key: QCheckBox(parent=self, text=key, objectName=key)
                       for key in ['Sensor PV', 'Controller PV', 'Setpoint', 'Power']}
        self.check_group = QButtonGroup()
        self.check_group.setExclusive(False)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(text='Plotting', objectName='Header'))
        for key in controls:
            vbox.addWidget(self.buttons[key])
            match key:
                case 'Start':
                    self.buttons[key].clicked.connect(functools.partial(self.start_stop_plotting))
                case 'Clear':
                    self.buttons[key].clicked.connect(self.clear_pplot)
                case 'Export':
                    self.buttons[key].clicked.connect(self.export_data)
                case 'Autoscale':
                    self.buttons[key].clicked.connect(self.toggle_autoscale)
                case 'Zoom':
                    self.buttons[key].clicked.connect(self.toggle_zoom)

        vbox.addSpacing(20)
        vbox.addWidget(QLabel(text='Data sources', objectName='Header'))
        for key, button in self.checks.items():
            button.setChecked(True)
            self.check_group.addButton(button)
            vbox.addWidget(button)
        vbox.addStretch()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(vbox)

    def start_stop_plotting(self):
        if self.buttons['Start'].isChecked():
            gui_signals.start_log.emit()
        else:
            gui_signals.log.emit()

    def clear_pplot(self):
        gui_signals.clear_log.emit()
        if self.buttons['Start'].isChecked():
            self.buttons['Start'].click()

    def export_data(self):
        if (file_path := QFileDialog.getSaveFileName(self, 'Save as...', 'Logs/Log.csv', 'CSV (*.csv)')[0]) != '':
            gui_signals.export_log.emit(file_path)

    def toggle_autoscale(self):
        pass

    def toggle_zoom(self):
        pass

