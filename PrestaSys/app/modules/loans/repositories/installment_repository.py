from sqlalchemy import select

from app.core.database.session import SessionLocal
from app.modules.loans.models.installment import Installment


class InstallmentRepository:

    # =====================================
    # Crear una cuota
    # =====================================

    def add(self, installment):

        with SessionLocal() as session:

            session.add(installment)

            session.commit()

            session.refresh(installment)

            return installment

    # =====================================
    # Crear varias cuotas
    # =====================================

    def add_all(self, installments):

        with SessionLocal() as session:

            session.add_all(installments)

            session.commit()

    # =====================================
    # Buscar cuotas de un préstamo
    # =====================================

    def get_by_loan(self, loan_id):

        with SessionLocal() as session:

            stmt = (
                select(Installment)
                .where(
                    Installment.loan_id == loan_id
                )
                .order_by(
                    Installment.installment_number
                )
            )

            return session.scalars(stmt).all()

    # =====================================
    # Buscar cuota por ID
    # =====================================

    def get_by_id(self, installment_id):

        with SessionLocal() as session:

            return session.get(
                Installment,
                installment_id
            )

    # =====================================
    # Obtener todas las pendientes
    # =====================================

    def get_pending(self):

        with SessionLocal() as session:

            stmt = (
                select(Installment)
                .where(
                    Installment.status == "PENDIENTE"
                )
                .order_by(
                    Installment.loan_id,
                    Installment.installment_number
                )
            )

            return session.scalars(stmt).all()

    # =====================================
    # Primera pendiente
    # =====================================

    def get_next_pending(self, loan_id):

        with SessionLocal() as session:

            stmt = (
                select(Installment)
                .where(
                    Installment.loan_id == loan_id,
                    Installment.status == "PENDIENTE"
                )
                .order_by(
                    Installment.installment_number
                )
            )

            return session.scalar(stmt)

    # =====================================
    # Actualizar
    # =====================================

    def update(self, installment):

        with SessionLocal() as session:

            session.merge(installment)

            session.commit()

            return installment

    # =====================================
    # Contar pendientes
    # =====================================

    def count_pending(self, loan_id):

        return len(self.get_by_loan(loan_id))