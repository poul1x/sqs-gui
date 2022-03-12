from datetime import datetime
from threading import Thread
from typing import Dict, List
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from sqs_gui.app.components.message_tabs import MessageTabs
from sqs_gui.app.components.messages_pane import MessageItem, MessagesPane
from sqs_gui.app.components.hints_pane import HintsPane

from sqs_gui.app.receiver import Credentials, ReceiveConditions, receiveMessages
from .queues_pane import QueueItem, MessageQueuesPane
from .properties_pane import MQPropertiesPane
from ..queues import MessageQueue, QueueInfo, list_message_queues
from ..receiver import Message, sendMessages


def credentials():
    return Credentials("root", "toortoor", "us-east-1", "http://localhost:9324")


HINT_TAB = "Hints"



class CentralWidget(QWidget):

    _creds: Credentials
    _queues: List[MessageQueue]
    _messages: Dict[str, List[Message]]

    _queuesPane: MessageQueuesPane
    _propsPane: MQPropertiesPane
    _messageTabs: MessageTabs

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
        self._messages = {q.name: list() for q in self._queues}
        return self._queues

    def refreshQueuesPane(self):

        for queue in self.getMessageQueueList():
            queueInfo = queue.info()
            self._queuesPane.addItem(
                QueueItem(
                    queueName=queueInfo.name,
                    numMessages=queueInfo.numMessages,
                    dumpedAt=queueInfo.dumpDate.strftime("%c"),
                )
            )

    def setupSignalHandlers(self):
        self._queuesPane.doubleClicked.connect(self.onQueuesPaneDoubleClick)

    def updatePropertiesPane(self, queueInfo: QueueInfo):
        self._propsPane.setItems(queueInfo.attributes, queueInfo.tags)

    def findTabIndexByName(self, name: str):

        result = None
        for i in range(self._messageTabs.count()):
            if self._messageTabs.tabText(i) == name:
                result = i
                break

        return result

    def updateMessageTabsPane(self, queueInfo: QueueInfo):

        tabIndex = self.findTabIndexByName(queueInfo.name)
        numMessages = int(queueInfo.attributes["ApproximateNumberOfMessages"])

        if tabIndex:
            self._messageTabs.setCurrentIndex(tabIndex)
            return

        if numMessages == 0:
            # msg = QMessageBox()
            # msg.setIcon(QMessageBox.Information)
            # msg.setText("Queue does not contain any messages")
            # msg.setWindowTitle("No messages")
            # msg.exec()
            return

        messagesPane = MessagesPane(self)
        self._messageTabs.addTab(messagesPane, queueInfo.name)
        self._messageTabs.setCurrentWidget(messagesPane)

        def threadedReceive():

            messages = self._messages[queueInfo.name]
            conditions = ReceiveConditions(all=False, count=1000, timeout=5)

            for msg in receiveMessages(queueInfo.name, self._creds, conditions):

                sendTimestamp = msg.attributes["SentTimestamp"]
                sendDate = datetime.fromtimestamp(int(sendTimestamp) // 1000)

                item = MessageItem(
                    sendTimestamp=sendTimestamp,
                    sendDate=sendDate.strftime("%c"),
                    messageBody=msg.body[:256],
                )

                messagesPane.addItem(item)
                messages.append(msg)

        Thread(target=threadedReceive).start()

    def onQueuesPaneDoubleClick(self, queueIndex: int):
        queueInfo = self._queues[queueIndex].info()
        self.updatePropertiesPane(queueInfo)
        self.updateMessageTabsPane(queueInfo)

    def initPropertiesPane(self):
        self._propsPane = MQPropertiesPane()

    def applyStyleSheets(self):

        file = QFile(":splitter.qss")
        if not file.open(QIODevice.ReadOnly):
            return

        self.setStyleSheet(file.readAll().data().decode())
        file.close()

    def onTabClose(self, index: int):

        # Remove received messages
        queueName = self._messageTabs.tabText(index)
        self._messages[queueName].clear()

        # Remove tab
        widget = self._messageTabs.removeTab(index)


    def initUserInterface(self):

        # Higher-level components
        propsPane = MQPropertiesPane(self)
        queuesPane = MessageQueuesPane(self)
        messageTabs = MessageTabs(self)

        hintsPane = HintsPane(self)
        messageTabs.addTab(hintsPane, HINT_TAB)
        messageTabs.tabCloseRequested.connect(self.onTabClose)

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

    def selectedQueues(self):
        return self._queuesPane.selectedQueues()

    @property
    def queues(self):
        return self._queues

    @property
    def messages(self):
        return self._messages

    @property
    def queuesPane(self):
        return self._queuesPane

    @property
    def propsPane(self):
        return self._propsPane

    @property
    def messageTabs(self):
        return self._messageTabs


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

    def setupQueueActions(self):

        reloadAction = QAction("&Exit", self)
        # reloadAction.setShortcut("Ctrl+Q")
        reloadAction.setStatusTip("Reload queue")
        reloadAction.triggered.connect()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&Queue")
        fileMenu.addAction(reloadAction)

    def setupDeveloperActions(self):

        sendAction = QAction("&Send messages", self)
        sendAction.setStatusTip("Send test messages to selected queue")
        centralWidget: CentralWidget = self.centralWidget()

        def send():

            selectedRows = centralWidget.queuesPane.selectedRows()

            def send2(row):
                queue = centralWidget.queues[row]
                sendMessages(queue.name, 1000, self._creds)

            for row in selectedRows:
                Thread(target=send2, args=(row,)).start()


        sendAction.triggered.connect(lambda: send())

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&Developer")
        fileMenu.addAction(sendAction)

    def setupMenuBar(self):
        self.setupExitAction()
        self.setupDeveloperActions()
        # self.setupQueueActions()

    def initUserInterface(self):

        self.resize(1900, 1200)
        self.setCentralWidget(CentralWidget(self._creds))
        # self.statusBar().showMessage('Ready')
        self.setWindowTitle("SQS Graphical user interface")
        self.setupMenuBar()
