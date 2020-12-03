import sys
from PyQt5 import QtWidgets, uic, QtCore

from ui.MainWindow import Ui_MainWindow
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
        self.generateinvite.clicked.connect(self.onGenerateInviteClicked)

    def showTime(self):
        time = QtCore.QTime.currentTime()
        self.lcdNumber.display(time.toString("hh:mm"))

    def onGenerateInviteClicked(self):
        print("Clicked on generate invite")
        first_name = self.nameinput.text()
        middle_name = self.middlenameinput.text()
        last_name = self.lastnameinput.text()
        print(f"The following input was given: {first_name} {middle_name} {last_name}.")


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
