from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QWidget,
    QTabWidget,
    QTabBar,
)


class MessageTabBar(QTabBar):

    """Custom tab bar settings"""

    def __init__(self) -> None:
        super().__init__()
        self.setElideMode(Qt.ElideRight)

    def tabSizeHint(self, i):
        return QSize(200, 30)

    def tabMinimalSizeHint(self, i):
        return QSize(200, 30)

class MessageTabs(QTabWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        messageTabBar = MessageTabBar()
        messageTabBar.setMovable(True)
        messageTabBar.setAutoHide(True)
        messageTabBar.setTabsClosable(True)
        messageTabBar.setUsesScrollButtons(True)
        self.setTabBar(messageTabBar)

    # def addTab(self):
    #     pass