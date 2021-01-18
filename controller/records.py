from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime
from ui.pending_records import Ui_PendingRecordsDialog
import logging
import resource_rc  # Used for loading images

from library.api_handler import ApiHandler


class Records(QtWidgets.QDialog, Ui_PendingRecordsDialog):
    def __init__(self, api_instance: ApiHandler, parent=None):
        """
        Records dialog class constructor
        :param api_instance: The ApiHandler instance
        :param parent: Not used, can be left empty
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.api = api_instance
        # Resize headers section
        header = self.tableWidget.horizontalHeader()
        for i in range(3):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        # Load icon
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(":/images/img/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # Fill the table widget with proof records
        self.__fillTable()

        # Set handler for refresh button
        self.refreshBtn.clicked.connect(self.__refreshButtonHandler)

    def __refreshButtonHandler(self):
        logging.info("Clicked on refresh button")
        self.__fillTable()

    def __verifyButtonHandler(self, presentation_exchange_id: str):
        logging.info("Clicked on removeButtonHandler")
        response = self.api.verify_presentation(presentation_exchange_id)
        print(response)
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.pos()).row()
            self.tableWidget.removeRow(row)

    def __fillTable(self):
        all_records = []
        [all_records.append(i) for i in self.api.get_proof_records(state="presentation_received")]
        [all_records.append(i) for i in self.api.get_proof_records(state="request_sent")]
        self.tableWidget.setRowCount(len(all_records))
        print(all_records)
        # Fill the table with the received presentations first
        for i, item in enumerate(all_records):
            alias = self.api.get_alias_by_conn_id(conn_id=item["connection_id"])
            if alias is None:
                continue
            if item["state"] == "presentation_received":
                btn = QtWidgets.QPushButton(self.tableWidget)
                btn.setMinimumSize(QtCore.QSize(0, 27))
                btn.setText("Verifieer")
                btn.setIcon(self.icon)
                btn.clicked.connect(lambda: self.__verifyButtonHandler(item["pres_ex_id"]))
                self.tableWidget.setCellWidget(i, 4, btn)
            else:
                self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem("Verzoek verstuurd"))
            name = " ".join(alias.split(" ")[:2])
            bsn = alias.split(" ")[2]
            date = datetime.fromisoformat(item["created_at"]).strftime("%d %B %Y om %H:%M")
            # Fill the table
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(bsn))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(item["type"]))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(date))
