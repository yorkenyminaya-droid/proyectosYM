from datetime import timedelta
from dateutil.relativedelta import relativedelta


class LoanSchedule:

    @staticmethod
    def generate_dates(start_date, installments, frequency):

        dates = []

        current = start_date

        for _ in range(installments):

            dates.append(current)

            if frequency == "DIARIO":

                current += timedelta(days=1)

            elif frequency == "SEMANAL":

                current += timedelta(days=7)

            elif frequency == "QUINCENAL":

                current += timedelta(days=15)

            elif frequency == "MENSUAL":

                current += relativedelta(months=1)

            else:

                raise ValueError(
                    "Frecuencia no válida."
                )

        return dates