from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QTextEdit,
    QPushButton,
    QDateEdit,
)

from PySide6.QtCore import QDate


class PaymentForm(QWidget):

    def __init__(self):

        super().__init__()

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # ==========================
        # Préstamo
        # ==========================

        self.loan = QComboBox()

        form.addRow(
            "Préstamo",
            self.loan
        )

        # ==========================
        # Cuota
        # ==========================

        self.installment = QComboBox()

        form.addRow(
            "Cuota",
            self.installment
        )

        # ==========================
        # Fecha
        # ==========================

        self.payment_date = QDateEdit()

        self.payment_date.setCalendarPopup(True)

        self.payment_date.setDate(
            QDate.currentDate()
        )

        form.addRow(
            "Fecha",
            self.payment_date
        )

        # ==========================
        # Valor
        # ==========================

        self.amount = QDoubleSpinBox()

        self.amount.setMaximum(999999999)

        self.amount.setDecimals(2)

        form.addRow(
            "Valor pagado",
            self.amount
        )

        # ==========================
        # Método
        # ==========================

        self.method = QComboBox()

        self.method.addItems([
            "EFECTIVO",
            "TRANSFERENCIA",
            "NEQUI",
            "DAVIPLATA"
        ])

        form.addRow(
            "Método",
            self.method
        )

        # ==========================
        # Referencia
        # ==========================

        self.reference = QTextEdit()

        self.reference.setMaximumHeight(60)

        form.addRow(
            "Referencia",
            self.reference
        )

        # ==========================
        # Observaciones
        # ==========================

        self.notes = QTextEdit()

        form.addRow(
            "Observaciones",
            self.notes
        )

        layout.addLayout(form)

        self.btn_save = QPushButton(
            "Registrar Pago"
        )

        layout.addWidget(
            self.btn_save
        )