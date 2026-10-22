from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
)

from app.modules.loans.widgets.loan_form import LoanForm
from app.modules.loans.widgets.loan_list import LoanList
from app.modules.loans.controller import LoanController


class LoansView(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # Buscador
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Buscar préstamo..."
        )

        main_layout.addWidget(self.search)

        # Contenido
        content = QHBoxLayout()

        self.list = LoanList()
        self.form = LoanForm()

        content.addWidget(self.list, 1)
        content.addWidget(self.form, 2)

        main_layout.addLayout(content)

        self.controller = LoanController(self)