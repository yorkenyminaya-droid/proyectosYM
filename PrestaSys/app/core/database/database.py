"""
Configuración del motor de base de datos.
"""

from sqlalchemy import create_engine

from app.core.config.settings import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)