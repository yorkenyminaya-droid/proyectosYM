from sqlalchemy import (
    Column,
    Integer,
    Float,
    Date,
    ForeignKey,
    String,
)

from sqlalchemy.orm import relationship

from app.core.database.base import Base


class Payment(Base):

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    loan_id = Column(
        Integer,
        ForeignKey("loans.id"),
        nullable=False
    )

    installment_id = Column(
        Integer,
        ForeignKey("loan_installments.id"),
        nullable=True
    )

    payment_date = Column(
        Date,
        nullable=False
    )

    capital_paid = Column(
        Float,
        default=0
    )

    interest_paid = Column(
        Float,
        default=0
    )

    late_fee = Column(
        Float,
        default=0
    )

    total_paid = Column(
        Float,
        nullable=False
    )

    payment_method = Column(
        String(30),
        default="EFECTIVO"
    )

    notes = Column(String)

    loan = relationship("Loan")

    installment = relationship("Installment")