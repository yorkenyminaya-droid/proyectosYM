from app.modules.loans.models import Loan
from app.modules.loans.repositories.loan_repository import LoanRepository
from app.modules.loans.installment_service import InstallmentService
from app.modules.loans.repositories.installment_repository import InstallmentRepository
from app.modules.loans.services.installment_generator import InstallmentGenerator


class LoanService:

    def __init__(self):
        self.repository = LoanRepository()
        self.installment_repository = InstallmentRepository()

    # ======================================
    # Generar código automático
    # ======================================

    def generate_code(self):
        last = self.repository.get_last()

        if last is None:
            return "PRE-000001"

        number = int(last.code.split("-")[1]) + 1
        return f"PRE-{number:06d}"

    # ======================================
    # Crear préstamo
    # ======================================

    def create_loan(self, data):
        principal = float(data["principal_amount"])
        interest = float(data["interest_rate"])
        installments = int(data["installments"])
        loan_type = data["loan_type"]

        # ==========================
        # Calcular valores
        # ==========================
        if loan_type == "CUOTAS":
            total_amount = principal + (principal * interest / 100)
            installment_amount = total_amount / installments
        else:
            # En préstamos a rédito
            total_amount = principal
            installment_amount = principal * interest / 100

        # ==========================
        # Instanciar entidad
        # ==========================
        loan = Loan(
            code=self.generate_code(),
            client_id=data["client_id"],
            loan_type=loan_type,
            payment_frequency=data["payment_frequency"],
            principal_amount=principal,
            current_balance=principal,
            interest_rate=interest,
            total_amount=round(total_amount, 2),
            installment_amount=round(installment_amount, 2),
            installments=installments,
            capital_paid=0,
            interest_paid=0,
            start_date=data["start_date"],
            due_date=data["due_date"],
            next_payment_date=data["start_date"],
            last_payment_date=None,
            notes=data.get("notes", "")
        )

        # ==========================
        # Guardar préstamo y cuotas
        # ==========================
        loan = self.repository.add(loan)

        print("Tipo:", loan.loan_type)

        if loan.loan_type in ("CUOTAS", "PLAZO"):

            installments = InstallmentGenerator.generate(
            loan
    )

        print("Cantidad de cuotas:", len(installments))

        self.installment_repository.add_all(
        installments
    )

        print("Cuotas guardadas.")

        return loan

    # ======================================
    # Consultas
    # ======================================

    def get_all_loans(self):
        return self.repository.get_all()

    def get_loan_by_id(self, loan_id):
        return self.repository.get_by_id(loan_id)

    # ======================================
    # Actualizar préstamo
    # ======================================

    def update_loan(self, loan_id, data):
        principal = float(data["principal_amount"])
        interest = float(data["interest_rate"])
        installments = int(data.get("installments") or 0)

        if data["loan_type"] == "CUOTAS":
            data["total_amount"] = round(
                principal + (principal * interest / 100), 2
            )
            data["installment_amount"] = round(
                data["total_amount"] / installments, 2
            )
            data["installments"] = installments
        else:
            # Rédiito: Mantener la consistencia con create_loan
            data["total_amount"] = principal
            data["installment_amount"] = round(principal * interest / 100, 2)
            data["installments"] = None

        return self.repository.update(loan_id, data)