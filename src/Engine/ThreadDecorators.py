import serial
from PySide2.QtCore import Signal, QRunnable, QObject


class Signals(QObject):
    over = Signal(object)
    started = Signal(object)
    con_fail = Signal(object)
    imp_fail = Signal(object)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except serial.SerialException as ser_ex:
            print(ser_ex)
            self.signals.con_fail.emit(ser_ex)
        except NotImplementedError as imp_ex:
            print(imp_ex)
            self.signals.con_fail.emit(imp_ex)
        else:
            self.signals.over.emit(result)
