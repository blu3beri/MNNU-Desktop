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
        # TODO: Create config file to save certain properties like the ACA-PY instance port/ip

        # Create API Handler instance with default ip and port
        self.api = ApiHandler("localhost", 7001)

        # Temp dir for images and misc stuff will be removed when program closes
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create timer for digital clock
        self.clockTimer = QtCore.QTimer(self)
        self.clockTimer.timeout.connect(self.__showTime)
        self.clockTimer.start(1)  # Update the time (almost) instant upon start

        # Create timer for greetings text
        self.greetingsTimer = QtCore.QTimer(self)
        self.greetingsTimer.timeout.connect(self.__updateGreetings)
        self.greetingsTimer.start(1)  # Update the greeting (almost) instant upon start

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

    def __showTime(self):
        time = QtCore.QTime.currentTime()
        self.lcdClock.display(time.toString("hh:mm"))
        self.clockTimer.setInterval(1000)  # Set the interval to update the time every second

    def __updateGreetings(self):
        # Check if there is an valid connection and then get the agent name
        if self.api.test_connection():
            agent = self.api.get_agent_name().replace("_", " ")
        else:
            # TODO: Make sure message is clear to end user and not too technical
            self.welcomeLabel.setText("Geen verbinding met agent")
            self.greetingsTimer.setInterval(10000)  # Update the greeting every second if there is no connection
            return
        # Get the current time
        time = QtCore.QTime.currentTime()
        # TODO: Should probably also check the minutes
        if time.hour() <= 12:
            greeting = "Goedemorgen"
        elif 13 <= time.hour() <= 18:
            greeting = "Goedemiddag"
        else:
            greeting = "Goedenavond"
        self.welcomeLabel.setText(f"{greeting} {agent}")
        self.greetingsTimer.setInterval(60000)  # Set the interval to only check every minute

    def onSettingsMenuClicked(self):
        print("Clicked settings")
        settings_dialog = Settings(self.api)
        settings_dialog.exec_()
        print("Settings menu closed")

    def onGenerateInviteClicked(self):
        print("Clicked on generate invite")
        self.connLabel.setText("")  # Reset the conn label when button is pressed
        f_name = self.nameInput.text()
        m_name = self.middleNameInput.text()
        l_name = self.lastNameInput.text()
        # Check if at least fist_name and last_name are filled in
        if not f_name or not l_name:
            print("First name and/or last name is empty")
            self.connLabel.setText("Voornaam en/of achternaam is leeg")
            return
        # Generate invitation url
        if self.api.test_connection():
            alias = f"{f_name} {m_name+' ' if m_name else ''}{l_name}"
            print(f"The following input was given: {alias}")
            # Check if a connection with this alias already exists
            conn = self.api.get_connections(alias=alias)["results"]
            if len(conn):
                print("Connection already exists with this alias")
                self.connLabel.setText(f"Er bestaat al een connectie met deze naam\n"
                                       f"De status van deze connectie is: {conn[0]['state']}")
                return  # Don't execute the rest of the code since we don't want duplicates
            # Create a new invitation
            conn_id, invite = self.api.create_invitation(
                alias=alias,
                multi_use=False,
                auto_accept=False)
            print(f"Generated invite: {invite}")
            self.qrCodeLabel.setPixmap(QtGui.QPixmap(self.__createInviteQr(invite=invite)).scaled(224, 224))
            # TODO: Check QT docs on how to scale the image properly, remove qr when connection is established
            return
        self.connLabel.setText("Geen verbinding mogelijk met ACA-PY.\n"
                               "Staat de server aan en is de juiste ip/poort ingesteld?")
        print("Connection to ACA-PY failed, is the instance running and are the correct ip/port specified?")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
