from dataclasses import dataclass
from typing import List
from enum import Enum

from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QVBoxLayout,
    QTableView,
    QLineEdit,
    QWidget,
)


@dataclass
class QueueItem:
    queueName: str
    numMessages: str
    dumpedAt: str


class Columns(int, Enum):
    queueName = 0
    numMessages = 1
    dumpedAt = 2


class MessageQueuesPane(QWidget):

    """Shows list of queues in a table widget"""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        labels = ["Queue name", "Messages", "Dumped at"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        filterProxyModel = QSortFilterProxyModel()
        filterProxyModel.setSourceModel(dataModel)
        filterProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filterProxyModel.setFilterKeyColumn(Columns.queueName)

        table = QTableView()
        table.setModel(filterProxyModel)
        table.setEditTriggers(QAbstractItemView.EditKeyPressed)

        hHeader = table.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.queueName, QHeaderView.Stretch)
        hHeader.setSectionResizeMode(Columns.numMessages, QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(Columns.dumpedAt, QHeaderView.ResizeToContents)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = table.verticalHeader()
        vHeader.setVisible(False)

        searchField = QLineEdit()
        searchField.setPlaceholderText("Enter queue name to find")
        searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)
        searchField.textChanged.connect(filterProxyModel.setFilterFixedString)

        layout = QVBoxLayout()
        layout.addWidget(table)
        layout.addWidget(searchField)

        self._dataModel = dataModel
        self.setLayout(layout)

    def addItem(self, item: QueueItem):

        roFlags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        rwFlags = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

        itemName = QStandardItem(item.queueName)
        itemName.setFlags(rwFlags)

        itemMessages = QStandardItem(item.numMessages)
        itemMessages.setFlags(roFlags)

        itemDumpedAt = QStandardItem(item.dumpedAt)
        itemDumpedAt.setFlags(roFlags)

        row = [itemName, itemMessages, itemDumpedAt]
        self._dataModel.appendRow(row)

    def setItems(self, items: List[QueueItem]):
        for item in items:
            self.addItem(item)