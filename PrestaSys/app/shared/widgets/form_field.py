from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QVBoxLayout
)


class FormField(QWidget):

    def __init__(self, label):

        super().__init__()

        layout = QVBoxLayout(self)

        self.label = QLabel(label)

        self.input = QLineEdit()

        layout.addWidget(self.label)

        layout.addWidget(self.input)

    def text(self):

        return self.input.text()

    def clear(self):

        self.input.clear()

    def setText(self, value):

        self.input.setText(value)