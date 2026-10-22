import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QAbstractItemView, QComboBox, QSpinBox, QGridLayout
    
)
from PyQt6.QtCore import Qt


class VentasView(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Inicializar Tablas de Facturación en la DB
        self.init_db()

        # Listas en memoria para el carrito de compras actual
        self.carrito = []
        self.cliente_seleccionado = None

        # Layout Principal
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # Título
        titulo = QLabel("Módulo de Facturación (Nueva Venta)")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout_principal.addWidget(titulo)

        # ==========================================
        # SECCIÓN 1: SELECCIÓN DE CLIENTE
        # ==========================================
        layout_cliente = QHBoxLayout()
        
        lbl_cli = QLabel("Cliente:")
        lbl_cli.setStyleSheet("font-weight: bold;")
        self.cb_clientes = QComboBox()
        self.cb_clientes.setFixedWidth(300)
        self.actualizar_combo_clientes()
        
        layout_cliente.addWidget(lbl_cli)
        layout_cliente.addWidget(self.cb_clientes)
        layout_cliente.addStretch()
        
        layout_principal.addLayout(layout_cliente)

        # ==========================================
        # SECCIÓN 2: AGREGAR PRODUCTOS AL CARRITO
        # ==========================================
        layout_productos = QHBoxLayout()

        lbl_prod = QLabel("Producto:")
        lbl_prod.setStyleSheet("font-weight: bold;")
        self.cb_productos = QComboBox()
        self.cb_productos.setFixedWidth(300)
        self.actualizar_combo_productos()

        lbl_cant = QLabel("Cantidad:")
        lbl_cant.setStyleSheet("font-weight: bold;")
        self.txt_cantidad = QSpinBox()
        self.txt_cantidad.setMinimum(1)
        self.txt_cantidad.setMaximum(1000)
        self.txt_cantidad.setFixedWidth(80)

        self.btn_agregar = QPushButton("➕ Agregar")
        self.btn_agregar.setStyleSheet("background-color: #0EA5E9; color: white; font-weight: bold; padding: 5px 15px;")
        self.btn_agregar.clicked.connect(self.agregar_al_carrito)

        layout_productos.addWidget(lbl_prod)
        layout_productos.addWidget(self.cb_productos)
        layout_productos.addWidget(lbl_cant)
        layout_productos.addWidget(self.txt_cantidad)
        layout_productos.addWidget(self.btn_agregar)
        layout_productos.addStretch()

        layout_principal.addLayout(layout_productos)

        # ==========================================
        # SECCIÓN 3: TABLA DE DETALLES (CARRITO)
        # ==========================================
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["ID Prod", "Descripción", "Cantidad", "Precio Unitario", "Subtotal"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_carrito.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_carrito.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout_principal.addWidget(self.tabla_carrito)

        # Botón para remover del carrito
        self.btn_remover = QPushButton("🗑️ Quitar Item Seleccionado")
        self.btn_remover.setFixedWidth(200)
        self.btn_remover.clicked.connect(self.remover_del_carrito)
        layout_principal.addWidget(self.btn_remover)

        # ==========================================
        # SECCIÓN 4: TOTALES Y PROCESAMIENTO
        # ==========================================
        layout_inferior = QHBoxLayout()

        # Botones de Factura al lado izquierdo
        layout_acciones_factura = QVBoxLayout()
        self.btn_facturar = QPushButton("🧾 Registrar y Guardar Factura")
        self.btn_facturar.setStyleSheet("background-color: #10B981; color: white; font-size: 16px; font-weight: bold; padding: 10px;")
        self.btn_facturar.clicked.connect(self.procesar_factura)

        self.btn_imprimir = QPushButton("🖨️ Imprimir Última Factura (Simulación)")
        self.btn_imprimir.setStyleSheet("font-weight: bold; padding: 8px;")
        self.btn_imprimir.clicked.connect(self.imprimir_ticket_consola)

        layout_acciones_factura.addWidget(self.btn_facturar)
        layout_acciones_factura.addWidget(self.btn_imprimir)
        layout_inferior.addLayout(layout_acciones_factura)
        layout_inferior.addStretch()

        # Cuadro de Totales al lado derecho
        layout_totales = QGridLayout()
        
        lbl_t_sub = QLabel("Subtotal:")
        self.val_subtotal = QLabel("RD$ 0.00")
        lbl_t_itbis = QLabel("ITBIS (18%):")
        self.val_itbis = QLabel("RD$ 0.00")
        lbl_t_total = QLabel("TOTAL:")
        self.val_total = QLabel("RD$ 0.00")
        
        # Estilos de etiquetas de totales
        self.val_total.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        lbl_t_total.setStyleSheet("font-size: 20px; font-weight: bold;")

        layout_totales.addWidget(lbl_t_sub, 0, 0)
        layout_totales.addWidget(self.val_subtotal, 0, 1)
        layout_totales.addWidget(lbl_t_itbis, 1, 0)
        layout_totales.addWidget(self.val_itbis, 1, 1)
        layout_totales.addWidget(lbl_t_total, 2, 0)
        layout_totales.addWidget(self.val_total, 2, 1)

        layout_inferior.addLayout(layout_totales)
        layout_principal.addLayout(layout_inferior)

        # ID de la última factura creada para impresión
        self.ultima_factura_id = None

    # ==========================================
    # LÓGICA DE NEGOCIO Y BASE DE DATOS
    # ==========================================

    def init_db(self):
        """Crea las tablas relacionales de facturas"""
        self.conn = sqlite3.connect("agua_vere.db")
        self.cursor = self.conn.cursor()
        
        # Tabla Maestra de Facturas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                fecha TEXT NOT NULL,
                subtotal REAL,
                itbis REAL,
                total REAL
            )
        """)
        
        # Tabla Detalle de Facturas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalles_factura (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER,
                producto_id INTEGER,
                descripcion TEXT,
                cantidad INTEGER,
                precio REAL,
                subtotal REAL,
                FOREIGN KEY(factura_id) REFERENCES facturas(id)
            )
        """)
        self.conn.commit()

    def actualizar_combo_clientes(self):
        """Busca y mapea los clientes registrados desde la base de datos"""
        self.cb_clientes.clear()
        try:
            self.cursor.execute("SELECT nombre FROM clientes")
            clientes = self.cursor.fetchall()
            if clientes:
                for c in clientes:
                    self.cb_clientes.addItem(c[0])
            else:
                self.cb_clientes.addItem("Cliente General (Contado)")
        except sqlite3.OperationalError:
            self.cb_clientes.addItem("Cliente General (Contado)")

    def actualizar_combo_productos(self):
        """Muestra los productos disponibles en inventario con sus respectivos precios"""
        self.cb_productos.clear()
        try:
            self.cursor.execute("SELECT id, nombre, presentacion, precio, existencia FROM productos")
            self.productos_db = self.cursor.fetchall()
            for p in self.productos_db:
                # Texto descriptivo para el ComboBox: Nombre [Presentación] - RD$ Precio (Stock)
                texto = f"{p[1]} ({p[2]}) - RD$ {p[3]:,.2f} [Stock: {p[4]}]"
                self.cb_productos.addItem(texto, p) # Guardamos el objeto completo 'p' como userData
        except sqlite3.OperationalError:
            pass

    def agregar_al_carrito(self):
        """Suma un producto y calcula sus subtotales en la grilla visual"""
        if self.cb_productos.currentIndex() == -1:
            return

        # Recuperar la data del producto guardada en el combo
        producto_data = self.cb_productos.currentData()
        id_prod, nombre, presentacion, precio, stock = producto_data
        cantidad = self.txt_cantidad.value()

        if cantidad > stock:
            QMessageBox.warning(self, "Stock Insuficiente", f"No puedes vender {cantidad} unidades. Solo quedan {stock} en existencia.")
            return

        # Verificar si el item ya está en el carrito para sumar la cantidad
        for item in self.carrito:
            if item['id'] == id_prod:
                if item['cantidad'] + cantidad > stock:
                    QMessageBox.warning(self, "Stock Insuficiente", "La cantidad total del carrito supera las existencias.")
                    return
                item['cantidad'] += cantidad
                item['subtotal'] = item['cantidad'] * item['precio']
                self.redibujar_carrito()
                return

        # Si es nuevo, lo añadimos
        desc_completa = f"{nombre} ({presentacion})"
        item_carrito = {
            'id': id_prod,
            'descripcion': desc_completa,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': cantidad * precio
        }
        self.carrito.append(item_carrito)
        self.redibujar_carrito()

    def redibujar_carrito(self):
        """Refresca los items visuales en el QTableWidget y actualiza cálculos numéricos"""
        self.tabla_carrito.setRowCount(0)
        subtotal_general = 0.0

        for r_num, item in enumerate(self.carrito):
            self.tabla_carrito.insertRow(r_num)
            self.tabla_carrito.setItem(r_num, 0, QTableWidgetItem(str(item['id'])))
            self.tabla_carrito.setItem(r_num, 1, QTableWidgetItem(item['descripcion']))
            self.tabla_carrito.setItem(r_num, 2, QTableWidgetItem(str(item['cantidad'])))
            self.tabla_carrito.setItem(r_num, 3, QTableWidgetItem(f"RD$ {item['precio']:,.2f}"))
            self.tabla_carrito.setItem(r_num, 4, QTableWidgetItem(f"RD$ {item['subtotal']:,.2f}"))
            
            subtotal_general += item['subtotal']

        # Cálculos económicos fiscales (ITBIS 18%)
        itbis = subtotal_general * 0.18
        total = subtotal_general + itbis

        # Guardar en memoria de clase los valores numéricos brutos
        self.subtotal_num = subtotal_general
        self.itbis_num = itbis
        self.total_num = total

        # Renderizar textos formateados en la UI
        self.val_subtotal.setText(f"RD$ {subtotal_general:,.2f}")
        self.val_itbis.setText(f"RD$ {itbis:,.2f}")
        self.val_total.setText(f"RD$ {total:,.2f}")

    def remover_del_carrito(self):
        """Elimina la fila seleccionada del arreglo del carrito"""
        fila = self.tabla_carrito.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Selecciona un artículo de la tabla para quitarlo.")
            return
        self.carrito.pop(fila)
        self.redibujar_carrito()

    def procesar_factura(self):
        """Guarda la transacción maestra, sus renglones y descuenta el stock de productos"""
        if not self.carrito:
            QMessageBox.warning(self, "Carrito Vacío", "No puedes facturar si no has agregado productos.")
            return

        cliente = self.cb_clientes.currentText()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Insertar Factura Maestra
        self.cursor.execute(
            "INSERT INTO facturas (cliente, fecha, subtotal, itbis, total) VALUES (?, ?, ?, ?, ?)",
            (cliente, fecha_actual, self.subtotal_num, self.itbis_num, self.total_num)
        )
        self.ultima_factura_id = self.cursor.lastrowid

        # 2. Insertar Detalles de factura y descontar inventario de cada artículo
        for item in self.carrito:
            self.cursor.execute(
                "INSERT INTO detalles_factura (factura_id, producto_id, descripcion, cantidad, precio, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                (self.ultima_factura_id, item['id'], item['descripcion'], item['cantidad'], item['precio'], item['subtotal'])
            )
            
            # Restar existencias en la tabla productos
            self.cursor.execute(
                "UPDATE productos SET existencia = existencia - ? WHERE id = ?",
                (item['cantidad'], item['id'])
            )

        self.conn.commit()
        QMessageBox.information(self, "Venta Exitosa", f"Factura #{self.ultima_factura_id} generada y guardada correctamente.")
        
        # Limpiar carrito y refrescar combos de stock actualizado
        self.carrito.clear()
        self.redibujar_carrito()
        self.actualizar_combo_productos()

    def imprimir_ticket_consola(self):
        """Genera y emite un diseño estructurado tipo Ticket POS para impresión en consola térmica"""
        if self.ultima_factura_id is None:
            QMessageBox.warning(self, "Sin registros", "No hay ninguna factura procesada en esta sesión para imprimir.")
            return

        # Re-buscar los datos actualizados de la DB para la simulación fiel de la impresión
        self.cursor.execute("SELECT * FROM facturas WHERE id = ?", (self.ultima_factura_id,))
        factura = self.cursor.fetchone()
        
        self.cursor.execute("SELECT descripcion, cantidad, precio, subtotal FROM detalles_factura WHERE factura_id = ?", (self.ultima_factura_id,))
        detalles = self.cursor.fetchall()

        # Armado de ticket de formato POS (Impresión limpia)
        ticket = []
        ticket.append("==========================================")
        ticket.append("               AGUA VERE                  ")
        ticket.append("         SISTEMA DE FACTURACIÓN           ")
        ticket.append("==========================================")
        ticket.append(f"Factura No:  {factura[0]}")
        ticket.append(f"Fecha/Hora:  {factura[2]}")
        ticket.append(f"Cliente:     {factura[1]}")
        ticket.append("------------------------------------------")
        ticket.append(f"{'Cant. Descripción':<25} {'Precio':<8} {'Total':<8}")
        ticket.append("------------------------------------------")
        
        for det in detalles:
            linea = f"{det[1]} x{det[0]:<2}  {det[2]:>6.2f} {det[3]:>8.2f}"
            ticket.append(linea)
            
        ticket.append("------------------------------------------")
        ticket.append(f"Subtotal:                      RD$ {factura[3]:,.2f}")
        ticket.append(f"ITBIS (18%):                   RD$ {factura[4]:,.2f}")
        ticket.append(f"TOTAL:                         RD$ {factura[5]:,.2f}")
        ticket.append("==========================================")
        ticket.append("        ¡Gracias por su preferencia!       ")
        ticket.append("==========================================\n")

        # Imprime directamente en la salida de comandos / terminal
        print("\n".join(ticket))
        QMessageBox.information(self, "Impresora POS", "El ticket de venta estructurado se envió a la consola del sistema.")