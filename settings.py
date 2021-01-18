from PyQt5 import QtWidgets
from ui.settings import Ui_SettingsDialog

from library.api_handler import ApiHandler


class Settings(QtWidgets.QDialog, Ui_SettingsDialog):
    def __init__(self, api_instance: ApiHandler, parent=None):
        """
        Settings dialog class constructor
        :param api_instance: The ApiHandler instance
        :param parent: Not used, can be left empty
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.api = api_instance
        self.__setConnectionLabel()
        # Set handler for test connection button
        self.testConnectionBtn.clicked.connect(self.onTestConnectionClicked)

    def __setConnectionLabel(self):
        if self.api.test_connection():
            self.connstatus.setStyleSheet("color: rgb(12, 240, 14);")
            self.connstatus.setText("Verbonden")
        else:
            self.connstatus.setStyleSheet("color: rgb(255, 0, 0);")
            self.connstatus.setText("Niet verbonden")

    def onTestConnectionClicked(self):
        ip = self.ipvalue.text()
        port = int(self.portvalue.text() or 0)
        # Check if both values are correctly filled in
        if ip and port != 0:
            self.api.set_url(ip, port)
            self.__setConnectionLabel()
