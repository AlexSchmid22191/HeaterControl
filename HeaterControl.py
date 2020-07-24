from threading import Timer, enumerate

import wx
from pubsub.pub import addTopicDefnProvider, TOPIC_TREE_FROM_CLASS, setTopicUnspecifiedFatal

import Topic_Def
from Engine import HeaterControlEngine
from Interface import HeaterInterface

addTopicDefnProvider(Topic_Def, TOPIC_TREE_FROM_CLASS)
setTopicUnspecifiedFatal(True)


def main():
    app = wx.App()
    app.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
    engine = HeaterInterface(None)
    print('Engine initilized: {:s}'.format(str(engine.__class__)))
    gui = HeaterControlEngine()
    print('GUI initialized: {:s}'.format(str(gui.__class__)))
    app.MainLoop()


if __name__ == '__main__':
    main()
    for thread in enumerate():
        if type(thread) == Timer:
            thread.cancel()