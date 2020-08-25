from pubsub.pub import addTopicDefnProvider, TOPIC_TREE_FROM_CLASS, setTopicUnspecifiedFatal

from Engine import Topic_Def
from Engine.Engine import HeaterControlEngine
from PySide2.QtWidgets import QApplication
from QtInterface.ElchMainWindow import ElchMainWindow

addTopicDefnProvider(Topic_Def, TOPIC_TREE_FROM_CLASS)
setTopicUnspecifiedFatal(True)


def main():
    app = QApplication()
    engine = HeaterControlEngine()
    gui = ElchMainWindow()
    app.exec_()


if __name__ == '__main__':
    main()
