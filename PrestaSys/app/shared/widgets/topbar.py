from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
)


class TopBar(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedHeight(60)

        layout = QHBoxLayout(self)

        title = QLabel("PrestaSys")

        title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        user = QLabel("Administrador")

        layout.addWidget(title)

        layout.addStretch()

        layout.addWidget(user)

        layout.setAlignment(user, Qt.AlignmentFlag.AlignRight)