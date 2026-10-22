from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from PySide6.QtCore import Qt


class PaymentList(QTableWidget):

    def __init__(self):

        super().__init__()

        self.setColumnCount(7)

        self.setHorizontalHeaderLabels([

            "Fecha",

            "Préstamo",

            "Cliente",

            "Valor",

            "Método",

            "Cuota",

            "Observación",

        ])

        self.verticalHeader().setVisible(False)

        self.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    # =====================================

    def load_payments(self, payments):

        self.clearContents()

        self.setRowCount(0)

        for payment in payments:

            row = self.rowCount()

            self.insertRow(row)

            self.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(payment.payment_date)
                )
            )

            self.setItem(
                row,
                1,
                QTableWidgetItem(
                    payment.loan.code
                )
            )

            self.setItem(
                row,
                2,
                QTableWidgetItem(
                    f"{payment.loan.client.first_name} "
                    f"{payment.loan.client.last_name}"
                )
            )

            self.setItem(
                row,
                3,
                QTableWidgetItem(
                    f"{payment.total_paid:,.2f}"
                )
            )

            self.setItem(
                row,
                4,
                QTableWidgetItem(
                    payment.payment_method
                )
            )

            installment = ""

            if payment.installment:

                installment = str(
                    payment.installment.installment_number
                )

            self.setItem(
                row,
                5,
                QTableWidgetItem(
                    installment
                )
            )

            self.setItem(
                row,
                6,
                QTableWidgetItem(
                    payment.notes or ""
                )
            )