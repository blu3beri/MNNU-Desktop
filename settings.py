from PyQt5 import QtWidgets
from ui.settings import Ui_Dialog

from library.api_handler import ApiHandler


class Settings(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, api_instance: ApiHandler, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.api = api_instance

        # Set handler for test connection button
        self.testConnectionBtn.clicked.connect(self.onTestConnectionClicked)

    def onTestConnectionClicked(self):
        ip = self.ipvalue.text()
        port = int(self.portvalue.text() or 0)
        # Check if both values are correctly filled in
        if ip and port is not 0:
            self.api.set_url(ip, port)
            if self.api.test_connection():
                self.connstatus.setStyleSheet("color: rgb(0, 255, 0);")
                self.connstatus.setText("Verbonden")
            else:
                self.connstatus.setStyleSheet("color: rgb(255, 0, 0);")
                self.connstatus.setText("Niet verbonden")
