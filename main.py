import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
import qrcode
import tempfile
import uuid
import re
import logging

from ui.MainWindow import Ui_MainWindow
from controller.settings import Settings
from controller.connections import Connections
from controller.records import Records
from library.api_handler import ApiHandler
from schemas.naw import naw
from helpers.requested_attribute_generator import generate_requested_attributes


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        # TODO: Create config file to save certain properties like the ACA-PY instance port/ip and medical profession
        # Docs: https://doc.qt.io/qt-5/qsettings.html
        # Disable the dialog help button globally
        QApplication.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton)

        # Setup logger
        logging.basicConfig(filename="MNNU-Desktop.log", level=logging.INFO)
        # Add handler to also log to the terminal
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info("Logging started...")

        # Create API Handler instance with default ip and port
        # TODO: Read ip and port from config if exists, otherwise use default values
        self.api = ApiHandler("localhost", 7001)
        # Disable the patient tabs on startup
        self.__patientTabsEnabled(False)

        # Configure available schemas
        self.schemas = {"NAW": naw, }

        #####################
        #  State variables  #
        #####################
        # Fill the patient selection box
        self.__fillPatientSelectionBox(self.api.get_active_connection_aliases())
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
        # Create timer to fill/update the patient records
        self.patientRecordsTimer = QtCore.QTimer(self)
        self.patientRecordsTimer.timeout.connect(self.__updatePatientRecords)

        ####################
        #     Handlers     #
        ####################
        # Set handler for generate invite button
        self.generateInvite.clicked.connect(self.onGenerateInviteClicked)
        # Set handler for settings button
        self.actionInstellingen.triggered.connect(self.onSettingsMenuClicked)
        # Set handler for pending connections button
        self.actionOpenstaandeConnectieVerzoeken.triggered.connect(self.onPendingConnectionsMenuClicked)
        # Set handler for pending records button
        self.actionOpenstaandeOpvraagGegevens.triggered.connect(self.onPendingRecordsMenuClicked)
        # Set handler for refresh patient
        self.refreshPatientBtn.clicked.connect(self.onRefreshPatientClicked)
        # Set handler for select patient
        self.confirmPatientBtn.clicked.connect(self.onSelectPatientClicked)
        # Set handler for delete patient
        self.deletePatientBtn.clicked.connect(self.onDeletePatientClicked)
        # Set handler for request records
        self.sendRequestBtn.clicked.connect(self.onSendRequestClicked)

        #############################
        #     Credential checks     #
        #############################
        # Check if the schemas are created and up-to-date
        if self.api.test_connection():
            self.__createSchemas(self.schemas)

    def __del__(self):
        """
        MainWindow class destructor
        :return: None
        """
        self.tempDir.cleanup()

    def __createInviteQr(self, invite: str) -> str:
        """
        Generate a connection invite qr-code
        :param invite: The Base64 encoded invite string
        :return: The full path to the generated qr image
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(invite)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        # Generate random filename
        filename = f"{self.tempDir.name}/{uuid.uuid4().hex}.png"
        img.save(filename)
        return filename

    def __createSchemas(self, schemas: dict) -> None:
        """
        Create schemas and place them on the chain
        :param schemas: The schema to create
        :return: None
        """
        for key, schema in schemas.items():
            exists = False
            for i in self.api.get_schemas():
                if i.split(':')[2:] == [schema["schema_name"], schema["schema_version"]]:
                    logging.info(f"The {key} schema exists and is up-to-date (version: {schema['schema_version']})")
                    exists = True
                    break
            if not exists:
                logging.info(f"The {key} schema does not exist or is not up-to-date, creating...")
                self.api.create_schema(schema=schema)
        logging.info("All schemas are up-to-date and created!")

    def __showTime(self) -> None:
        """
        Show the time on the main page (Function is attached to a QTimer object)
        :return: None
        """
        time = QtCore.QTime.currentTime()
        if (time.second() % 2) == 0:
            self.lcdClock.display(time.toString("hh:mm"))
        else:
            self.lcdClock.display(time.toString("hh mm"))
        self.clockTimer.setInterval(1000)  # Set the interval to update the time every second

    def __updateGreetings(self) -> None:
        """
        Show a greetings message on the main page (Function is attached to a QTimer object)
        :return: None
        """
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

    @staticmethod
    def __fillRecordTable(table: QtWidgets.QTableWidget, records: dict) -> None:
        """
        Fill the supplied table with the supplied records
        :param table: The table to fill
        :param records: The records to fill the table with
        :return: None
        """
        # TODO: Reformat the records so they are back in their original order
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        i = 0
        table.setRowCount(len(records))
        for key, value in records.items():
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(value))
            i += 1

    def __updatePatientRecords(self) -> None:
        """
        Update all patient record (tables)
        :return: None
        """
        logging.info("Refreshing patient records")
        self.patientRecordsTimer.setInterval(60000)  # Change interval to only check every minute (POC)
        records = self.api.get_verified_proof_records(self.api.get_connection_id(self.currentAlias))
        # TODO: Add support for more record types here
        if "NAW" in records:
            self.__fillRecordTable(self.nawTable, records["NAW"])

    def __patientTabsEnabled(self, state: bool) -> None:
        """
        Enable or disable the patient tabs
        :param state: True (enabled), False (Disabled)
        :return: None
        """
        for i in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, state)

    def __fillPatientSelectionBox(self, patients: list) -> None:
        """
        Fill the patient selection box with the given patient list
        :param patients: The list of patients to fill the selection box with
        :return: None
        """
        patients = ["-- Selecteer patiënt --"] + sorted(patients, key=str.lower)
        self.selectPatientBox.clear()
        self.selectPatientBox.addItems(patients)
        self.selectPatientBox.setCurrentIndex(0)
        # If the patientBox is empty eq 1 disable the patient tabs
        if self.selectPatientBox.count() == 1:
            self.__patientTabsEnabled(False)

    #############################
    #      Button handlers      #
    #############################

    def onSettingsMenuClicked(self) -> None:
        """
        Handler for the Settings menu button
        :return: None
        """
        logging.info("Clicked settings menu")
        settings_dialog = Settings(self.api)
        settings_dialog.exec_()
        logging.info("Settings menu closed")
        profession = settings_dialog.professionComboBox.currentText()
        if not profession or settings_dialog.professionComboBox.currentIndex() == 0:
            logging.info("No profession selected")
            return
        logging.info(f"Selected profession: {profession}")
        # TODO: Save medical profession

    def onPendingConnectionsMenuClicked(self) -> None:
        """
        Handler for the pending connections button
        :return: None
        """
        logging.info("Clicked Pending Connections menu")
        connections_dialog = Connections(self.api)
        connections_dialog.exec()

    def onPendingRecordsMenuClicked(self) -> None:
        """
        Handler for the pending records button
        :return: None
        """
        logging.info("Clicked Pending Records menu")
        records_dialog = Records(self.api)
        records_dialog.exec()

    def onRefreshPatientClicked(self) -> None:
        """
        Handler for the refresh patient (list) button
        :return: None
        """
        logging.info("Clicked on refresh patient")
        self.__fillPatientSelectionBox(self.api.get_active_connection_aliases())

    def onSelectPatientClicked(self) -> None:
        """
        Handler for the select patient button
        :return: None
        """
        logging.info("Clicked on select patient")
        alias = self.selectPatientBox.currentText()
        if not alias or self.selectPatientBox.currentIndex() == 0:
            logging.info("No patient selected")
            # Disable updating of patient record tabs
            self.patientRecordsTimer.stop()
            # Disable the patient tabs and clear the current alias variable
            self.__patientTabsEnabled(False)
            self.currentAlias = None
            return
        # Enable the patient tabs since a patient is selected
        self.__patientTabsEnabled(True)
        self.currentAlias = alias
        logging.info(f"Selected alias: {alias} with conn_id: {self.api.get_connection_id(self.currentAlias)}")
        self.patientRecordsTimer.start(1)  # Do the update instantly

    def onDeletePatientClicked(self) -> None:
        """
        Handler for the delete patient button
        :return: None
        """
        logging.info("Clicked on delete patient")
        alias = self.selectPatientBox.currentText()
        if not alias or self.selectPatientBox.currentIndex() == 0:
            return
        # Create a popup to ask for a confirmation
        action = QMessageBox.warning(self,
                                     'Verwijder connectie',
                                     f"Weet je zeker dat je de connnectie met {alias} wilt verwijderen?",
                                     QMessageBox.Yes | QMessageBox.No
                                     )
        if action == QMessageBox.Yes:
            logging.info(f"Deleting connection with alias: {alias}")
            if not self.api.delete_connection(self.api.get_connection_id(alias)):
                logging.warning("Unable to delete connection with given alias")
            # Refresh the active connection box list
            self.__fillPatientSelectionBox(self.api.get_active_connection_aliases())
        else:
            # User pressed No, do nothing
            return

    def onGenerateInviteClicked(self) -> None:
        """
        Handler for the generate invite button
        :return: None
        """
        logging.info("Clicked on generate invite")
        self.connLabel.setText("")  # Reset the conn label when button is pressed
        f_name = self.nameInput.text()
        m_name = self.middleNameInput.text()
        l_name = self.lastNameInput.text()
        bsn = self.bsnInput.text()
        # Check if at least fist_name and last_name are filled in
        if not f_name or not l_name:
            logging.warning("First name and/or last name is empty")
            self.connLabel.setText("Voornaam en/of achternaam is leeg")
            return
        # Check if the BSN is valid using a regular expression
        elif not re.match(r"^[0-9]{9}$", bsn):
            logging.warning("BSN is empty")
            self.connLabel.setText("BSN is leeg of klopt niet")
            return
        # Generate invitation url
        if self.api.test_connection():
            alias = f"{f_name} {m_name + ' ' if m_name else ''}{l_name} {bsn}"
            logging.info(f"The following input was given: {alias}")
            # Check if a connection with this alias already exists
            conn = self.api.get_connections(alias=alias)["results"]
            if len(conn):
                logging.warning("Connection already exists with this alias")
                self.connLabel.setText(f"Er bestaat al een connectie met deze naam\n"
                                       f"De status van deze connectie is: {conn[0]['state']}")
                return  # Don't execute the rest of the code since we don't want duplicates
            # Create a new invitation
            conn_id, invite = self.api.create_invitation(
                alias=alias,
                multi_use=False,
                auto_accept=True)
            logging.info(f"Generated invite: {invite}")
            # TODO: Check QT docs on how to scale the image properly, remove qr when connection is established
            self.qrCodeLabel.setPixmap(QtGui.QPixmap(self.__createInviteQr(invite=invite)).scaled(224, 224))
            return
        self.connLabel.setText("Geen verbinding mogelijk met ACA-PY.\n"
                               "Staat de server aan en is de juiste ip/poort ingesteld?")
        logging.warning("Connection to ACA-PY failed, is the instance running and are the correct ip/port specified?")

    def onSendRequestClicked(self) -> None:
        """
        Handler for the send request button (request patient record)
        :return: None
        """
        requested_record = self.recordTypeBox.currentText()
        reason = self.reasonText.toPlainText()
        if not requested_record or self.recordTypeBox.currentIndex() == 0:
            logging.info("No record selected")
            self.sendRequestLabel.setStyleSheet("color: rgb(255, 0, 0);")
            self.sendRequestLabel.setText("Er is geen type geselecteerd")
            return
        conn_id = self.api.get_connection_id(self.currentAlias)
        logging.info(
            f"Requested record type:{requested_record} to connection alias:{self.currentAlias} with conn id:{conn_id}"
        )
        self.api.send_proof_request(
            conn_id=conn_id,
            requested_attributes=generate_requested_attributes(self.schemas[requested_record]),
            requested_predicates={},
            name=requested_record,
            comment=reason if reason else "Geen reden opgegeven"
        )
        self.sendRequestLabel.setStyleSheet("color: rgb(12, 240, 14);")
        self.sendRequestLabel.setText("Verzoek is verstuurd")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
