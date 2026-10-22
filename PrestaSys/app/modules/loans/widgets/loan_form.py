from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QDateEdit,
)

from PySide6.QtCore import QDate

from app.modules.clients.service import ClientService
from app.modules.loans.calculator import LoanCalculator

from app.shared.constants.loans import (
    LOAN_TYPES,
    PAYMENT_FREQUENCIES,
)


class LoanForm(QWidget):

    def __init__(self):
        super().__init__()

        self.loan_id = None
        self.client_service = ClientService()

        self.build_ui()

    # ==================================================
    # Construcción de la interfaz
    # ==================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Tipo

        self.loan_type = QComboBox()
        self.loan_type.addItems(LOAN_TYPES)

        # Cliente

        self.client = QComboBox()

        # Frecuencia

        self.frequency = QComboBox()
        self.frequency.addItems(PAYMENT_FREQUENCIES)

        # Fecha

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())

        # Capital

        self.principal = QDoubleSpinBox()
        self.principal.setMaximum(100000000)
        self.principal.setDecimals(2)

        # Interés

        self.interest = QDoubleSpinBox()
        self.interest.setMaximum(100)
        self.interest.setDecimals(2)
        self.interest.setValue(20)

        # Cuotas

        self.installments = QSpinBox()
        self.installments.setMinimum(1)
        self.installments.setMaximum(120)
        self.installments.setValue(12)

        # Resultados

        self.total_label = QLabel("Total a pagar")

        self.total = QLabel("0.00")

        self.installment_label = QLabel(
            "Valor por cuota"
        )

        self.installment = QLabel("0.00")

        # Observaciones

        self.notes = QTextEdit()

        # =====================================
        # Agregar controles
        # =====================================

        form.addRow("Tipo", self.loan_type)
        form.addRow("Cliente", self.client)
        form.addRow("Frecuencia", self.frequency)
        form.addRow("Fecha", self.start_date)
        form.addRow("Capital", self.principal)
        form.addRow("Interés (%)", self.interest)
        form.addRow("Cuotas", self.installments)
        form.addRow(self.total_label, self.total)
        form.addRow(self.installment_label, self.installment)
        form.addRow("Observaciones", self.notes)

        layout.addLayout(form)

        # Botón

        self.btn_save = QPushButton(
            "Guardar Préstamo"
        )

        layout.addWidget(self.btn_save)

        # =====================================
        # Eventos
        # =====================================

        self.loan_type.currentIndexChanged.connect(
            self.update_form
        )

        self.principal.valueChanged.connect(
            self.calculate_totals
        )

        self.interest.valueChanged.connect(
            self.calculate_totals
        )

        self.installments.valueChanged.connect(
            self.calculate_totals
        )

        self.load_clients()

        self.update_form()

        self.calculate_totals()

    # ==================================================
    # Calcular valores
    # ==================================================

    def calculate_totals(self):

        principal = self.principal.value()

        interest = self.interest.value()

        loan_type = self.loan_type.currentText()

        # =============================
        # Préstamo por cuotas
        # =============================

        if loan_type in ("CUOTAS", "PLAZO"):

            installments = self.installments.value()

            if installments <= 0:
                return

            result = LoanCalculator.calculate_installment(
                principal,
                interest,
                installments
            )

            self.total.setText(
                f"{result['total']:,.2f}"
            )

            self.installment.setText(
                f"{result['installment']:,.2f}"
            )

        # =============================
        # Préstamo a rédito
        # =============================

        else:

            interest_payment = (
                LoanCalculator.calculate_interest_payment(
                    principal,
                    interest
                )
            )

            self.total.setText(
                f"{interest_payment:,.2f}"
            )

            self.installment.setText("0.00")

    # ==================================================
    # Mostrar/Ocultar controles
    # ==================================================

    def update_form(self):

        loan_type = self.loan_type.currentText()

        is_installment = (
            loan_type in ("CUOTAS", "PLAZO")
        )

        self.installments.setVisible(
            is_installment
        )

        self.installment_label.setVisible(
            is_installment
        )

        self.installment.setVisible(
            is_installment
        )

        if is_installment:

            self.total_label.setText(
                "Total a pagar"
            )

        else:

            self.total_label.setText(
                "Rédito por período"
            )

        self.calculate_totals()

    # ==================================================
    # Clientes
    # ==================================================

    def load_clients(self):

        self.client.clear()

        self.client.addItem(
            "Seleccione un cliente...",
            None
        )

        clients = self.client_service.get_all_clients()

        for client in clients:

            self.client.addItem(
                f"{client.code} - {client.first_name} {client.last_name}",
                client.id
            )

    # ==================================================
    # Obtener datos
    # ==================================================

    def get_data(self):

        return {

            "loan_type": self.loan_type.currentText(),

            "client_id": self.client.currentData(),

            "payment_frequency": self.frequency.currentText(),

            "principal_amount": self.principal.value(),

            "interest_rate": self.interest.value(),

            "total_amount": float(
                self.total.text().replace(",", "")
            ),

            "installment_amount": float(
                self.installment.text().replace(",", "")
            ),

            "installments": self.installments.value(),

            "start_date": self.start_date.date().toPython(),

            "due_date": self.start_date.date().toPython(),

            "notes": self.notes.toPlainText(),

        }

    # ==================================================
    # Limpiar formulario
    # ==================================================

    def clear(self):

        self.loan_id = None

        self.loan_type.setCurrentIndex(0)

        self.client.setCurrentIndex(0)

        self.frequency.setCurrentIndex(0)

        self.principal.setValue(0)

        self.interest.setValue(20)

        self.installments.setValue(12)

        self.start_date.setDate(
            QDate.currentDate()
        )

        self.notes.clear()

        self.calculate_totals()

    # ==================================================
    # Validación
    # ==================================================

    def validate(self):

        if self.client.currentData() is None:
            return False, "Debe seleccionar un cliente."

        if self.principal.value() <= 0:
            return False, "Debe ingresar el capital."

        return True, ""

    # ==================================================
    # Cargar préstamo
    # ==================================================

    def load_loan(self, loan):

        self.loan_id = loan.id

        self.loan_type.setCurrentText(
            loan.loan_type
        )

        self.frequency.setCurrentText(
            loan.payment_frequency
        )

        index = self.client.findData(
            loan.client_id
        )

        if index >= 0:
            self.client.setCurrentIndex(index)

        self.principal.setValue(
            loan.principal_amount
        )

        self.interest.setValue(
            loan.interest_rate
        )

        self.installments.setValue(
            loan.installments or 1
        )

        self.start_date.setDate(
            QDate(
                loan.start_date.year,
                loan.start_date.month,
                loan.start_date.day
            )
        )

        self.notes.setPlainText(
            loan.notes or ""
        )

        self.update_form()

        self.calculate_totals()