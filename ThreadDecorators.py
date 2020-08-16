from PySide2.QtCore import QTimer, QThread, Signal, QRunnable, QObject, QThreadPool
from threading import Thread
import wx
import functools
import pubsub.pub


def in_new_thread(target_func):
    """Wrapper to execute function in new thread"""
    @functools.wraps(target_func)
    def wrapper(*args, **kwargs):
        com_thread = Thread(target=target_func, args=args, kwargs=kwargs)
        com_thread.start()
    return wrapper


def in_main_thread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wx.CallAfter(func, *args, **kwargs)

    return wrapper


def in_qt_main_thread(func):
    def wrapper(*args, **kwargs):
        QTimer.singleShot(1, func)

    return wrapper


class OtherThread(QThread):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn

    over = Signal(object)

    def run(self):
        x = self.fn()
        self.over.emit(x)


class Signals(QObject):
    over = Signal(object)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.sig = Signals()
        self.over = self.sig.over
        self.fn = fn


    def run(self):
        x = self.fn()
        self.sig.over.emit(x)



