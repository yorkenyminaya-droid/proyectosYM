from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Date,
    Text,
)

from sqlalchemy.orm import relationship

from app.core.database.base import Base


class Loan(Base):

    __tablename__ = "loans"

    # =====================================
    # Identificación
    # =====================================

    id = Column(Integer, primary_key=True)

    code = Column(
        String(20),
        unique=True,
        nullable=False
    )

    # =====================================
    # Cliente
    # =====================================

    client_id = Column(
        Integer,
        ForeignKey("clients.id"),
        nullable=False
    )

    client = relationship("Client")

    # =====================================
    # Tipo de préstamo
    # =====================================

    loan_type = Column(
        String(20),
        nullable=False
    )

    payment_frequency = Column(
        String(20),
        nullable=False
    )

    # =====================================
    # Valores financieros
    # =====================================

    # Capital entregado
    principal_amount = Column(
        Float,
        nullable=False
    )

    # Saldo actual
    current_balance = Column(
        Float,
        nullable=False
    )

    # Tasa de interés (%)
    interest_rate = Column(
        Float,
        nullable=False
    )

    # Total del préstamo (solo cuotas)
    total_amount = Column(
        Float,
        default=0
    )

    # Cantidad de cuotas
    installments = Column(
        Integer,
        default=0
    )

    # Valor de la cuota
    installment_amount = Column(
        Float,
        default=0
    )

    # =====================================
    # Control financiero
    # =====================================

    capital_paid = Column(
        Float,
        default=0
    )

    interest_paid = Column(
        Float,
        default=0
    )

    # =====================================
    # Fechas
    # =====================================

    start_date = Column(
        Date,
        nullable=False
    )

    due_date = Column(Date)

    next_payment_date = Column(Date)

    last_payment_date = Column(Date)

    # =====================================
    # Estado
    # =====================================

    status = Column(
        String(20),
        default="ACTIVO"
    )

    # =====================================
    # Observaciones
    # =====================================

    notes = Column(Text)