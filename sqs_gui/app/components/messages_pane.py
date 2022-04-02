from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, QModelIndex, QDateTime
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QLineEdit,
    QWidget,
)

from ..receiver import SQSMessage

from dataclasses import dataclass
from typing import List
from enum import Enum


class Columns(int, Enum):
    sendTimestamp = 0
    sendDate = 1
    messageBody = 2


@dataclass
class MessageItem:
    sendTimestamp: str
    sendDate: str
    messageBody: str

class CustomSortProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:

        filterRegExp = self.filterRegExp()
        if filterRegExp.isEmpty():
            return True

        sourceModel = self.sourceModel()
        indexBody = sourceModel.index(sourceRow, Columns.messageBody, sourceParent)
        return filterRegExp.indexIn(sourceModel.data(indexBody)) != -1

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:

        # No knowledge how to change sort column. First by default
        assert left.column() == Columns.sendTimestamp
        assert right.column() == Columns.sendTimestamp

        # Compare timestamp
        leftData = self.sourceModel().data(left)
        rightData = self.sourceModel().data(right)
        return int(leftData) > int(rightData)

    def sort(self, column: int, order: Qt.SortOrder) -> None:
        if column == Columns.sendTimestamp:
            super().sort(column, order)

class MessagesPane(QWidget):

    """Displays list of messages"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):

        labels = ["Send timestamp", "Send date", "Message body"]
        dataModel = QStandardItemModel(0, len(Columns))
        dataModel.setHorizontalHeaderLabels(labels)

        proxyModel = CustomSortProxyModel()
        proxyModel.setSourceModel(dataModel)
        proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        tableView = QTableView()
        tableView.setModel(proxyModel)
        tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.setColumnHidden(Columns.sendTimestamp, True)
        tableView.setSortingEnabled(True)

        hHeader = tableView.horizontalHeader()
        hHeader.setSectionResizeMode(QHeaderView.Interactive)
        hHeader.setSectionResizeMode(Columns.messageBody, QHeaderView.Stretch)
        # hHeader.resizeSections(QHeaderView.ResizeToContents)
        hHeader.setDefaultAlignment(Qt.AlignLeft)

        vHeader = tableView.verticalHeader()
        vHeader.setVisible(False)

        searchField = QLineEdit()
        searchField.setPlaceholderText("Search in message body")
        searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)
        searchField.textChanged.connect(proxyModel.setFilterFixedString)

        layout = QVBoxLayout()
        layout.addWidget(tableView)
        layout.addWidget(searchField)

        self._tableView = tableView
        self._dataModel = dataModel
        self.setLayout(layout)

    def clear(self):
        self._dataModel.clear()

    def addItem(self, item: MessageItem):

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        itemTimestamp = QStandardItem(item.sendTimestamp)
        itemTimestamp.setFlags(flags)

        itemDate = QStandardItem(item.sendDate)
        itemDate.setFlags(flags)

        itemBody = QStandardItem(item.messageBody)
        itemBody.setFlags(flags)

        row = [itemTimestamp, itemDate, itemBody]
        self._dataModel.appendRow(row)