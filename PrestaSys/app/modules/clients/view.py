from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QComboBox,
)

from app.modules.clients.widgets.client_form import ClientForm
from app.modules.clients.widgets.client_list import ClientList
from app.modules.clients.controller import ClientController


class ClientsView(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # ==========================
        # Barra superior
        # ==========================

        top_layout = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Buscar por código, nombre, documento o teléfono..."
        )

        top_layout.addWidget(self.search)

        top_layout.addWidget(QLabel("Estado:"))

        self.status = QComboBox()
        self.status.addItems([
            "Activos",
            "Inactivos"
        ])

        top_layout.addWidget(self.status)

        main_layout.addLayout(top_layout)

        # ==========================
        # Contenido principal
        # ==========================

        content = QHBoxLayout()

        self.list = ClientList()
        self.form = ClientForm()

        content.addWidget(self.list, 1)
        content.addWidget(self.form, 2)

        main_layout.addLayout(content)

        self.controller = ClientController(self)