from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
)

from app.core.database.base import Base


class CashMovement(Base):

    __tablename__ = "cash_movements"

    id = Column(Integer, primary_key=True)

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
        nullable=False
    )

    balance = Column(
        Float,
        default=0
    )