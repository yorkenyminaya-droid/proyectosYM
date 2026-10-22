from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt


class ClientList(QTableWidget):

    def __init__(self):
        super().__init__()

        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([
            "Código",
            "Nombre",
            "Documento",
            "Teléfono",
        ])

        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)

        # Ajustar columnas para ocupar el ancho disponible
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    def load_clients(self, clients):

        self.clearContents()
        self.setRowCount(0)

        for client in clients:

            row = self.rowCount()
            self.insertRow(row)

            item_code = QTableWidgetItem(client.code)
            item_code.setData(Qt.ItemDataRole.UserRole, client.id)

            self.setItem(row, 0, item_code)

            self.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{client.first_name} {client.last_name}"
                )
            )

            self.setItem(
                row,
                2,
                QTableWidgetItem(client.document)
            )

            self.setItem(
                row,
                3,
                QTableWidgetItem(client.phone)
            )

    def get_selected_client_id(self):

        selected = self.currentRow()

        if selected < 0:
             return None

        item = self.item(selected, 0)

        if item is None:
            return None

        return item.data(Qt.ItemDataRole.UserRole)