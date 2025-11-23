from serial import SerialException
from minimalmodbus import ModbusException
from PySide2.QtCore import Signal, QRunnable, QObject


class Signals(QObject):
    over = Signal(object)
    con_fail = Signal(str)
    imp_fail = Signal(str)


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
        except (SerialException, ModbusException) as ser_ex:
            self.signals.con_fail.emit(f'Serial communication failed: {ser_ex}')
        except NotImplementedError as imp_ex:
            self.signals.con_fail.emit(imp_ex)
        else:
            self.signals.over.emit(result)
