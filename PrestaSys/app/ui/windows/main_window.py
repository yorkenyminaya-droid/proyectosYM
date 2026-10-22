from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)

from PySide6.QtWidgets import QStackedWidget

from app.shared.widgets.sidebar import Sidebar
from app.shared.widgets.topbar import TopBar

from app.modules.dashboard.view import DashboardView
from app.modules.clients.view import ClientsView
from app.modules.loans.view import LoansView
from app.modules.payments.view import PaymentsView


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PrestaSys")
        self.resize(1400, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # ==========================
        # Sidebar
        # ==========================

        self.sidebar = Sidebar()

        # ==========================
        # Contenido
        # ==========================

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.topbar = TopBar()

        self.stack = QStackedWidget()

        # ==========================
        # Módulos
        # ==========================

        self.dashboard = DashboardView()
        self.clients = ClientsView()
        self.loans = LoansView()
        self.payments = PaymentsView()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.clients)
        self.stack.addWidget(self.loans)
        self.stack.addWidget(self.payments)

        # ==========================
        # Etiqueta inferior
        # ==========================

        self.content_label = QLabel("Módulo: Inicio")

        self.content_label.setStyleSheet("""
            font-size: 24px;
        """)

        content_layout.addWidget(self.topbar)
        content_layout.addWidget(self.stack)
        content_layout.addWidget(self.content_label)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_widget)

        self.sidebar.menu_clicked.connect(
            self.change_module
        )

    def change_module(self, module_name):

        if module_name == "Salir":
            self.close()
            return

        if module_name == "Inicio":
            self.stack.setCurrentWidget(self.dashboard)

        elif module_name == "Clientes":
            self.stack.setCurrentWidget(self.clients)

        elif module_name == "Préstamos":
            self.stack.setCurrentWidget(self.loans)

        elif module_name == "Pagos":
            self.stack.setCurrentWidget(self.payments)

        self.content_label.setText(
            f"Módulo: {module_name}"
        )