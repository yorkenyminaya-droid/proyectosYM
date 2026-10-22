import sqlite3
from config import DATABASE


def get_connection():

    conexion = sqlite3.connect(DATABASE)

    conexion.row_factory = sqlite3.Row

    return conexion


def crear_bd():

    conexion = get_connection()

    cursor = conexion.cursor()

    # TABLA ACTIVIDADES

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS actividades(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nombre TEXT NOT NULL,

        fecha TEXT NOT NULL,

        anio INTEGER NOT NULL,

        mes TEXT NOT NULL,

        carpeta TEXT NOT NULL

    )

    """)

    # TABLA FOTOS

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS fotos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        actividad_id INTEGER,

        nombre_archivo TEXT,

        ruta TEXT,

        tamano INTEGER,

        fecha_subida TEXT,

        FOREIGN KEY(actividad_id)

        REFERENCES actividades(id)

    )

    """)

    conexion.commit()

    conexion.close()