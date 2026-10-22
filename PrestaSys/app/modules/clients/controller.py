from PySide6.QtWidgets import QMessageBox

from app.modules.clients.service import ClientService


class ClientController:

    def __init__(self, view):
        self.view = view
        self.service = ClientService()

        self.view.form.btn_save.clicked.connect(self.save_client)

        self.view.list.itemSelectionChanged.connect(
            self.load_selected_client
        )

        self.view.form.btn_disable.clicked.connect(
        self.change_active_status
)

        self.view.search.textChanged.connect(
        self.search_clients
)
        
        self.view.status.currentIndexChanged.connect(
        self.change_status
)

        self.load_clients()

    def save_client(self):

        valid, message = self.view.form.validate()

        if not valid:
            QMessageBox.warning(
                self.view,
                "Validación",
                message
            )
            return

        try:

            # ==========================
            # NUEVO CLIENTE
            # ==========================
            if self.view.form.client_id is None:

                self.service.create_client(
                    self.view.form.get_data()
            )

                QMessageBox.information(
                    self.view,
                    "Éxito",
                    "Cliente registrado correctamente."
            )

            # ==========================
            # EDITAR CLIENTE
            # ==========================
            else:

                data = self.view.form.get_data()

                self.service.update_client(
                    self.view.form.client_id,
                    data
            )

                QMessageBox.information(
                    self.view,
                    "Éxito",
                    "Cliente actualizado correctamente."
            )

            self.load_clients()

            self.view.list.clearSelection()

            self.view.form.clear()

        except Exception as e:

            QMessageBox.critical(
                self.view,
                "Error",
                str(e)
            )

    def load_clients(self):

        active = self.view.status.currentText() == "Activos"

        clients = self.service.get_all_clients(active)

        self.view.list.load_clients(clients)

    def load_selected_client(self):

        client_id = self.view.list.get_selected_client_id()

        if client_id is None:
            return

        client = self.service.get_client_by_id(client_id)

        if client is None:
            return

        self.view.form.load_client(client)

    def search_clients(self):

        text = self.view.search.text().strip()

        if text == "":
         self.load_clients()
         return

        clients = self.service.search_clients(text)

        self.view.list.load_clients(clients)

    def deactivate_client(self):

        if self.view.form.client_id is None:

            QMessageBox.warning(
            self.view,
            "Atención",
            "Seleccione un cliente."
        )
            return

        reply = QMessageBox.question(
            self.view,
            "Confirmar",
            "¿Desea inactivar este cliente?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
    )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.service.deactivate_client(
        self.view.form.client_id
    )

        QMessageBox.information(
        self.view,
        "Éxito",
        "Cliente inactivado correctamente."
    )

        self.load_clients()
        self.view.list.clearSelection()
        self.view.form.clear()


    def change_status(self):

        self.view.search.clear()

        self.load_clients()

        self.view.form.clear()

        self.view.list.clearSelection()

        if self.view.status.currentText() == "Activos":
            self.view.form.btn_disable.setText("Inactivar")
        else:
            self.view.form.btn_disable.setText("Reactivar")
    
    def change_active_status(self):

        if self.view.status.currentText() == "Activos":
            self.deactivate_client()
        else:
            self.reactivate_client()
    
    def reactivate_client(self):

        if self.view.form.client_id is None:

            QMessageBox.warning(
            self.view,
            "Atención",
            "Seleccione un cliente."
        )
            return

        reply = QMessageBox.question(
        self.view,
        "Confirmar",
        "¿Desea reactivar este cliente?",
        QMessageBox.StandardButton.Yes |
        QMessageBox.StandardButton.No
    )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.service.reactivate_client(
        self.view.form.client_id
    )

        QMessageBox.information(
        self.view,
        "Éxito",
        "Cliente reactivado correctamente."
    )

        self.load_clients()
        self.view.list.clearSelection()
        self.view.form.clear()