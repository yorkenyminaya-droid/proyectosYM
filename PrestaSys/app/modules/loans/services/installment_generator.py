from datetime import timedelta

from app.modules.loans.models.installment import Installment


class InstallmentGenerator:

    @staticmethod
    def generate(loan):

        installments = []

        current_date = loan.start_date

        frequency_days = {
            "DIARIO": 1,
            "SEMANAL": 7,
            "QUINCENAL": 15,
            "MENSUAL": 30,
        }

        days = frequency_days.get(
            loan.payment_frequency,
            30
        )

        capital = round(
            loan.principal_amount / loan.installments,
            2
        )

        interest = round(
            (
                loan.total_amount -
                loan.principal_amount
            ) / loan.installments,
            2
        )

        total = round(
            capital + interest,
            2
        )

        for number in range(1, loan.installments + 1):

            installment = Installment(

                loan_id=loan.id,

                installment_number=number,

                due_date=current_date,

                capital_amount=capital,

                interest_amount=interest,

                total_amount=total,

                paid_amount=0,

                balance=total,

                status="PENDIENTE",
            )

            installments.append(
                installment
            )

            current_date += timedelta(days=days)

        return installments