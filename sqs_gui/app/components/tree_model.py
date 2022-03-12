from __future__ import annotations
from typing import List, Optional, Any

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt5.QtWidgets import QWidget

# See https://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
# See https://doc.qt.io/qt-5/qtwidgets-itemviews-editabletreemodel-example.html


class TreeItem:

    _dataItems: List[str]
    _dataItemsEditable: List[bool]
    _children: List[TreeItem]
    _parent: Optional[TreeItem]

    def __init__(
        self,
        dataItems: List[str] = [],
        parent: Optional[TreeItem] = None,
    ) -> None:
        self._dataItemsEditable = [False for _ in range(len(dataItems))]
        self._dataItems = dataItems
        self._parent = parent
        self._children = []

    def isEditable(self, column: int):

        if column < 0 or column > len(self._dataItemsEditable):
            return False

        return self._dataItemsEditable[column]

    def setEditable(self, column: int, isEditable: bool):

        if column < 0 or column > len(self._dataItemsEditable):
            return False

        self._dataItemsEditable[column] = isEditable
        return True

    def data(self, column: int):

        if column < 0 or column > len(self._dataItems):
            return None

        return self._dataItems[column]

    def setData(self, column: int, data: str) -> bool:

        if column < 0 or column > len(self._dataItems):
            return False

        self._dataItems[column] = data
        return True

    def child(self, row: int):

        if row < 0 or row > len(self._children):
            return None

        return self._children[row]

    def addChild(self, item: TreeItem):
        item._parent = self
        self._children.append(item)

    def insertChildren(self, position: int, count: int, columns: int):

        if position < 0 or position > len(self._children):
            return False

        for _ in range(count):
            dataItems = [None] * columns
            item = TreeItem(dataItems, self)
            self._children.insert(position, item)

        return True

    def removeChildren(self, position: int, count: int):

        if position < 0 or position > len(self._children):
            return False

        for _ in range(count):
            del self._children[position]

        return True

    def insertColumns(self, position: int, columns: int):

        if position < 0 or position > len(self._dataItems):
            return False

        for _ in range(columns):
            self._dataItems.insert(position, None)

        for child in self._children:
            child.insertColumns(position, columns)

        return True

    def removeColumns(self, position: int, columns: int):

        if position < 0 or position > len(self._dataItems):
            return False

        for _ in range(columns):
            del self._dataItems[position]

        for child in self._children:
            child.removeColumns(position, columns)

        return True

    def removeChild(self, item: TreeItem):
        self._children.remove(item)

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

    def parentItem(self):
        return self._parent


class CustomTreeModel(QAbstractItemModel):

    _rootItem: TreeItem

    def __init__(
        self,
        headers: TreeItem,
        parent: QWidget,
    ):
        super().__init__(parent)
        self._rootItem = headers

    def setItems(self, treeItems: List[TreeItem]):

        self.layoutAboutToBeChanged.emit()
        self.removeRows(0, self.rowCount())

        for item in treeItems:
            self._rootItem.addChild(item)

        self.layoutChanged.emit()

    def itemFromIndex(self, index: QModelIndex) -> TreeItem:

        if not index.isValid():
            return self._rootItem

        return index.internalPointer()

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem = self.itemFromIndex(parent)
        childItem = parentItem.child(row)

        if not childItem:
            return QModelIndex()

        return self.createIndex(row, column, childItem)

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:

        childItem = self.itemFromIndex(index)
        parentItem = childItem.parentItem()

        if not parentItem or parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:

        if parent.column() > 0:
            return 0

        parentItem = self.itemFromIndex(parent)
        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._rootItem.columnCount()

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
        item = self.itemFromIndex(index)

        if item.isEditable(index.column()):
            return defaultFlags | Qt.ItemIsEditable

        return defaultFlags

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:

        if not index.isValid():
            return False

        if role != Qt.EditRole:
            return False

        if not value:
            return False

        item: TreeItem = index.internalPointer()
        result = item.setData(index.column(), value)

        if result:
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])

        return result

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._rootItem.data(section)

        return None

    def setHeaderData(
        self, section: int, orientation: Qt.Orientation, value: Any, role: int
    ) -> bool:

        if role != Qt.EditRole or orientation != Qt.Horizontal:
            return False

        result = self._rootItem.setData(section, value)

        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def insertRows(
        self, row: int, count: int, parent: QModelIndex = QModelIndex()
    ) -> bool:
        parentItem = self.itemFromIndex(parent)
        self.beginInsertRows(parent, row, row + count - 1)
        status = parentItem.insertChildren(row, count, self.columnCount())
        self.endInsertRows()
        return status

    def insertRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        return self.insertRows(row, 1, parent)

    def insertColumns(
        self, column: int, count: int, parent: QModelIndex = QModelIndex()
    ) -> bool:
        self.beginInsertColumns(parent, column, column + count - 1)
        status = self._rootItem.insertColumns(column, count)
        self.endInsertColumns()
        return status

    def insertColumn(self, column: int, parent: QModelIndex = QModelIndex()) -> bool:
        return self.insertColumns(column, 1, parent)

    def removeRows(
        self, row: int, count: int, parent: QModelIndex = QModelIndex()
    ) -> bool:
        parentItem = self.itemFromIndex(parent)
        self.beginRemoveRows(parent, row, row + count - 1)
        status = parentItem.removeChildren(row, count)
        self.endRemoveRows()
        return status

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.removeRows(row, 1, parent)

    def removeColumns(self, column: int, count: int, parent: QModelIndex) -> bool:

        self.beginRemoveColumns(parent, column, column + count - 1)
        status = self._rootItem.removeColumns(column, count)
        self.endRemoveColumns()

        if self._rootItem.columnCount() == 0:
            self.removeRows(0, self.rowCount())

        return status

    def removeColumn(self, column: int, parent: QModelIndex = QModelIndex()) -> bool:
        return self.removeColumns(column, 1, parent)
