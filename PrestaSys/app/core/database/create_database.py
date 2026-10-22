from app.core.database.base import Base
from app.core.database.connection import engine

# ==========================
# Clientes
# ==========================

from app.modules.clients.model import Client

# ==========================
# Préstamos
# ==========================

from app.modules.loans.models.loan import Loan
from app.modules.loans.models.installment import Installment
from app.modules.loans.models.payment import Payment
from app.modules.loans.models.loan_movement import LoanMovement
from app.modules.loans.models.cash_movement import CashMovement


def create_database():

    Base.metadata.create_all(engine)