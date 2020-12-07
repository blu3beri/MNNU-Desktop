import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import qrcode
import tempfile
import uuid

from ui.MainWindow import Ui_MainWindow
from settings import Settings
from library.api_handler import ApiHandler


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Create API Handler instance with default ip and port
        self.api = ApiHandler("localhost", 7001)

        # Temp dir for images and misc stuff will be removed when program closes
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create timer for digital clock
        self.clockTimer = QtCore.QTimer(self)
        self.clockTimer.timeout.connect(self.showTime)
        self.clockTimer.start(1000)

        # Set handler for generate invite button
        self.generateInvite.clicked.connect(self.onGenerateInviteClicked)
        # Set handler for settings button
        self.actionInstellingen.triggered.connect(self.onSettingsMenuClicked)

    def __del__(self):
        self.temp_dir.cleanup()

    def __createInviteQr(self, invite) -> str:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(invite)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        # Generate random filename
        filename = f"{self.temp_dir.name}/{uuid.uuid4().hex}.png"
        img.save(filename)
        return filename

    def showTime(self):
        time = QtCore.QTime.currentTime()
        self.lcdClock.display(time.toString("hh:mm"))

    def onSettingsMenuClicked(self):
        print("Clicked settings")
        settings_dialog = Settings(self.api)
        settings_dialog.exec_()
        print("Settings menu closed")

    def onGenerateInviteClicked(self):
        print("Clicked on generate invite")
        f_name = self.nameInput.text()
        m_name = self.middleNameInput.text()
        l_name = self.lastNameInput.text()
        # Check if at least fist_name and last_name are filled in
        if not f_name or not l_name:
            print("First name and/or last name is empty")
            # TODO: Add label to GUI to notify user of missing input field values
            return
        # Generate invitation url
        if self.api.test_connection():
            print(f"The following input was given: {f_name} {m_name+' ' if m_name else ''}{l_name}.")
            conn_id, invite = self.api.create_invitation(
                alias=f"{f_name} {m_name+' ' if m_name else ''}{l_name}",
                multi_use=False,
                auto_accept=False)
            print(f"Generated invite: {invite}")
            self.qrCodeLabel.setPixmap(QtGui.QPixmap(self.__createInviteQr(invite=invite)).scaled(224, 224))
            print(self.temp_dir.name)
            return
        # TODO: To the same label, notify user that the connection to the API failed thus no invite was created
        print("Connection to ACA-PY failed, is the instance running and are the correct ip/port specified?")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
