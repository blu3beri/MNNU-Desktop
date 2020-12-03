from PyQt5 import QtWidgets
from ui.settings import Ui_Dialog


class Settings(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
