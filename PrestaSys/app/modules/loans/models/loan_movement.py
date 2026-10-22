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


class LoanMovement(Base):

    __tablename__ = "loan_movements"

    id = Column(Integer, primary_key=True)

    loan_id = Column(
        Integer,
        ForeignKey("loans.id"),
        nullable=False
    )

    movement_date = Column(
        Date,
        nullable=False
    )

    movement_type = Column(
        String(30),
        nullable=False
    )

    description = Column(
        String(200)
    )

    amount = Column(
        Float,
        default=0
    )

    previous_balance = Column(
        Float,
        default=0
    )

    new_balance = Column(
        Float,
        default=0
    )

    loan = relationship("Loan")