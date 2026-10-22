from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database.session import SessionLocal
from app.modules.loans.models import Loan


class LoanRepository:

    def add(self, loan):

        with SessionLocal() as session:

            session.add(loan)

            session.commit()

            session.refresh(loan)

            return loan

    def get_all(self):

        with SessionLocal() as session:

            stmt = (
            select(Loan)
            .options(
                joinedload(Loan.client)
            )
            .order_by(Loan.id.desc())
        )

        return session.scalars(stmt).all()

    def get_last(self):

        with SessionLocal() as session:

            stmt = (
                select(Loan)
                .order_by(Loan.id.desc())
            )

            return session.scalar(stmt)

    def get_by_id(self, loan_id):

        with SessionLocal() as session:

            stmt = (
            select(Loan)
            .options(
                joinedload(Loan.client)
            )
            .where(Loan.id == loan_id)
        )

        return session.scalar(stmt)

    def update(self, loan_id, data):

        with SessionLocal() as session:

         loan = session.get(Loan, loan_id)

        if loan is None:
            return None

        loan.client_id = data["client_id"]

        loan.loan_type = data["loan_type"]

        loan.payment_frequency = data["payment_frequency"]

        loan.principal_amount = data["principal_amount"]

        loan.interest_rate = data["interest_rate"]

        loan.total_amount = data["total_amount"]

        loan.installments = data["installments"]

        loan.installment_amount = data["installment_amount"]

        loan.start_date = data["start_date"]

        loan.due_date = data["due_date"]

        loan.notes = data["notes"]

        session.commit()

        session.refresh(loan)

        return loan