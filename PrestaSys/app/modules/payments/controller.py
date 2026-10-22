from app.modules.loans.services.payment_service import PaymentService


class PaymentController:

    def __init__(self, view):

        self.view = view

        self.service = PaymentService()

        self.connect_signals()

        self.load_loans()

        self.load_payments()

    # =====================================

    def connect_signals(self):

        self.view.form.btn_save.clicked.connect(
            self.save_payment
        )

        self.view.form.loan.currentIndexChanged.connect(
            self.load_installments
        )

        self.view.form.installment.currentIndexChanged.connect(
            self.update_amount
        )

    # =====================================

    def load_loans(self):

        combo = self.view.form.loan

        combo.clear()

        combo.addItem(
            "Seleccione un préstamo...",
            None
        )

        loans = self.service.get_active_loans()

        for loan in loans:

            combo.addItem(
                f"{loan.code} - {loan.client.first_name} {loan.client.last_name}",
                loan.id
            )

    # =====================================

    def load_installments(self):

        combo = self.view.form.installment

        combo.clear()

        loan_id = self.view.form.loan.currentData()

        if loan_id is None:
            return

        installments = self.service.get_pending_installments(
            loan_id
        )

        combo.addItem(
            "Seleccione una cuota...",
            None
        )

        for installment in installments:

            combo.addItem(
                f"Cuota {installment.installment_number} - ${installment.balance:,.2f}",
                installment.id
            )

    # =====================================

    def update_amount(self):

        installment_id = (
            self.view.form.installment.currentData()
        )

        if installment_id is None:

            self.view.form.amount.setValue(0)

            return

        installment = self.service.get_installment(
            installment_id
        )

        if installment:

            self.view.form.amount.setValue(
                float(installment.balance)
            )

    # =====================================

    def load_payments(self):

        payments = self.service.get_all()

        self.view.list.load_payments(
            payments
        )

    # =====================================

    def save_payment(self):

        print("Registrar pago...")