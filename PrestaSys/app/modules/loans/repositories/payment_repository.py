from sqlalchemy import select

from app.core.database.session import SessionLocal

from app.modules.loans.models.payment import Payment


class PaymentRepository:

    # =====================================
    # Registrar pago
    # =====================================

    def add(self, payment):

        with SessionLocal() as session:

            session.add(payment)

            session.commit()

            session.refresh(payment)

            return payment

    # =====================================
    # Buscar por ID
    # =====================================

    def get_by_id(self, payment_id):

        with SessionLocal() as session:

            return session.get(
                Payment,
                payment_id
            )

    # =====================================
    # Buscar pagos de un préstamo
    # =====================================

    def get_by_loan(self, loan_id):

        with SessionLocal() as session:

            stmt = (
                select(Payment)
                .where(
                    Payment.loan_id == loan_id
                )
                .order_by(
                    Payment.payment_date.desc()
                )
            )

            return session.scalars(stmt).all()

    # =====================================
    # Obtener todos
    # =====================================

    def get_all(self):

        with SessionLocal() as session:

            stmt = (
                select(Payment)
                .order_by(
                    Payment.payment_date.desc()
                )
            )

            return session.scalars(stmt).all()

    # =====================================
    # Actualizar
    # =====================================

    def update(self, payment):

        with SessionLocal() as session:

            session.merge(payment)

            session.commit()

            return payment

    # =====================================
    # Eliminar
    # =====================================

    def delete(self, payment_id):

        with SessionLocal() as session:

            payment = session.get(
                Payment,
                payment_id
            )

            if payment is None:
                return False

            session.delete(payment)

            session.commit()

            return True