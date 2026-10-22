from pathlib import Path

from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parents[3]

DB_DIR = BASE_DIR / "database"

DB_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_DIR / 'prestasys.db'}"

engine = create_engine(

    DATABASE_URL,

    echo=False,

    future=True

)