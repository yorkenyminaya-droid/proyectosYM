from sqlalchemy import select

from app.core.database.session import SessionLocal

from app.modules.loans.models.cash_movement import CashMovement


class CashMovementRepository:

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
    # Obtener todos
    # =====================================

    def get_all(self):

        with SessionLocal() as session:

            stmt = (
                select(CashMovement)
                .order_by(
                    CashMovement.movement_date.desc()
                )
            )

            return session.scalars(stmt).all()

    # =====================================
    # Buscar por ID
    # =====================================

    def get_by_id(self, movement_id):

        with SessionLocal() as session:

            return session.get(
                CashMovement,
                movement_id
            )

    # =====================================
    # Eliminar
    # =====================================

    def delete(self, movement_id):

        with SessionLocal() as session:

            movement = session.get(
                CashMovement,
                movement_id
            )

            if movement is None:
                return False

            session.delete(movement)

            session.commit()

            return True