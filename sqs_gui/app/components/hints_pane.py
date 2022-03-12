from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QWidget,
    QLabel,
)

class HintsPane(QWidget):

    """Displays list of messages"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.initUserInterface()

    def initUserInterface(self):
        layout = QVBoxLayout()
        label = QLabel("Double click on queue name to load messages")
        layout.addWidget(label)
        self.setLayout(layout)


