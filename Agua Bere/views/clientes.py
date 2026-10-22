import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt


class ClientesView(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Inicializar la Base de Datos
        self.init_db()

        # 2. Configuración del Layout Principal
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # ==========================================
        # BARRA SUPERIOR (Título y Búsqueda)
        # ==========================================
        barra_superior = QHBoxLayout()
        
        titulo = QLabel("Gestión de Clientes")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        barra_superior.addWidget(titulo)
        barra_superior.addStretch()

        # Buscador
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar cliente por nombre...")
        self.txt_buscar.setFixedWidth(250)
        self.txt_buscar.textChanged.connect(self.buscar_cliente) # Busca en tiempo real
        barra_superior.addWidget(self.txt_buscar)
        
        layout_principal.addLayout(barra_superior)

        # ==========================================
        # FORMULARIO DE ENTRADA DE DATOS
        # ==========================================
        layout_formulario = QHBoxLayout()
        
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre Completo")
        
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Teléfono")
        
        self.txt_balance = QLineEdit()
        self.txt_balance.setPlaceholderText("Balance Inicial (Ej: 0.00)")

        layout_formulario.addWidget(self.txt_nombre)
        layout_formulario.addWidget(self.txt_telefono)
        layout_formulario.addWidget(self.txt_balance)
        
        layout_principal.addLayout(layout_formulario)

        # ==========================================
        # BOTONERA DE ACCIONES
        # ==========================================
        layout_botones = QHBoxLayout()

        self.btn_guardar = QPushButton("💾 Guardar / Registrar")
        self.btn_guardar.clicked.connect(self.guardar_cliente)

        self.btn_editar = QPushButton("✏️ Editar Seleccionado")
        self.btn_editar.clicked.connect(self.cargar_para_editar)

        self.btn_eliminar = QPushButton("❌ Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)

        self.btn_limpiar = QPushButton("🧹 Nuevo / Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        # Estilos rápidos para los botones
        estilo_botones = "QPushButton { padding: 8px 15px; font-weight: bold; }"
        for btn in [self.btn_guardar, self.btn_editar, self.btn_eliminar, self.btn_limpiar]:
            btn.setStyleSheet(estilo_botones)
            layout_botones.addWidget(btn)
            
        layout_botones.addStretch()
        layout_principal.addLayout(layout_botones)

        # ==========================================
        # TABLA DE CLIENTES
        # ==========================================
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Balance"])
        
        # Ajustes de comportamiento de la tabla
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # No editar directo en celda
        
        layout_principal.addWidget(self.tabla)

        # ID oculto para saber si estamos editando un cliente existente
        self.cliente_id_actual = None

        # Cargar los datos iniciales
        self.cargar_tabla()

    # ==========================================
    # LÓGICA DE BASE DE DATOS Y FUNCIONES
    # ==========================================

    def init_db(self):
        """Crea la conexión y la tabla si no existen"""
        self.conn = sqlite3.connect("agua_vere.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT,
                balance REAL DEFAULT 0.0
            )
        """)
        self.conn.commit()

    def cargar_tabla(self, datos=None):
        """Renderiza los datos en el QTableWidget"""
        if datos is None:
            self.cursor.execute("SELECT * FROM clientes")
            datos = self.cursor.fetchall()

        self.tabla.setRowCount(0)
        for row_number, row_data in enumerate(datos):
            self.tabla.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if column_number == 0:  # Centrar el ID
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(row_number, column_number, item)

    def guardar_cliente(self):
        """Guarda un nuevo cliente o actualiza uno existente"""
        nombre = self.txt_nombre.text().strip()
        telefono = self.txt_telefono.text().strip()
        balance = self.txt_balance.text().strip() or "0.0"

        if not nombre:
            QMessageBox.warning(self, "Campos Vacíos", "El nombre es obligatorio.")
            return

        try:
            balance_float = float(balance)
        except ValueError:
            QMessageBox.warning(self, "Error de Datos", "El balance debe ser un número válido.")
            return

        if self.cliente_id_actual is None:
            # NUEVO CLIENTE
            self.cursor.execute(
                "INSERT INTO clientes (nombre, telefono, balance) VALUES (?, ?, ?)",
                (nombre, telefono, balance_float)
            )
            QMessageBox.information(self, "Éxito", "Cliente registrado correctamente.")
        else:
            # EDITAR CLIENTE EXISTENTE
            self.cursor.execute(
                "UPDATE clientes SET nombre=?, telefono=?, balance=? WHERE id=?",
                (nombre, telefono, balance_float, self.cliente_id_actual)
            )
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")

        self.conn.commit()
        self.limpiar_formulario()
        self.cargar_tabla()

    def cargar_para_editar(self):
        """Pasa los datos de la fila seleccionada de la tabla al formulario"""
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un cliente de la tabla.")
            return

        # Recuperar datos de la fila
        self.cliente_id_actual = int(self.tabla.item(fila_seleccionada, 0).text())
        self.txt_nombre.setText(self.tabla.item(fila_seleccionada, 1).text())
        self.txt_telefono.setText(self.tabla.item(fila_seleccionada, 2).text())
        self.txt_balance.setText(self.tabla.item(fila_seleccionada, 3).text())
        
        self.btn_guardar.setText("💾 Actualizar Cliente")

    def eliminar_cliente(self):
        """Elimina el registro seleccionado"""
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un cliente para eliminar.")
            return

        id_cliente = self.tabla.item(fila_seleccionada, 0).text()
        nombre_cliente = self.tabla.item(fila_seleccionada, 1).text()

        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación", 
            f"¿Estás seguro de que deseas eliminar al cliente '{nombre_cliente}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmacion == QMessageBox.StandardButton.Yes:
            self.cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
            self.conn.commit()
            QMessageBox.information(self, "Eliminado", "Cliente borrado con éxito.")
            self.limpiar_formulario()
            self.cargar_tabla()

    def buscar_cliente(self):
        """Filtra la tabla según el texto del buscador"""
        texto = self.txt_buscar.text().strip()
        if texto == "":
            self.cargar_tabla()
        else:
            self.cursor.execute("SELECT * FROM clientes WHERE nombre LIKE ?", (f"%{texto}%",))
            resultados = self.cursor.fetchall()
            self.cargar_tabla(resultados)

    def limpiar_formulario(self):
        """Restablece los campos de texto y el estado de edición"""
        self.txt_nombre.clear()
        self.txt_telefono.clear()
        self.txt_balance.clear()
        self.cliente_id_actual = None
        self.btn_guardar.setText("💾 Guardar / Registrar")
        self.tabla.clearSelection()