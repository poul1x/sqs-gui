import sys
from PyQt5.QtWidgets import QApplication
from .components.main_window import MyWindow

def runApp():

    app = QApplication(sys.argv)

    myWindow = MyWindow()
    myWindow.show()

    sys.exit(app.exec())