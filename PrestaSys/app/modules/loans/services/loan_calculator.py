class LoanCalculator:

    @staticmethod
    def calculate_installment(principal, interest, installments):

        total = principal + (
            principal * interest / 100
        )

        installment = total / installments

        return {

            "total": round(total, 2),

            "installment": round(
                installment,
                2
            )

        }

    @staticmethod
    def calculate_interest_payment(principal, interest):

        return round(

            principal * interest / 100,

            2

        )

    @staticmethod
    def apply_capital_payment(balance, capital_payment):

        new_balance = balance - capital_payment

        if new_balance < 0:

            new_balance = 0

        return round(new_balance, 2)