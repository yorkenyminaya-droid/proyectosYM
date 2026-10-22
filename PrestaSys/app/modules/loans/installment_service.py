from app.modules.loans.models.installment import Installment
from app.modules.loans.schedule import LoanSchedule


class InstallmentService:

    @staticmethod
    def generate_installments(loan):

        dates = LoanSchedule.generate_dates(
            loan.start_date,
            loan.installments,
            loan.payment_frequency
        )

        installments = []

        capital = round(
            loan.principal_amount / loan.installments,
            2
        )

        interest = round(
            (loan.total_amount - loan.principal_amount)
            / loan.installments,
            2
        )

        for number, due_date in enumerate(dates, start=1):

            installments.append(

                Installment(

                    loan_id=loan.id,

                    installment_number=number,

                    due_date=due_date,

                    capital_amount=capital,

                    interest_amount=interest,

                    total_amount=loan.installment_amount,

                    paid_amount=0,

                    balance=loan.installment_amount,

                    status="PENDIENTE"

                )

            )

        return installments