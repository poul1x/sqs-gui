from asyncio import QueueEmpty
import datetime
from typing import List
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from sqs_gui.app.receiver import Credentials

from .queue_manager import QueueItem, QueueManager

from .properties_manager import EditableTreeModel, TreeItem

class MQPropertiesView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        headers = TreeItem(["Attribute name", "Value"])
        self._model =EditableTreeModel(headers, self)

        filterProxyModel = QSortFilterProxyModel(self)
        filterProxyModel.setSourceModel(self._model)
        filterProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filterProxyModel.setRecursiveFilteringEnabled(True)
        # filterProxyModel.setFilterKeyColumn(0)
        # filterProxyModel.setDynamicSortFilter(False)

        self._mqView = QTreeView()
        self._mqView.setModel(filterProxyModel)

        # self._model.setItems([TreeItem(["b", "V"])])

        self._mqView.header().setSectionResizeMode(QHeaderView.Interactive)
        self._mqView.header().resizeSections(QHeaderView.ResizeToContents)
        self._mqView.header().setStretchLastSection(True)

        searchField = QLineEdit()
        searchField.setPlaceholderText("Enter property name to find")
        searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)
        searchField.textChanged.connect(filterProxyModel.setFilterFixedString)

        layout.addWidget(self._mqView)
        layout.addWidget(searchField)
        self.setLayout(layout)

    def setItems(self, items: List[TreeItem]):
        self._model.setItems(items)
        self._mqView.header().resizeSections(QHeaderView.ResizeToContents)
        self._mqView.expandAll()


class MessageView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        btnSearch = QPushButton("Search message")
        mqView = QListWidget()
        mqView.addItems(["msg-one", "msg-two", "msg-three", "A" * 500])
        layout.addWidget(mqView)
        layout.addWidget(btnSearch)
        mqView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLayout(layout)


class MyTabBar(QTabBar):
    def __init__(self) -> None:
        super().__init__()
        self.setElideMode(Qt.ElideRight)

    def tabSizeHint(self, i):
        return QSize(200, 30)

    def tabMinimalSizeHint(self, i):
        return QSize(200, 30)

def credentials():
    return Credentials("root", "toortoor", "us-east-1", "http://localhost:9324")

class CentralWidget(QWidget):

    _creds: Credentials

    def __init__(self, creds: Credentials):
        super().__init__()
        self._creds = creds

        # Layouts
        vBoxLayout = QVBoxLayout()
        hBoxLayout = QHBoxLayout()

        # Frames
        topLeftFrame = QFrame()
        bottomLeftFrame = QFrame()
        rightFrame = QFrame()
        topLeftFrame.setFrameShape(QFrame.StyledPanel)
        bottomLeftFrame.setFrameShape(QFrame.StyledPanel)
        topLeftFrame.setFrameShape(QFrame.StyledPanel)
        rightFrame.setFrameShape(QFrame.StyledPanel)

        self._queues = list_message_queues(self._creds)
        mqView = QueueManager()

        for queue in self._queues:
            queueInfo = queue.info()
            mqView.addQueueItem(
                QueueItem(
                    queueName=queueInfo.name,
                    numMessages=queueInfo.numMessages,
                    dumpedAt=queueInfo.dumpDate,
                )
            )

        queueInfo = self._queues[0].info()

        rightVal = "<Empty>" if len(queueInfo.tags) == 0 else ""
        itemTags = TreeItem(["Tags", rightVal])
        for key, val in queueInfo.tags:
            item = TreeItem([key, val])
            # item.setEditable(1, True)
            itemTags.addChild(item)

        rightVal = "<Empty>" if len(queueInfo.attributes) == 0 else ""
        itemAttrs = TreeItem(["Attributes", rightVal])
        for key, val in queueInfo.attributes.items():
            item = TreeItem([key, val or "<Unknown>"])
            # item.setEditable(1, True)
            itemAttrs.addChild(item)

        propsView = MQPropertiesView()
        propsView.setItems([itemTags, itemAttrs])
        # propsView.setItems([itemTags, itemAttrs])
        # propsView.setItems([TreeItem(["c", "d"])])

        msgView = MessageView()
        msgView2 = MessageView()
        msgView3 = MessageView()
        msgView4 = MessageView()
        msgView5 = MessageView()
        tabView = QTabWidget()

        # Left frames
        tmpLayout = QHBoxLayout()
        tmpLayout.addWidget(mqView)
        topLeftFrame.setLayout(tmpLayout)
        tmpLayout = QHBoxLayout()
        tmpLayout.addWidget(propsView)
        bottomLeftFrame.setLayout(tmpLayout)

        tabView.setTabBar(MyTabBar())
        tabView.tabBar().setMovable(True)
        tabView.tabBar().setAutoHide(True)
        tabView.tabBar().setTabsClosable(True)
        tabView.tabBar().setUsesScrollButtons(True)

        # Tabs
        tabView.addTab(msgView, "OneTwoThreeFourFiveSixSeven")
        tabView.addTab(msgView2, "A" * 50)
        tabView.addTab(msgView3, "A" * 50)
        tabView.addTab(msgView4, "A" * 50)
        tabView.addTab(msgView5, "Two")
        # tabView.setStyleSheet("QTabBar::tab { max-width: 150px; }")

        # self.layout.add
        # tabView.setLayout()
        # rightFrame.

        # Right frames
        tmpLayout = QHBoxLayout()
        tmpLayout.addWidget(tabView)
        rightFrame.setLayout(tmpLayout)

        # Splitter 1
        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(topLeftFrame)
        splitter1.addWidget(bottomLeftFrame)
        splitter1.setStretchFactor(0, 2)
        splitter1.setStretchFactor(1, 3)
        splitter1.handle(1).setAttribute(Qt.WA_Hover)
        splitter1.setChildrenCollapsible(False)

        # Splitter 2
        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(rightFrame)
        splitter2.setStretchFactor(0, 2)
        splitter2.setStretchFactor(1, 3)
        splitter2.handle(1).setAttribute(Qt.WA_Hover)
        splitter2.setChildrenCollapsible(False)

        # vBoxLayout.addWidget(splitter1)
        # vBoxLayout.setStretch(0, 2)
        # vBoxLayout.setStretch(1, 3)

        # hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(splitter2)

        self.setLayout(hBoxLayout)

        self.setStyleSheet(
            """
                /*QVBoxLayout {
                    border: 1px solid black;
                }*/
                QSplitter::handle:hover {
                    height: 1px;
                    width: 1px;
                    background: red;
                    color:red;
                }
                /*QSplitter::handle {
                    height: 1px;
                    width: 1px;
                    background: blue;
                    color: blue;
                }*/
                QSplitter::handle:pressed {
                    height: 1px;
                    width: 1px;
                    background: blue;
                    color: blue;
                }
            """
        )


from ..queues import MessageQueue, list_message_queues


class MainWindow(QMainWindow):

    _creds: Credentials

    def __init__(self, creds: Credentials = credentials()) -> None:
        super().__init__()
        self._creds = creds
        self.initUI()

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

    def initUI(self):

        self.setCentralWidget(CentralWidget(self._creds))
        # self.statusBar().showMessage('Ready')
        self.setWindowTitle("SQS Graphical user interface")
        self.setupMenuBar()
