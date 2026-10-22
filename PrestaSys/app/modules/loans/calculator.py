class LoanCalculator:

    @staticmethod
    def calculate_installment(principal, interest, installments):

        total = principal + (principal * interest / 100)

        installment = total / installments

        return {
            "total": round(total, 2),
            "installment": round(installment, 2)
        }

    @staticmethod
    def calculate_interest_payment(principal, interest):

        return round(
            principal * interest / 100,
            2
        )