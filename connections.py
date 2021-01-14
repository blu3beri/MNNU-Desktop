from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime
from ui.connections import Ui_PendingConnectionsDialog
import resource_rc

from library.api_handler import ApiHandler


class Connections(QtWidgets.QDialog, Ui_PendingConnectionsDialog):
    def __init__(self, api_instance: ApiHandler, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.api = api_instance
        # Resize section
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        # Load icon
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(":/images/img/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.__fillTable()

    def __removeButtonHandler(self, connection_id):
        print("Clicked on removeButtonHandler")
        self.api.delete_connection(connection_id)
        button = self.sender()
        if button:
            row = self.tableWidget.indexAt(button.pos()).row()
            self.tableWidget.removeRow(row)

    def __fillTable(self):
        pending = self.api.get_pending_connections()
        self.tableWidget.setRowCount(len(pending))
        for i, connection in enumerate(pending):
            btn = QtWidgets.QPushButton(self.tableWidget)
            btn.setMinimumSize(QtCore.QSize(0, 27))
            btn.setText("Verwijder")
            btn.setIcon(self.icon)
            btn.clicked.connect(lambda: self.__removeButtonHandler(connection["connection_id"]))
            alias = " ".join(connection["alias"].split(" ")[:2])
            bsn = connection["alias"].split(" ")[2]
            date = datetime.fromisoformat(connection["created_at"]).strftime("%d %B %Y om %H:%M")
            # Fill the table
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(alias))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(bsn))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(date))
            self.tableWidget.setCellWidget(i, 3, btn)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.viewport().update()
