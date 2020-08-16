from PySide2.QtCore import QTimer
from threading import Thread
import wx
import functools


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
