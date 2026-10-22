from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.core.database.base import Base


class Installment(Base):

    __tablename__ = "loan_installments"

    # =====================================
    # Identificación
    # =====================================

    id = Column(
        Integer,
        primary_key=True
    )

    loan_id = Column(
        Integer,
        ForeignKey("loans.id"),
        nullable=False
    )

    installment_number = Column(
        Integer,
        nullable=False
    )

    # =====================================
    # Fechas
    # =====================================

    due_date = Column(
        Date,
        nullable=False
    )

    payment_date = Column(Date)

    # =====================================
    # Valores
    # =====================================

    capital_amount = Column(
        Float,
        nullable=False
    )

    interest_amount = Column(
        Float,
        nullable=False
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    paid_amount = Column(
        Float,
        default=0
    )

    balance = Column(
        Float,
        nullable=False
    )

    # =====================================
    # Estado
    # =====================================

    status = Column(
        String(20),
        default="PENDIENTE"
    )

    # =====================================
    # Relación
    # =====================================

    loan = relationship("Loan")