import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QAbstractItemView, QComboBox, QSpinBox, QTabWidget
)
from PyQt6.QtCore import Qt


class InventarioView(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Inicializar Tablas en la DB
        self.init_db()

        # Layout Principal usando pestañas (Tabs) para separar las dos funciones
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        titulo = QLabel("Módulo de Inventario y Envases")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout_principal.addWidget(titulo)

        self.tabs = QTabWidget()
        layout_principal.addWidget(self.tabs)

        # Crear las dos pestañas internas
        self.tab_movimientos = QWidget()
        self.tab_botellones = QWidget()

        self.tabs.addTab(self.tab_movimientos, "📦 Entradas y Salidas (Ajustes)")
        self.tabs.addTab(self.tab_botellones, "🔄 Control de Botellones Retornables")

        # Configurar cada pestaña
        self.configurar_tab_movimientos()
        self.configurar_tab_botellones()

    def init_db(self):
        """Crea las tablas de historial de movimientos y control de envases"""
        self.conn = sqlite3.connect("agua_vere.db")
        self.cursor = self.conn.cursor()

        # Historial de entradas y salidas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT NOT NULL,
                tipo TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                motivo TEXT,
                fecha TEXT NOT NULL
            )
        """)

        # Historial de envases retornables prestados/devueltos por cliente
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS control_envases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                tipo_movimiento TEXT NOT NULL, -- 'Prestado' o 'Devuelto'
                cantidad INTEGER NOT NULL,
                fecha TEXT NOT NULL
            )
        """)
        self.conn.commit()

    # =========================================================================
    # PESTAÑA 1: ENTRADAS Y SALIDAS (AJUSTES DE STOCK)
    # =========================================================================
    def configurar_tab_movimientos(self):
        layout = QVBoxLayout()
        self.tab_movimientos.setLayout(layout)

        # Formulario de Ajuste
        layout_form = QHBoxLayout()

        lbl_prod = QLabel("Producto:")
        self.cb_productos = QComboBox()
        self.cb_productos.setFixedWidth(250)

        lbl_tipo = QLabel("Tipo:")
        self.cb_tipo_mov = QComboBox()
        self.cb_tipo_mov.addItems(["Entrada (+)", "Salida (-)"])

        lbl_cant = QLabel("Cantidad:")
        self.txt_cantidad_mov = QSpinBox()
        self.txt_cantidad_mov.setMinimum(1)
        self.txt_cantidad_mov.setMaximum(5000)

        self.txt_motivo = QLineEdit()
        self.txt_motivo.setPlaceholderText("Motivo (Ej: Compra a proveedor, Rotura...)")

        self.btn_registrar_mov = QPushButton("💾 Registrar Ajuste")
        self.btn_registrar_mov.setStyleSheet("background-color: #0EA5E9; color: white; font-weight: bold;")
        self.btn_registrar_mov.clicked.connect(self.procesar_ajuste_inventario)

        layout_form.addWidget(lbl_prod)
        layout_form.addWidget(self.cb_productos)
        layout_form.addWidget(lbl_tipo)
        layout_form.addWidget(self.cb_tipo_mov)
        layout_form.addWidget(lbl_cant)
        layout_form.addWidget(self.txt_cantidad_mov)
        layout_form.addWidget(self.txt_motivo)
        layout_form.addWidget(self.btn_registrar_mov)
        layout.addLayout(layout_form)

        # Tabla Historial de Ajustes
        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(5)
        self.tabla_movimientos.setHorizontalHeaderLabels(["Fecha", "Producto", "Tipo", "Cant.", "Motivo"])
        self.tabla_movimientos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.actualizar_combo_productos()
        self.cargar_tabla_movimientos()

    def actualizar_combo_productos(self):
        self.cb_productos.clear()
        try:
            self.cursor.execute("SELECT id, nombre, presentacion FROM productos")
            for p in self.cursor.fetchall():
                self.cb_productos.addItem(f"{p[1]} ({p[2]})", p[0])
        except sqlite3.OperationalError:
            pass

    def procesar_ajuste_inventario(self):
        if self.cb_productos.currentIndex() == -1:
            return

        id_prod = self.cb_productos.currentData()
        nombre_prod = self.cb_productos.currentText()
        tipo = self.cb_tipo_mov.currentText()
        cantidad = self.txt_cantidad_mov.value()
        motivo = self.txt_motivo.text().strip() or "Ajuste manual"
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Verificar si es salida para no dejar el stock en negativo
        if tipo == "Salida (-)":
            self.cursor.execute("SELECT existencia FROM productos WHERE id = ?", (id_prod,))
            stock_actual = self.cursor.fetchone()[0]
            if cantidad > stock_actual:
                QMessageBox.warning(self, "Error de Stock", f"No puedes retirar {cantidad} unidades. El stock actual es de {stock_actual}.")
                return
            cantidad_sql = -cantidad
        else:
            cantidad_sql = cantidad

        # 1. Actualizar stock en la tabla de productos
        self.cursor.execute("UPDATE productos SET existencia = existencia + ? WHERE id = ?", (cantidad_sql, id_prod))
        
        # 2. Registrar el log del movimiento
        self.cursor.execute(
            "INSERT INTO movimientos_inventario (producto, tipo, cantidad, motivo, fecha) VALUES (?, ?, ?, ?, ?)",
            (nombre_prod, tipo, cantidad, motivo, fecha)
        )
        self.conn.commit()

        QMessageBox.information(self, "Éxito", "Ajuste de inventario aplicado correctamente.")
        self.txt_motivo.clear()
        self.txt_cantidad_mov.setValue(1)
        self.cargar_tabla_movimientos()

    def cargar_tabla_movimientos(self):
        self.tabla_movimientos.setRowCount(0)
        self.cursor.execute("SELECT fecha, producto, tipo, cantidad, motivo FROM movimientos_inventario ORDER BY id DESC")
        for r_num, row in enumerate(self.cursor.fetchall()):
            self.tabla_movimientos.insertRow(r_num)
            for c_num, val in enumerate(row):
                self.tabla_movimientos.setItem(r_num, c_num, QTableWidgetItem(str(val)))


    # =========================================================================
    # PESTAÑA 2: CONTROL DE BOTELLONES RETORNABLES
    # =========================================================================
    def configurar_tab_botellones(self):
        layout = QVBoxLayout()
        self.tab_botellones.setLayout(layout)

        layout_form = QHBoxLayout()

        lbl_cli = QLabel("Cliente:")
        self.cb_clientes = QComboBox()
        self.cb_clientes.setFixedWidth(250)

        lbl_accion = QLabel("Acción:")
        self.cb_accion_envase = QComboBox()
        self.cb_accion_envase.addItems(["Prestar Botellones (Cliente se lleva vacíos)", "Devolver Botellones (Cliente entrega vacíos)"])

        lbl_cant = QLabel("Cantidad Envases:")
        self.txt_cantidad_envase = QSpinBox()
        self.txt_cantidad_envase.setMinimum(1)
        self.txt_cantidad_envase.setMaximum(500)

        self.btn_registrar_envase = QPushButton("🔄 Registrar Envases")
        self.btn_registrar_envase.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        self.btn_registrar_envase.clicked.connect(self.procesar_movimiento_envases)

        layout_form.addWidget(lbl_cli)
        layout_form.addWidget(self.cb_clientes)
        layout_form.addWidget(lbl_accion)
        layout_form.addWidget(self.cb_accion_envase)
        layout_form.addWidget(lbl_cant)
        layout_form.addWidget(self.txt_cantidad_envase)
        layout_form.addWidget(self.btn_registrar_envase)
        layout.addLayout(layout_form)

        # Tabla de Historial o Resumen por Cliente
        self.tabla_envases = QTableWidget()
        self.tabla_envases.setColumnCount(4)
        self.tabla_envases.setHorizontalHeaderLabels(["Fecha", "Cliente", "Operación", "Cant. Envases"])
        self.tabla_envases.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.actualizar_combo_clientes()
        self.cargar_tabla_envases()

    def actualizar_combo_clientes(self):
        self.cb_clientes.clear()
        try:
            self.cursor.execute("SELECT nombre FROM clientes")
            for c in self.cursor.fetchall():
                self.cb_clientes.addItem(c[0])
        except sqlite3.OperationalError:
            pass

    def procesar_movimiento_envases(self):
        if self.cb_clientes.currentIndex() == -1:
            return

        cliente = self.cb_clientes.currentText()
        accion = self.cb_accion_envase.currentText()
        cantidad = self.txt_cantidad_envase.value()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tipo_registro = "Prestado" if "Prestar" in accion else "Devuelto"

        # Guardar registro en la base de datos
        self.cursor.execute(
            "INSERT INTO control_envases (cliente, tipo_movimiento, cantidad, fecha) VALUES (?, ?, ?, ?)",
            (cliente, tipo_registro, cantidad, fecha)
        )
        self.conn.commit()

        QMessageBox.information(self, "Registro Exitoso", f"Se registraron {cantidad} envases como '{tipo_registro}' para {cliente}.")
        self.txt_cantidad_envase.setValue(1)
        self.cargar_tabla_envases()

    def cargar_tabla_envases(self):
        self.tabla_envases.setRowCount(0)
        self.cursor.execute("SELECT fecha, cliente, tipo_movimiento, cantidad FROM control_envases ORDER BY id DESC")
        for r_num, row in enumerate(self.cursor.fetchall()):
            self.tabla_envases.insertRow(r_num)
            for c_num, val in enumerate(row):
                self.tabla_envases.setItem(r_num, c_num, QTableWidgetItem(str(val)))

    # Método para refrescar combos al cambiar de pestaña general en el Dashboard
    def showEvent(self, event):
        self.actualizar_combo_productos()
        self.actualizar_combo_clientes()
        super().showEvent(event)