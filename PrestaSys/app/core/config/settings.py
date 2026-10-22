from pathlib import Path

APP_NAME = "PrestaSys"

APP_VERSION = "0.1.0 Alpha"

BASE_DIR = Path(__file__).resolve().parents[3]

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "prestasys.db"

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"