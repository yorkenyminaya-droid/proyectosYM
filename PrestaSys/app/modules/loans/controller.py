from PySide6.QtWidgets import QMessageBox

from app.modules.loans.service import LoanService


class LoanController:

    def __init__(self, view):

        self.view = view

        self.service = LoanService()

        self.view.form.btn_save.clicked.connect(
            self.save_loan
        )

        self.load_loans()

    def save_loan(self):

        valid, message = self.view.form.validate()

        if not valid:

            QMessageBox.warning(
            self.view,
            "Validación",
            message
        )

            return

        try:

            data = self.view.form.get_data()

            if self.view.form.loan_id is None:

                self.service.create_loan(data)

                QMessageBox.information(
                self.view,
                "Éxito",
                "Préstamo registrado correctamente."
            )

            else:

                self.service.update_loan(
                self.view.form.loan_id,
                data
            )

                QMessageBox.information(
                self.view,
                "Éxito",
                "Préstamo actualizado correctamente."
            )

            self.view.form.clear()

            self.load_loans()

        except Exception as e:

            QMessageBox.critical(
            self.view,
            "Error",
            str(e)
        )

    def load_loans(self):

        loans = self.service.get_all_loans()

        self.view.list.load_loans(loans)