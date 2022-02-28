from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QWidget,
)

class MessagesPane(QWidget):

    """Displays list of messages"""

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

