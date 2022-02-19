from typing import Dict, Optional
from enum import Enum

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import (
    QTreeView,
    QHeaderView,
    QVBoxLayout,
    QLineEdit,
    QWidget,
)

from .tree_model import TreeItem, CustomTreeModel

# TODO: set some items to True when editing will be implemented
_PROPS_EDITABLE = {
    "ApproximateNumberOfMessages": False,
    "ApproximateNumberOfMessagesDelayed": False,
    "ApproximateNumberOfMessagesNotVisible": False,
    "ContentBasedDeduplication": False,
    "CreatedTimestamp": False,
    "DeduplicationScope": False,
    "DelaySeconds": False,
    "FifoQueue": False,
    "FifoThroughputLimit": False,
    "KmsDataKeyReusePeriodSeconds": False,
    "KmsMasterKeyId": False,
    "LastModifiedTimestamp": False,
    "MaximumMessageSize": False,
    "MessageRetentionPeriod": False,
    "Policy": False,
    "QueueArn": False,
    "ReceiveMessageWaitTimeSeconds": False,
    "RedriveAllowPolicy": False,
    "RedrivePolicy": False,
    "SqsManagedSseEnabled": False,
    "VisibilityTimeout": False,
}


class Columns(int, Enum):
    propName = 0
    propValue = 1


class SpecialValues(str, Enum):
    empty = "<Empty>"
    unknown = "<Unknown>"


class MQPropertiesPane(QWidget):

    """Shows message queue attributes, tags, etc..."""

    _propsModel: CustomTreeModel
    _propsTree: QTreeView

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        headers = TreeItem(["Property name", "Value"])
        self._propsModel = CustomTreeModel(headers, self)

        filterProxyModel = QSortFilterProxyModel(self)
        filterProxyModel.setSourceModel(self._propsModel)
        filterProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filterProxyModel.setRecursiveFilteringEnabled(True)

        self._propsTree = QTreeView()
        self._propsTree.setModel(filterProxyModel)

        header = self._propsTree.header()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.resizeSections(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        searchField = QLineEdit()
        searchField.setPlaceholderText("Enter property name to find")
        searchField.addAction(QIcon(":search.svg"), QLineEdit.LeadingPosition)
        searchField.textChanged.connect(filterProxyModel.setFilterFixedString)

        layout = QVBoxLayout()
        layout.addWidget(self._propsTree)
        layout.addWidget(searchField)
        self.setLayout(layout)

    def setItems(
        self,
        queueAttrs: Dict[str, Optional[str]],
        queueTags: Dict[str, str],
    ):

        rightVal = "" if queueAttrs else SpecialValues.empty.value
        itemAttrs = TreeItem(["Attributes", rightVal])

        for name, value in queueAttrs.items():
            item = TreeItem([name, value or SpecialValues.unknown])
            item.setEditable(Columns.propValue, _PROPS_EDITABLE[name])
            itemAttrs.addChild(item)

        rightVal = "" if queueTags else SpecialValues.empty.value
        itemTags = TreeItem(["Tags", rightVal])

        for name, value in queueTags.items():
            item = TreeItem([name, value])
            # TODO: set to True when will be implemented
            item.setEditable(Columns.propValue, False)
            itemTags.addChild(item)

        self._propsModel.setItems([itemAttrs, itemTags])
        self._propsTree.expandAll()
