from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from Interface.ElchMainWindow import ElchMainWindow
from src.Engine.Engine import HeaterControlEngine


def main():
    app = QApplication()
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = HeaterControlEngine()
    gui = ElchMainWindow()
    gui.show()
    app.exec()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}')
