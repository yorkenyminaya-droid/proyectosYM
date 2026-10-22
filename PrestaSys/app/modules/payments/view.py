from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter
)

from PySide6.QtCore import Qt

from app.modules.payments.widgets.payment_form import PaymentForm
from app.modules.payments.widgets.payment_list import PaymentList
from app.modules.payments.controller import PaymentController


class PaymentsView(QWidget):

    def __init__(self):

        super().__init__()

        self.build_ui()

        self.controller = PaymentController(self)

    # ======================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Vertical)

        self.form = PaymentForm()

        self.list = PaymentList()

        splitter.addWidget(self.form)

        splitter.addWidget(self.list)

        splitter.setStretchFactor(0, 1)

        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)