from app.modules.clients.model import Client
from app.modules.clients.repository import ClientRepository


class ClientService:

    def __init__(self):

        self.repository = ClientRepository()

    def generate_code(self):

        last = self.repository.get_last()

        if last is None:
            return "CLI-000001"

        number = int(last.code.split("-")[1]) + 1

        return f"CLI-{number:06d}"

    def create_client(self, data):

        if self.repository.get_by_document(data["document"]):
            raise ValueError("La cédula ya está registrada.")

        client = Client(

            code=self.generate_code(),

            first_name=data["first_name"],

            last_name=data["last_name"],

            document=data["document"],

            phone=data.get("phone", ""),

            phone2=data.get("phone2", ""),

            address=data.get("address", ""),

            reference=data.get("reference", ""),

            reference_phone=data.get("reference_phone", ""),

            email=data.get("email", ""),

            notes=data.get("notes", ""),

        )

        return self.repository.add(client)

    def get_all_clients(self, active=True):

        return self.repository.get_all(active)
    
    def get_client_by_id(self, client_id):

        return self.repository.get_by_id(client_id)
    
    def update_client(self, client_id, data):

        return self.repository.update(client_id, data)
    
    def search_clients(self, text):

        return self.repository.search(text)
    
    def deactivate_client(self, client_id):

        return self.repository.deactivate(client_id)
    
    def reactivate_client(self, client_id):

        return self.repository.reactivate(client_id)
    
    