import sqlite3

def conectar():
    conexion = sqlite3.connect("sistema.db")
    return conexion

def crear_tablas():
    con = conectar()
    cursor = con.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        existencia INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facturas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        cliente_id INTEGER,
        total REAL
    )
    """)

    con.commit()
    con.close()

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada correctamente.")