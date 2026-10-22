import os
from pathlib import Path

# Carpeta donde SIGAFI guardará la información del usuario
DATA_DIR = Path.home() / "Documents" / "SIGAFI"

# Crear la carpeta si no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Crear la carpeta uploads si no existe
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


class Config:

    SECRET_KEY = "SIGAFI-2026"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(DATA_DIR / "galeria.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = str(UPLOADS_DIR)

    # LOGIN
    ADMIN_USER = "administrador"
    ADMIN_PASSWORD = "Iseepenc2026"