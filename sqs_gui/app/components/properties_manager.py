from __future__ import annotations
from typing import List, Optional, Any

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

# See https://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html

class TreeItem:

    _dataItems: List[str]
    _children: List[TreeItem]
    _parent: Optional[TreeItem]

    def __init__(
        self,
        dataItems: List[str] = [],
        parent: Optional[TreeItem] = None,
    ) -> None:
        self._dataItems = dataItems
        self._parent = parent
        self._children = []

    def child(self, row: int):

        if row < 0 or row > len(self._children):
            return None

        return self._children[row]


    def addChild(self, item: TreeItem):
        item.setParentItem(self)
        self._children.append(item)

    def childCount(self):
        return len(self._children)

    def childIndex(self, item: TreeItem):
        return self._children.index(item)

    def row(self):

        if self._parent is None:
            return 0

        return self._parent.childIndex(self)

    def columnCount(self):
        return len(self._dataItems)

    def data(self, column: int):

        if column < 0 or column > len(self._dataItems):
            return None

        return self._dataItems[column]

    def setData(self, column: int, data: str) -> bool:

        if column < 0 or column > len(self._dataItems):
            return False

        self._dataItems[column] = data
        return True

    def parentItem(self):
        return self._parent

    def setParentItem(self, item: TreeItem):
        self._parent = item


class MyTreeModel(QAbstractItemModel):

    _rootItem: TreeItem
    _numColumns: int

    def __init__(
        self,
        headers: TreeItem,
        parent: QWidget,
    ):
        super().__init__(parent)
        self._rootItem = headers
        self._numColumns = headers.columnCount()

    def setTreeItems(self, treeItems: List[TreeItem]):

        # def rm(items: TreeItem):

        #     for item in items:
        #         if item._children:
        #             rm(item._children)

        #     item._parent = None
        #     item._children = []

        # rm([self._rootItem])

        self._rootItem._children = []
        for item in treeItems:
            assert item.columnCount() == self._numColumns
            self._rootItem.addChild(item)

    def itemFromIndex(self, index: QModelIndex) -> TreeItem:

        if not index.isValid():
            return self._rootItem

        return index.internalPointer()

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem = self.itemFromIndex(parent)
        childItem = parentItem.child(row)

        if not childItem:
            return QModelIndex()

        return self.createIndex(row, column, childItem)

    def parent(self, index: QModelIndex) -> QModelIndex:

        childItem = self.itemFromIndex(index)
        parentItem = childItem.parentItem()

        assert parentItem is not None
        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent: QModelIndex) -> int:

        if parent.column() > 0:
            return 0

        parentItem = self.itemFromIndex(parent)
        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex) -> int:
        return self._numColumns

    def data(self, index: QModelIndex, role: int) -> Any:

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item: TreeItem = index.internalPointer()
        return item.data(index.column())

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:

        if not index.isValid():
            return Qt.NoItemFlags

        defaultFlags = super().flags(index)
        return defaultFlags

        if index.column() == 0:
            return defaultFlags

        return defaultFlags | Qt.ItemIsEditable

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:

        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        if not value:
            return False

        item: TreeItem = index.internalPointer()
        return item.setData(index.column(), value)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._rootItem.data(section)

        return None