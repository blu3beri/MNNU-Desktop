import sys
from PyQt5 import QtWidgets, QtCore

from ui.MainWindow import Ui_MainWindow
from settings import Settings
from library.api_handler import ApiHandler


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Create timer for digital clock
        self.clockTimer = QtCore.QTimer(self)
        self.clockTimer.timeout.connect(self.showTime)
        self.clockTimer.start(1000)

        # Set handler for generate invite button
        self.generateInvite.clicked.connect(self.onGenerateInviteClicked)
        # Set handler for settings button
        self.actionInstellingen.triggered.connect(self.onSettingsMenuClicked)

    def showTime(self):
        time = QtCore.QTime.currentTime()
        self.lcdClock.display(time.toString("hh:mm"))

    def onSettingsMenuClicked(self):
        print("Clicked settings")
        settingsDialog = Settings()
        settingsDialog.exec_()
        ip = settingsDialog.ipvalue.text()
        port = int(settingsDialog.portvalue.text())
        print(f"Received: {ip}:{port}")

    def onGenerateInviteClicked(self):
        print("Clicked on generate invite")
        first_name = self.nameInput.text()
        middle_name = self.middleNameInput.text()
        last_name = self.lastNameInput.text()
        print(f"The following input was given: {first_name} {middle_name} {last_name}.")


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
