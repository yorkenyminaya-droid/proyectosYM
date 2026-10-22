from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
)


class Sidebar(QWidget):

    menu_clicked = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedWidth(220)

        layout = QVBoxLayout(self)

        buttons = [
            "Inicio",
            "Clientes",
            "Préstamos",
            "Pagos",
            "Caja",
            "Reportes",
            "Configuración",
            "Salir"
        ]

        for text in buttons:
            button = QPushButton(text)

            button.setMinimumHeight(45)

            button.clicked.connect(
                lambda checked=False, name=text:
                self.menu_clicked.emit(name)
            )

            layout.addWidget(button)

        layout.addStretch()