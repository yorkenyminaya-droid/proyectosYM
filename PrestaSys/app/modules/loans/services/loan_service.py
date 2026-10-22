from app.modules.loans.models.loan import Loan

from app.modules.loans.repositories.loan_repository import LoanRepository
from app.modules.loans.repositories.installment_repository import InstallmentRepository

from app.modules.loans.services.loan_calculator import LoanCalculator
from app.modules.loans.services.installment_generator import InstallmentGenerator


class LoanService:

    def __init__(self):

        self.loan_repository = LoanRepository()

        self.installment_repository = InstallmentRepository()

    # ======================================
    # Crear préstamo
    # ======================================

    def create_loan(self, data):

        loan = Loan()

        loan.code = self.generate_code()

        loan.loan_type = data["loan_type"]

        loan.client_id = data["client_id"]

        loan.payment_frequency = data["payment_frequency"]

        loan.principal_amount = data["principal_amount"]

        loan.interest_rate = data["interest_rate"]

        loan.installments = data["installments"]

        loan.start_date = data["start_date"]

        loan.due_date = data["due_date"]

        loan.notes = data["notes"]

        # ===========================
        # Calcular valores
        # ===========================

        if loan.loan_type == "CUOTAS":

            result = LoanCalculator.calculate_installment(
                loan.principal_amount,
                loan.interest_rate,
                loan.installments
            )

            loan.total_amount = result["total"]

            loan.installment_amount = result["installment"]

        else:

            loan.total_amount = loan.principal_amount

            loan.installment_amount = 0

        loan.current_balance = loan.principal_amount

        loan.status = "ACTIVO"

        # ===========================
        # Guardar préstamo
        # ===========================

        loan = self.loan_repository.add(loan)

        # ===========================
        # Generar cuotas
        # ===========================

        if loan.loan_type == "CUOTAS":

            installments = InstallmentGenerator.generate(
                loan
            )

            self.installment_repository.add_all(
                installments
            )

        return loan

    # ======================================
    # Obtener préstamos
    # ======================================

    def get_all_loans(self):

        return self.loan_repository.get_all()

    # ======================================
    # Buscar por ID
    # ======================================

    def get_by_id(self, loan_id):

        return self.loan_repository.get_by_id(
            loan_id
        )

    # ======================================
    # Actualizar
    # ======================================

    def update_loan(self, loan):

        return self.loan_repository.update(
            loan
        )

    # ======================================
    # Eliminar
    # ======================================

    def delete_loan(self, loan_id):

        return self.loan_repository.delete(
            loan_id
        )

    # ======================================
    # Código automático
    # ======================================

    def generate_code(self):

        last = self.loan_repository.get_last()

        if last is None:

            return "PRE-000001"

        number = int(
            last.code.replace(
            "PRE-",
            ""
        )
    )

        number += 1

        return f"PRE-{number:06d}"