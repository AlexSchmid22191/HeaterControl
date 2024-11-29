from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from pubsub.pub import addTopicDefnProvider, TOPIC_TREE_FROM_CLASS, setTopicUnspecifiedFatal

from Engine import Topic_Def
from Engine.Engine import HeaterControlEngine
from QtInterface.ElchMainWindow import ElchMainWindow

addTopicDefnProvider(Topic_Def, TOPIC_TREE_FROM_CLASS)
setTopicUnspecifiedFatal(True)


def main():
    app = QApplication()
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = HeaterControlEngine()
    gui = ElchMainWindow()
    app.exec()


if __name__ == '__main__':
    main()
