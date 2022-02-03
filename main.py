from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class MessageQueueView(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        btnSearch = QPushButton("Search message queue")
        mqView = QListWidget()
        mqView.addItems(["mq-one", "mq-two", "mq-three", "mq-four", "mq-five"])
        layout.addWidget(mqView)
        layout.addWidget(btnSearch)
        self.setLayout(layout)


class MQPropertiesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        btnSearch = QPushButton("Search mq props")
        mqView = QListWidget()
        mqView.addItems(["mq-one", "mq-two", "mq-three"])
        layout.addWidget(mqView)
        layout.addWidget(btnSearch)
        self.setLayout(layout)

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

class MyWindow(QWidget):

    def __init__(self):
        super().__init__()

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

        # My widgets
        mqView = MessageQueueView()
        propsView = MQPropertiesView()
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

if __name__ == "__main__":

    app = QApplication(sys.argv)

    myWindow = MyWindow()
    myWindow.show()

    sys.exit(app.exec())