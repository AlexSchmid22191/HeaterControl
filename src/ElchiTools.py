from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.Interface.ElchMainWindow import ElchMainWindow
from src.Engine.Engine import HeaterControlEngine
import src.appinfo

def main():
    app = QApplication()
    app.setApplicationName(f"{src.appinfo.APP_NAME}")
    app.setApplicationDisplayName(f"{src.appinfo.APP_NAME}")
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
