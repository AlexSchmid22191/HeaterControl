from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

from Interface.ElchMainWindow import ElchMainWindow
from src.Engine.Engine import HeaterControlEngine


def main():
    app = QApplication()
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = HeaterControlEngine()
    print(f'Engine started!: {engine}')
    gui = ElchMainWindow()
    gui.show()
    app.exec_()


if __name__ == '__main__':
    main()
