import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QAbstractItemView, QComboBox
)
from PyQt6.QtCore import Qt


class ProductosView(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Inicializar la Base de Datos para Productos
        self.init_db()

        # 2. Configuración del Layout Principal
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # ==========================================
        # BARRA SUPERIOR (Título y Búsqueda)
        # ==========================================
        barra_superior = QHBoxLayout()
        
        titulo = QLabel("Inventario de Productos")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        barra_superior.addWidget(titulo)
        barra_superior.addStretch()

        # Buscador en tiempo real
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar producto...")
        self.txt_buscar.setFixedWidth(250)
        self.txt_buscar.textChanged.connect(self.buscar_producto)
        barra_superior.addWidget(self.txt_buscar)
        
        layout_principal.addLayout(barra_superior)

        # ==========================================
        # FORMULARIO DE ENTRADA DE DATOS
        # ==========================================
        layout_formulario = QHBoxLayout()
        
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre del Producto (Ej: Agua Purificada)")
        
        # Selector de Presentación (Botellón, Botella 500ml, etc.)
        self.cb_presentacion = QComboBox()
        self.cb_presentacion.addItems([
            "Botellón 5 Galones",
            "Botella 500 ml",
            "Botella 1 Litro",
            "Botella 1.5 Litros",
            "Paquete de Vasos",
            "Otros"
        ])
        
        self.txt_precio = QLineEdit()
        self.txt_precio.setPlaceholderText("Precio Venta (RD$)")
        
        self.txt_existencia = QLineEdit()
        self.txt_existencia.setPlaceholderText("Existencia Inicial")

        layout_formulario.addWidget(self.txt_nombre, stretch=2)
        layout_formulario.addWidget(self.cb_presentacion, stretch=1)
        layout_formulario.addWidget(self.txt_precio, stretch=1)
        layout_formulario.addWidget(self.txt_existencia, stretch=1)
        
        layout_principal.addLayout(layout_formulario)

        # ==========================================
        # BOTONERA DE ACCIONES
        # ==========================================
        layout_botones = QHBoxLayout()

        self.btn_guardar = QPushButton("💾 Guardar Producto")
        self.btn_guardar.clicked.connect(self.guardar_producto)

        self.btn_editar = QPushButton("✏️ Editar Seleccionado")
        self.btn_editar.clicked.connect(self.cargar_para_editar)

        self.btn_eliminar = QPushButton("❌ Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_producto)

        self.btn_limpiar = QPushButton("🧹 Nuevo / Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        # Estilo estético para botones
        estilo_botones = "QPushButton { padding: 8px 15px; font-weight: bold; }"
        for btn in [self.btn_guardar, self.btn_editar, self.btn_eliminar, self.btn_limpiar]:
            btn.setStyleSheet(estilo_botones)
            layout_botones.addWidget(btn)
            
        layout_botones.addStretch()
        layout_principal.addLayout(layout_botones)

        # ==========================================
        # TABLA DE PRODUCTOS
        # ==========================================
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Producto", "Presentación", "Precio", "Existencia"])
        
        # Ajustes de comportamiento de la tabla
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout_principal.addWidget(self.tabla)

        # Control del ID en edición
        self.producto_id_actual = None

        # Cargar los datos iniciales de la DB a la tabla
        self.cargar_tabla()

    # ==========================================
    # LÓGICA DE BASE DE DATOS Y OPERACIONES
    # ==========================================

    def init_db(self):
        """Conecta a la base de datos compartida y crea la tabla productos"""
        self.conn = sqlite3.connect("agua_vere.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                presentacion TEXT NOT NULL,
                precio REAL DEFAULT 0.0,
                existencia INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def cargar_tabla(self, datos=None):
        """Llena el QTableWidget con los productos de la DB"""
        if datos is None:
            self.cursor.execute("SELECT * FROM productos")
            datos = self.cursor.fetchall()

        self.tabla.setRowCount(0)
        for row_number, row_data in enumerate(datos):
            self.tabla.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                # Formatear y centrar columnas numéricas o ID
                if column_number in [0, 2, 3, 4]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column_number == 3: # Columna Precio
                    item.setText(f"RD$ {float(data):,.2f}")
                
                self.tabla.setItem(row_number, column_number, item)

    def guardar_producto(self):
        """Crea o edita un registro de producto"""
        nombre = self.txt_nombre.text().strip()
        presentacion = self.cb_presentacion.currentText()
        precio = self.txt_precio.text().strip() or "0.0"
        existencia = self.txt_existencia.text().strip() or "0"

        if not nombre:
            QMessageBox.warning(self, "Campos Vacíos", "El nombre del producto es obligatorio.")
            return

        # Validaciones de tipos numéricos numéricas
        try:
            precio_float = float(precio)
            existencia_int = int(existencia)
        except ValueError:
            QMessageBox.warning(self, "Error de Formato", "El precio debe ser un número decimal y la existencia un entero.")
            return

        if self.producto_id_actual is None:
            # GUARDAR NUEVO
            self.cursor.execute(
                "INSERT INTO productos (nombre, presentacion, precio, existencia) VALUES (?, ?, ?, ?)",
                (nombre, presentacion, precio_float, existencia_int)
            )
            QMessageBox.information(self, "Éxito", "Producto registrado en el inventario.")
        else:
            # ACTUALIZAR EXISTENTE
            self.cursor.execute(
                "UPDATE productos SET nombre=?, presentacion=?, precio=?, existencia=? WHERE id=?",
                (nombre, presentacion, precio_float, existencia_int, self.producto_id_actual)
            )
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")

        self.conn.commit()
        self.limpiar_formulario()
        self.cargar_tabla()

    def cargar_para_editar(self):
        """Envía el producto seleccionado al formulario superior"""
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un producto de la tabla.")
            return

        self.producto_id_actual = int(self.tabla.item(fila_seleccionada, 0).text())
        self.txt_nombre.setText(self.tabla.item(fila_seleccionada, 1).text())
        
        # Setea el ComboBox de la presentación
        texto_presentacion = self.tabla.item(fila_seleccionada, 2).text()
        index = self.cb_presentacion.findText(texto_presentacion)
        if index >= 0:
            self.cb_presentacion.setCurrentIndex(index)

        # Limpiar el formato 'RD$ ' para poder editar el número puro
        precio_limpio = self.tabla.item(fila_seleccionada, 3).text().replace("RD$ ", "").replace(",", "")
        self.txt_precio.setText(precio_limpio)
        
        self.txt_existencia.setText(self.tabla.item(fila_seleccionada, 4).text())
        
        self.btn_guardar.setText("💾 Actualizar Producto")

    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona un producto para eliminar.")
            return

        id_prod = self.tabla.item(fila_seleccionada, 0).text()
        nombre_prod = self.tabla.item(fila_seleccionada, 1).text()

        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación", 
            f"¿Estás seguro de que deseas eliminar '{nombre_prod}' del inventario?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmacion == QMessageBox.StandardButton.Yes:
            self.cursor.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
            self.conn.commit()
            QMessageBox.information(self, "Eliminado", "Producto removido exitosamente.")
            self.limpiar_formulario()
            self.cargar_tabla()

    def buscar_producto(self):
        """Filtrado interactivo en tiempo real"""
        texto = self.txt_buscar.text().strip()
        if texto == "":
            self.cargar_tabla()
        else:
            self.cursor.execute("SELECT * FROM productos WHERE nombre LIKE ? OR presentacion LIKE ?", (f"%{texto}%", f"%{texto}%"))
            resultados = self.cursor.fetchall()
            self.cargar_tabla(resultados)

    def limpiar_formulario(self):
        """Limpia los campos para habilitar un nuevo registro"""
        self.txt_nombre.clear()
        self.cb_presentacion.setCurrentIndex(0)
        self.txt_precio.clear()
        self.txt_existencia.clear()
        self.producto_id_actual = None
        self.btn_guardar.setText("💾 Guardar Producto")
        self.tabla.clearSelection()