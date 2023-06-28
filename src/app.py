from PyQt5 import QtWidgets, uic
import sys

class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.show()

app = QtWidgets.QApplication(sys.argv)
window = UI()
app.exec_()