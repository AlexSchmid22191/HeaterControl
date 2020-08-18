import wx
import time
import serial
import functools
import threading

from PySide2.QtCore import Signal, QRunnable, QObject


def in_new_thread(target_func):
    """Wrapper to execute function in new thread"""
    @functools.wraps(target_func)
    def wrapper(*args, **kwargs):
        com_thread = threading.Thread(target=target_func, args=args, kwargs=kwargs)
        com_thread.start()
    return wrapper


def in_main_thread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wx.CallAfter(func, *args, **kwargs)

    return wrapper


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


class WorkThread(threading.Thread):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

    def run(self):
        self.signals.started.emit()
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