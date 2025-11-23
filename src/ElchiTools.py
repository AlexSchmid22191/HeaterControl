from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

from src.Engine.Engine import HeaterControlEngine
from Interface.ElchMainWindow import ElchMainWindow


def main():
    app = QApplication()
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = HeaterControlEngine()
    gui = ElchMainWindow()
    app.exec_()


if __name__ == '__main__':
    main()
