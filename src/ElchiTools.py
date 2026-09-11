import argparse
import logging
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.Engine.AppLogging import setup_logging
from src.Interface.ElchMainWindow import ElchMainWindow
from src.Engine.Engine import HeaterControlEngine
import src.appinfo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_mode", action="store_true")
    args = parser.parse_args()
    setup_logging(logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"This is {src.appinfo.APP_NAME} Version {src.appinfo.APP_VERSION}")
    logger.info("Application starting")
    app = QApplication()
    app.setApplicationName(f"{src.appinfo.APP_NAME}")
    app.setApplicationDisplayName(f"{src.appinfo.APP_NAME}")
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = HeaterControlEngine(args.test_mode)
    gui = ElchMainWindow()
    app.aboutToQuit.connect(engine.shutdown)
    gui.show()
    app.exec()
    logger.info("ElchiTools exited!")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}')
