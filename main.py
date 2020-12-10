import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import qrcode
import tempfile
import uuid
import re

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
        # Disable the patient tabs on startup
        self.__patientTabsEnabled(False)

        #####################
        #  State variables  #
        #####################
        # List of active connection aliases
        self.activeAliases = self.__getActiveConnectionAliases()
        # Fill the patient selection box
        self.__fillPatientSelectionBox(self.activeAliases)
        # Temp dir for images and misc stuff will be removed when program closes
        self.tempDir = tempfile.TemporaryDirectory()
        # Keep track of the current alias
        self.currentAlias = None

        ####################
        #      Timers      #
        ####################
        # Create timer for digital clock
        self.clockTimer = QtCore.QTimer(self)
        self.clockTimer.timeout.connect(self.__showTime)
        self.clockTimer.start(1)  # Update the time (almost) instant upon start
        # Create timer for greetings text
        self.greetingsTimer = QtCore.QTimer(self)
        self.greetingsTimer.timeout.connect(self.__updateGreetings)
        self.greetingsTimer.start(1)  # Update the greeting (almost) instant upon start

        ####################
        #     Handlers     #
        ####################
        # Set handler for generate invite button
        self.generateInvite.clicked.connect(self.onGenerateInviteClicked)
        # Set handler for settings button
        self.actionInstellingen.triggered.connect(self.onSettingsMenuClicked)
        # Set handler for select patient
        self.confirmPatientBtn.clicked.connect(self.onSelectPatientClicked)

    def __del__(self):
        self.tempDir.cleanup()

    def __createInviteQr(self, invite: str) -> str:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(invite)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        # Generate random filename
        filename = f"{self.tempDir.name}/{uuid.uuid4().hex}.png"
        img.save(filename)
        return filename

    def __getActiveConnectionAliases(self) -> list:
        aliases = []
        # If there is no active connection, return an empty list
        if not self.api.test_connection():
            return aliases
        connections = self.api.get_connections(state="active")["results"]
        for connection in connections:
            # Check if the connection actually has an alias
            if "alias" not in connection:
                continue
            else:
                aliases.append(connection["alias"])
        return aliases

    def __showTime(self) -> None:
        time = QtCore.QTime.currentTime()
        self.lcdClock.display(time.toString("hh:mm"))
        self.clockTimer.setInterval(1000)  # Set the interval to update the time every second

    def __updateGreetings(self) -> None:
        # Check if there is an valid connection and then get the agent name
        if self.api.test_connection():
            agent = self.api.get_agent_name().replace("_", " ")
        else:
            # TODO: Make sure message is clear to end user and not too technical
            self.welcomeLabel.setText("Geen verbinding met agent")
            self.greetingsTimer.setInterval(10000)  # Update the greeting every 10 seconds if there is no connection
            return
        # Get the current time
        time = int(QtCore.QTime.currentTime().toString("hhmm"))
        if time <= 1200:
            greeting = "Goedemorgen"
        elif 1201 <= time <= 1800:
            greeting = "Goedemiddag"
        else:
            greeting = "Goedenavond"
        self.welcomeLabel.setText(f"{greeting} {agent}")
        self.greetingsTimer.setInterval(60000)  # Set the interval to only check every minute

    def __patientTabsEnabled(self, state: bool) -> None:
        for i in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, state)

    def __fillPatientSelectionBox(self, patients: list) -> None:
        self.selectPatientBox.clear()
        self.selectPatientBox.addItems(sorted(patients, key=str.lower))

    def onSettingsMenuClicked(self) -> None:
        print("Clicked settings")
        settings_dialog = Settings(self.api)
        settings_dialog.exec_()
        print("Settings menu closed")

    def onSelectPatientClicked(self) -> None:
        print("Clicked on select patient")
        alias = self.selectPatientBox.currentText()
        if not alias:
            print("No patient selected")
            return
        print(f"Alias: {alias}")

    def onGenerateInviteClicked(self) -> None:
        print("Clicked on generate invite")
        self.connLabel.setText("")  # Reset the conn label when button is pressed
        f_name = self.nameInput.text()
        m_name = self.middleNameInput.text()
        l_name = self.lastNameInput.text()
        bsn = self.bsnInput.text()
        # Check if at least fist_name and last_name are filled in
        if not f_name or not l_name:
            print("First name and/or last name is empty")
            self.connLabel.setText("Voornaam en/of achternaam is leeg")
            return
        elif not re.match(r"^[0-9]{9}$", bsn):
            print("BSN is empty")
            self.connLabel.setText("BSN is leeg of klopt niet")
            return
        # Generate invitation url
        if self.api.test_connection():
            alias = f"{f_name} {m_name+' ' if m_name else ''}{l_name} {bsn}"
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
