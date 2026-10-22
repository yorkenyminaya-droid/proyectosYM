from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from PySide6.QtCore import Qt


class LoanList(QTableWidget):

    def __init__(self):

        super().__init__()

        self.setColumnCount(7)

        self.setHorizontalHeaderLabels([

            "Código",

            "Cliente",

            "Tipo",

            "Capital",

            "Saldo",

            "Frecuencia",

            "Estado",

        ])

        self.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.verticalHeader().setVisible(False)

        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    def load_loans(self, loans):

        self.clearContents()

        self.setRowCount(0)

        for loan in loans:

            row = self.rowCount()

            self.insertRow(row)

            item = QTableWidgetItem(loan.code)

            item.setData(
                Qt.ItemDataRole.UserRole,
                loan.id
            )

            self.setItem(row, 0, item)

            self.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{loan.client.first_name} {loan.client.last_name}"
                )
            )

            self.setItem(
                row,
                2,
                QTableWidgetItem(
                    loan.loan_type
                )
            )

            self.setItem(
                row,
                3,
                QTableWidgetItem(
                    f"{loan.principal_amount:,.2f}"
                )
            )

            self.setItem(
                row,
                4,
                QTableWidgetItem(
                    f"{loan.current_balance:,.2f}"
                )
            )

            self.setItem(
                row,
                5,
                QTableWidgetItem(
                    loan.payment_frequency
                )
            )

            self.setItem(
                row,
                6,
                QTableWidgetItem(
                    loan.status
                )
            )

    def get_selected_loan_id(self):

        row = self.currentRow()

        if row < 0:
            return None

        item = self.item(row, 0)

        if item is None:
            return None

        return item.data(
            Qt.ItemDataRole.UserRole
        )