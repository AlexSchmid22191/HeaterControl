from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication
from PySide2.QtWinExtras import QtWin
from pubsub.pub import addTopicDefnProvider, TOPIC_TREE_FROM_CLASS, setTopicUnspecifiedFatal

from Engine import Topic_Def
from Engine.Engine import HeaterControlEngine
from QtInterface.ElchMainWindow import ElchMainWindow

addTopicDefnProvider(Topic_Def, TOPIC_TREE_FROM_CLASS)
setTopicUnspecifiedFatal(True)


def main():
    QtWin.setCurrentProcessExplicitAppUserModelID('elchworks.elchitools.2.3')
    app = QApplication()
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = HeaterControlEngine()
    gui = ElchMainWindow()
    app.exec_()


if __name__ == '__main__':
    main()
