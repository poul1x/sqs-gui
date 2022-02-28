from dataclasses import dataclass
from typing import List
from enum import Enum

from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, QModelIndex
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

    """Shows list of queues in a tableView widget"""

    _tableView: QTableView
    _dataModel: QStandardItemModel

    doubleClicked = pyqtSignal(int)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()
        self.createCustomSignals()

    def slotDoubleClicked(self, index: QModelIndex):
        self.doubleClicked.emit(index.row())

    def createDoubleClickedSignal(self):
        self._tableView.doubleClicked.connect(self.slotDoubleClicked)

    def createCustomSignals(self):
        self.createDoubleClickedSignal()

    def initUserInterface(self):

        labels = ["Queue name", "Messages", "Dumped at"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        filterProxyModel = QSortFilterProxyModel()
        filterProxyModel.setSourceModel(dataModel)
        filterProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filterProxyModel.setFilterKeyColumn(Columns.queueName)

        tableView = QTableView()
        tableView.setModel(filterProxyModel)
        tableView.setEditTriggers(QAbstractItemView.EditKeyPressed)

        hHeader = tableView.horizontalHeader()
        hHeader.setSectionResizeMode(Columns.queueName, QHeaderView.Stretch)
        hHeader.setSectionResizeMode(Columns.numMessages, QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(Columns.dumpedAt, QHeaderView.ResizeToContents)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = tableView.verticalHeader()
        vHeader.setVisible(False)

        searchField = QLineEdit()
        searchField.setPlaceholderText("Enter queue name to find")
        searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)
        searchField.textChanged.connect(filterProxyModel.setFilterFixedString)

        layout = QVBoxLayout()
        layout.addWidget(tableView)
        layout.addWidget(searchField)

        self._tableView = tableView
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
