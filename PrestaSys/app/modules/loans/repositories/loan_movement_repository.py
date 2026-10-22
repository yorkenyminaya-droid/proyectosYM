from sqlalchemy import select

from app.core.database.session import SessionLocal

from app.modules.loans.models.loan_movement import LoanMovement


class LoanMovementRepository:

    # =====================================
    # Registrar movimiento
    # =====================================

    def add(self, movement):

        with SessionLocal() as session:

            session.add(movement)

            session.commit()

            session.refresh(movement)

            return movement

    # =====================================
    # Movimientos de un préstamo
    # =====================================

    def get_by_loan(self, loan_id):

        with SessionLocal() as session:

            stmt = (
                select(LoanMovement)
                .where(
                    LoanMovement.loan_id == loan_id
                )
                .order_by(
                    LoanMovement.movement_date.desc()
                )
            )

            return session.scalars(stmt).all()

    # =====================================
    # Obtener todos
    # =====================================

    def get_all(self):

        with SessionLocal() as session:

            stmt = (
                select(LoanMovement)
                .order_by(
                    LoanMovement.movement_date.desc()
                )
            )

            return session.scalars(stmt).all()