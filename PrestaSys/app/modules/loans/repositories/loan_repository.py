from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database.session import SessionLocal
from app.modules.loans.models.loan import Loan


class LoanRepository:

    # =====================================
    # Crear préstamo
    # =====================================

    def add(self, loan):

        with SessionLocal() as session:

            session.add(loan)

            session.commit()

            session.refresh(loan)

            return loan

    # =====================================
    # Obtener todos
    # =====================================

    def get_all(self):

        with SessionLocal() as session:

            stmt = (
                select(Loan)
                .options(joinedload(Loan.client))
                .order_by(Loan.id.desc())
            )

            return session.scalars(stmt).all()

    # =====================================
    # Buscar por ID
    # =====================================

    def get_by_id(self, loan_id):

        with SessionLocal() as session:

            return session.get(Loan, loan_id)

    # =====================================
    # Buscar por código
    # =====================================

    def get_by_code(self, code):

        with SessionLocal() as session:

            stmt = (
                select(Loan)
                .options(joinedload(Loan.client))
                .where(Loan.code == code)
            )

            return session.scalar(stmt)

    # =====================================
    # Buscar por cliente
    # =====================================

    def get_by_client(self, client_id):

        with SessionLocal() as session:

            stmt = (
                select(Loan)
                .options(joinedload(Loan.client))
                .where(Loan.client_id == client_id)
                .order_by(Loan.id.desc())
            )

            return session.scalars(stmt).all()

    # =====================================
    # Buscar por estado
    # =====================================

    def get_by_status(self, status):

        with SessionLocal() as session:

            stmt = (
                select(Loan)
                .options(joinedload(Loan.client))
                .where(Loan.status == status)
                .order_by(Loan.id.desc())
            )

            return session.scalars(stmt).all()

    # =====================================
    # Préstamos activos
    # =====================================

    def get_active(self):

        return self.get_by_status("ACTIVO")

    # =====================================
    # Último préstamo
    # =====================================

    def get_last(self):

        with SessionLocal() as session:

            stmt = (
                select(Loan)
                .order_by(Loan.id.desc())
                .limit(1)
            )

            return session.scalar(stmt)

    # =====================================
    # Actualizar
    # =====================================

    def update(self, loan):

        with SessionLocal() as session:

            session.merge(loan)

            session.commit()

            return loan

    # =====================================
    # Eliminar
    # =====================================

    def delete(self, loan_id):

        with SessionLocal() as session:

            loan = session.get(Loan, loan_id)

            if loan is None:
                return False

            session.delete(loan)

            session.commit()

            return True

    # =====================================
    # Estadísticas
    # =====================================

    def count_active(self):

        return len(self.get_by_status("ACTIVO"))

    def count_paid(self):

        return len(self.get_by_status("PAGADO"))

    def count_overdue(self):

        return len(self.get_by_status("EN MORA"))