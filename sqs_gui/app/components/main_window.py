from typing import List
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from sqs_gui.app.components.message_tabs import MessageTabs
from sqs_gui.app.components.messages_pane import MessagesPane

from sqs_gui.app.receiver import Credentials
from .queues_pane import QueueItem, MessageQueuesPane
from .properties_pane import MQPropertiesPane
from ..queues import MessageQueue

def credentials():
    return Credentials("root", "toortoor", "us-east-1", "http://localhost:9324")

class CentralWidget(QWidget):

    _creds: Credentials
    _queues: List[MessageQueue]

    def __init__(self, creds: Credentials):
        super().__init__()
        self._creds = creds
        self.getMessageQueueList()
        self.initUserInterface()
        self.setupSignalHandlers()
        self.applyStyleSheets()
        self.refreshQueuesPane()

    def getMessageQueueList(self):
        self._queues = list_message_queues(self._creds)
        return self._queues

    def refreshQueuesPane(self):

        for queue in self.getMessageQueueList():
            queueInfo = queue.info()
            self._queuesPane.addItem(
                QueueItem(
                    queueName=queueInfo.name,
                    numMessages=queueInfo.numMessages,
                    dumpedAt=queueInfo.dumpDate,
                )
            )

    def setupSignalHandlers(self):
        self._queuesPane.doubleClicked.connect(self.updatePropertiesPane)

    def updatePropertiesPane(self, queueIndex: int):

        queueInfo = self._queues[queueIndex].info()
        self._propsPane.setItems(queueInfo.attributes, queueInfo.tags)
        # self._propsPane.setItems(queueInfo.attributes, queueInfo.tags)

        # Add tab
        # msgView = MessagesPane()
        # self._messageTabs.addTab(msgView, "OneTwoThreeFourFiveSixSeven")

    def initPropertiesPane(self):
        self._propsPane = MQPropertiesPane()

    def applyStyleSheets(self):

        file = QFile(":splitter.qss")
        if not file.open(QIODevice.ReadOnly):
            return

        self.setStyleSheet(file.readAll().data().decode())
        file.close()

    def initUserInterface(self):

        # Higher-level components
        propsPane = MQPropertiesPane(self)
        queuesPane = MessageQueuesPane(self)
        messageTabs = MessageTabs(self)

        msgView = MessagesPane()
        messageTabs.addTab(msgView, "OneTwoThreeFourFiveSixSeven")

        # msgView2 = MessagesPane()
        # messageTabs.addTab(msgView2, "aaaa")

        # All frames
        topLeftFrame = QFrame()
        topLeftFrame.setFrameShape(QFrame.StyledPanel)
        bottomLeftFrame = QFrame()
        bottomLeftFrame.setFrameShape(QFrame.StyledPanel)
        rightFrame = QFrame()
        rightFrame.setFrameShape(QFrame.StyledPanel)

        # Left frames
        tmpLayout1 = QHBoxLayout()
        tmpLayout1.addWidget(queuesPane)
        topLeftFrame.setLayout(tmpLayout1)

        tmpLayout2 = QHBoxLayout()
        tmpLayout2.addWidget(propsPane)
        bottomLeftFrame.setLayout(tmpLayout2)

        # Right frames
        tmpLayout3 = QHBoxLayout()
        tmpLayout3.addWidget(messageTabs)
        rightFrame.setLayout(tmpLayout3)

        # Vertical splitter
        vSplitter = QSplitter(Qt.Vertical)
        vSplitter.addWidget(topLeftFrame)
        vSplitter.addWidget(bottomLeftFrame)
        vSplitter.setStretchFactor(0, 2)
        vSplitter.setStretchFactor(1, 3)
        vSplitter.handle(1).setAttribute(Qt.WA_Hover)
        vSplitter.setChildrenCollapsible(False)

        # Horizontal splitter
        hSplitter = QSplitter(Qt.Horizontal)
        hSplitter.addWidget(vSplitter)
        hSplitter.addWidget(rightFrame)
        hSplitter.setStretchFactor(0, 2)
        hSplitter.setStretchFactor(1, 3)
        hSplitter.handle(1).setAttribute(Qt.WA_Hover)
        hSplitter.setChildrenCollapsible(False)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(hSplitter)
        self.setLayout(hBoxLayout)

        self._messageTabs = messageTabs
        self._propsPane = propsPane
        self._queuesPane = queuesPane



from ..queues import MessageQueue, list_message_queues


class MainWindow(QMainWindow):

    _creds: Credentials

    def __init__(self, creds: Credentials = credentials()) -> None:
        super().__init__()
        self._creds = creds
        self.initUserInterface()

    def setupExitAction(self):
        exitAction = QAction("&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(exitAction)

    def setupMenuBar(self):
        self.setupExitAction()

    def initUserInterface(self):

        self.resize(1900, 1200)
        self.setCentralWidget(CentralWidget(self._creds))
        # self.statusBar().showMessage('Ready')
        self.setWindowTitle("SQS Graphical user interface")
        self.setupMenuBar()
