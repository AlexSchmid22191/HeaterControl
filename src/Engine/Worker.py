from PySide6.QtCore import Signal, QRunnable, QObject
from minimalmodbus import ModbusException
from serial import SerialException


class Signals(QObject):
    over = Signal(object)
    con_fail = Signal(str)
    imp_fail = Signal(str)
    error = Signal(str)
    finished = Signal()


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
            # noinspection PyUnresolvedReferences
            self.signals.con_fail.emit(f'Serial communication failed: {ser_ex}')
        except NotImplementedError as imp_ex:
            # noinspection PyUnresolvedReferences
            self.signals.imp_fail.emit(f'{imp_ex}')
        except Exception as ex:
            self.signals.error.emit(f'Error: {ex}')
        else:
            # noinspection PyUnresolvedReferences
            self.signals.over.emit(result)
        finally:
            self.signals.finished.emit()
