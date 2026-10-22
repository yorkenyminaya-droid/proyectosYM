"""
Constantes del módulo de préstamos.
"""

# ==========================================
# Tipos de préstamo
# ==========================================

LOAN_TYPE_PLAZO = "PLAZO"
LOAN_TYPE_REDITO = "REDITO"

LOAN_TYPES = [
    LOAN_TYPE_PLAZO,
    LOAN_TYPE_REDITO,
]

# ==========================================
# Frecuencia de pago
# ==========================================

FREQUENCY_DAILY = "DIARIO"
FREQUENCY_WEEKLY = "SEMANAL"
FREQUENCY_BIWEEKLY = "QUINCENAL"
FREQUENCY_MONTHLY = "MENSUAL"

PAYMENT_FREQUENCIES = [
    FREQUENCY_DAILY,
    FREQUENCY_WEEKLY,
    FREQUENCY_BIWEEKLY,
    FREQUENCY_MONTHLY,
]

# ==========================================
# Estados del préstamo
# ==========================================

LOAN_ACTIVE = "ACTIVO"
LOAN_LATE = "MORA"
LOAN_CANCELLED = "CANCELADO"
LOAN_REFINANCED = "REFINANCIADO"

LOAN_STATUSES = [
    LOAN_ACTIVE,
    LOAN_LATE,
    LOAN_CANCELLED,
    LOAN_REFINANCED,
]