from datetime import date

from app.modules.loans.models.payment import Payment

from app.modules.loans.repositories.payment_repository import PaymentRepository
from app.modules.loans.repositories.loan_repository import LoanRepository
from app.modules.loans.repositories.installment_repository import InstallmentRepository


class PaymentService:

    def __init__(self):

        self.payment_repository = PaymentRepository()

        self.loan_repository = LoanRepository()

        self.installment_repository = InstallmentRepository()

    # =====================================
    # Registrar pago
    # =====================================

    def register_payment(self, data):

        payment = Payment()

        payment.loan_id = data["loan_id"]

        payment.installment_id = data.get("installment_id")

        payment.payment_date = data.get(
            "payment_date",
            date.today()
        )

        payment.amount = data["amount"]

        payment.payment_method = data["payment_method"]

        payment.reference = data.get(
            "reference",
            ""
        )

        payment.notes = data.get(
            "notes",
            ""
        )

        return self.payment_repository.add(payment)

    # =====================================

    def get_all(self):

        return self.payment_repository.get_all()

    # =====================================

    def get_by_loan(self, loan_id):

        return self.payment_repository.get_by_loan(
            loan_id
        )

    # =====================================

    def get_active_loans(self):

        return self.loan_repository.get_active()

    # =====================================

    def get_pending_installments(self, loan_id):

        installments = self.installment_repository.get_by_loan(
            loan_id
        )

        return [
            installment
            for installment in installments
            if installment.status == "PENDIENTE"
        ]

    # =====================================

    def get_installment(self, installment_id):

        return self.installment_repository.get_by_id(
            installment_id
        )