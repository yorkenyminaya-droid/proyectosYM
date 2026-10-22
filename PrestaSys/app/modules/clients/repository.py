from sqlalchemy import select, or_

from app.core.database.session import SessionLocal
from app.modules.clients.model import Client


class ClientRepository:

    def add(self, client: Client):

        with SessionLocal() as session:

            session.add(client)
            session.commit()
            session.refresh(client)

            return client

    def get_all(self, active=True):

            with SessionLocal() as session:

                stmt = (
            select(Client)
            .where(Client.active == (1 if active else 0))
            .order_by(Client.id)
        )

            return session.scalars(stmt).all()

    def get_by_document(self, document):

        with SessionLocal() as session:

            stmt = select(Client).where(
                Client.document == document
            )

            return session.scalar(stmt)

    def get_last(self):

        with SessionLocal() as session:

            stmt = (
                select(Client)
                .order_by(Client.id.desc())
            )

            return session.scalar(stmt)

    def get_by_id(self, client_id):

        with SessionLocal() as session:

            stmt = select(Client).where(
                Client.id == client_id
            )

            return session.scalar(stmt)

    def update(self, client_id, data):

        with SessionLocal() as session:

            client = session.get(Client, client_id)

            if client is None:
                return None

            client.first_name = data["first_name"]
            client.last_name = data["last_name"]
            client.document = data["document"]
            client.phone = data["phone"]
            client.address = data["address"]
            client.notes = data["notes"]

            session.commit()
            session.refresh(client)

            return client

    def search(self, text):

        with SessionLocal() as session:

            stmt = (
                select(Client)
                .where(
                    Client.active == 1,
                    or_(
                        Client.code.like(f"%{text}%"),
                        Client.first_name.like(f"%{text}%"),
                        Client.last_name.like(f"%{text}%"),
                        Client.document.like(f"%{text}%"),
                        Client.phone.like(f"%{text}%")
                    )
                )
                .order_by(Client.id)
            )

            return session.scalars(stmt).all()

    def deactivate(self, client_id):

        with SessionLocal() as session:

            client = session.get(Client, client_id)

            if client is None:
                return False

            client.active = 0

            session.commit()

            return True
    def reactivate(self, client_id):

        with SessionLocal() as session:

            client = session.get(Client, client_id)

            if client is None:
                return False

            client.active = 1

            session.commit()

            return True