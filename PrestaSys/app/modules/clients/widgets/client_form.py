from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
)


class ClientForm(QWidget):

    def __init__(self):
        super().__init__()

        self.client_id = None

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.document = QLineEdit()
        self.phone = QLineEdit()
        self.address = QLineEdit()
        self.notes = QTextEdit()

        form.addRow("Nombre", self.first_name)
        form.addRow("Apellido", self.last_name)
        form.addRow("Cédula", self.document)
        form.addRow("Teléfono", self.phone)
        form.addRow("Dirección", self.address)
        form.addRow("Observaciones", self.notes)

        layout.addLayout(form)

        from PySide6.QtWidgets import QHBoxLayout

        buttons = QHBoxLayout()

        self.btn_save = QPushButton("Guardar Cliente")
        self.btn_disable = QPushButton("Inactivar")

        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.btn_disable)

        layout.addLayout(buttons)

    def get_data(self):

        return {
            "first_name": self.first_name.text(),
            "last_name": self.last_name.text(),
            "document": self.document.text(),
            "phone": self.phone.text(),
            "address": self.address.text(),
            "notes": self.notes.toPlainText(),
        }

    def clear(self):

        self.client_id = None

        self.first_name.clear()
        self.last_name.clear()
        self.document.clear()
        self.phone.clear()
        self.address.clear()
        self.notes.clear()

    def validate(self):

        if not self.first_name.text().strip():
            return False, "Debe ingresar el nombre."

        if not self.last_name.text().strip():
            return False, "Debe ingresar el apellido."

        if not self.document.text().strip():
            return False, "Debe ingresar la cédula."

        return True, ""

    def load_client(self, client):

        self.client_id = client.id

        self.first_name.setText(client.first_name)
        self.last_name.setText(client.last_name)
        self.document.setText(client.document)
        self.phone.setText(client.phone)
        self.address.setText(client.address)
        self.notes.setPlainText(client.notes)