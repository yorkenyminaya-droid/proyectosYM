from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel,
    QPushButton, QFrame, QVBoxLayout,
    QHBoxLayout, QGridLayout, QStackedWidget
)
from PyQt6.QtCore import Qt

# Importaciones de tus otras vistas independientes
from views.clientes import ClientesView
from views.productos import ProductosView
from views.ventas import VentasView
from views.inventario import InventarioView
from views.reportes import ReportesView


class Tarjeta(QFrame):
    def __init__(self, titulo, valor):
        super().__init__()
        self.setObjectName("tarjeta")

        layout = QVBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("tituloTarjeta")

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("valorTarjeta")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        self.setLayout(layout)


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Agua Vere - Sistema de Facturación")
        self.setGeometry(100, 100, 1400, 800)

        # 1. Inicializar el contenedor de páginas (QStackedWidget)
        self.paginas = QStackedWidget()

        # =========================
        # MENÚ LATERAL
        # =========================
        menu = QFrame()
        menu.setFixedWidth(250)
        menu.setObjectName("menu")

        layout_menu = QVBoxLayout()

        logo = QLabel("AGUA VERE")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setObjectName("logo")
        layout_menu.addWidget(logo)

        # Definición de los botones de navegación principales con atributos de clase (self.)
        self.btn_dashboard = QPushButton("🏠 Dashboard")
        self.btn_clientes = QPushButton("👥 Clientes")
        self.btn_productos = QPushButton("📦 Productos")
        self.btn_ventas = QPushButton("🧾 Facturación")
        self.btn_inventario = QPushButton("📊 Inventario")

        # Lista para aplicar estilos y configuraciones masivas a los botones activos
        botones_activos = [
            self.btn_dashboard, 
            self.btn_clientes, 
            self.btn_productos, 
            self.btn_ventas, 
            self.btn_inventario
        ]

        for boton in botones_activos:
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setMinimumHeight(45)
            boton.setObjectName("botonMenu")
            layout_menu.addWidget(boton)

        # Botones secundarios estáticos (solo visuales por ahora)
        botones_extras = [
            "🚚 Rutas",
            "💰 Cuentas x Cobrar",
            "📈 Reportes",
            "⚙ Configuración",
            "🚪 Salir"
        ]

        for texto in botones_extras:
            btn_extra = QPushButton(texto)
            btn_extra.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_extra.setMinimumHeight(45)
            btn_extra.setObjectName("botonMenu")
            layout_menu.addWidget(btn_extra)

        layout_menu.addStretch()
        menu.setLayout(layout_menu)

        # =========================
        # PÁGINA 1: DASHBOARD INTERNO (Contenido Principal Original)
        # =========================
        self.dashboard_page = QWidget()
        layout_dashboard_interno = QVBoxLayout()

        # Barra superior de la vista del Dashboard
        barra = QFrame()
        barra.setFixedHeight(70)
        barra.setObjectName("barraSuperior")

        layout_barra = QHBoxLayout()
        titulo = QLabel("Dashboard")
        titulo.setObjectName("tituloPrincipal")
        usuario = QLabel("Usuario: Administrador")
        usuario.setObjectName("usuario")

        layout_barra.addWidget(titulo)
        layout_barra.addStretch()
        layout_barra.addWidget(usuario)
        barra.setLayout(layout_barra)

        # Tarjetas estadísticas
        grid = QGridLayout()
        tarjeta1 = Tarjeta("Ventas Hoy", "RD$ 0.00")
        tarjeta2 = Tarjeta("Facturas Hoy", "0")
        tarjeta3 = Tarjeta("Clientes", "0")
        tarjeta4 = Tarjeta("Botellones Pendientes", "0")

        grid.addWidget(tarjeta1, 0, 0)
        grid.addWidget(tarjeta2, 0, 1)
        grid.addWidget(tarjeta3, 1, 0)
        grid.addWidget(tarjeta4, 1, 1)

        # Área de gráficos futuros
        grafico = QFrame()
        grafico.setObjectName("grafico")
        grafico_layout = QVBoxLayout()
        texto_grafico = QLabel("GRÁFICO DE VENTAS")
        texto_grafico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        texto_grafico.setObjectName("textoGrafico")
        grafico_layout.addWidget(texto_grafico)
        grafico.setLayout(grafico_layout)

        # Unir componentes a la página interna del Dashboard
        layout_dashboard_interno.addWidget(barra)
        layout_dashboard_interno.addLayout(grid)
        layout_dashboard_interno.addWidget(grafico)
        self.dashboard_page.setLayout(layout_dashboard_interno)

        # =========================
        # INTEGRACIÓN DE PÁGINAS AL STACKEDWIDGET
        # =========================
        self.clientes_page = ClientesView()
        self.productos_page = ProductosView()
        self.ventas_page = VentasView()
        self.inventario_page = InventarioView()

        self.paginas.addWidget(self.dashboard_page)  # Índice 0
        self.paginas.addWidget(self.clientes_page)   # Índice 1
        self.paginas.addWidget(self.productos_page)  # Índice 2
        self.paginas.addWidget(self.ventas_page)     # Índice 3
        self.paginas.addWidget(self.inventario_page) # Índice 4

        # =========================
        # CONEXIONES DE NAVEGACIÓN
        # =========================
        self.btn_dashboard.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
        self.btn_clientes.clicked.connect(lambda: self.paginas.setCurrentIndex(1))
        self.btn_productos.clicked.connect(lambda: self.paginas.setCurrentIndex(2))
        self.btn_ventas.clicked.connect(lambda: self.paginas.setCurrentIndex(3))
        self.btn_inventario.clicked.connect(lambda: self.paginas.setCurrentIndex(4))

        # =========================
        # ARMADO DE LA ESTRUCTURA PRINCIPAL
        # =========================
        principal = QWidget()
        self.setCentralWidget(principal)
        layout_principal = QHBoxLayout()

        # El menú va a la izquierda, y el QStackedWidget ocupa todo el espacio derecho móvil
        layout_principal.addWidget(menu)
        layout_principal.addWidget(self.paginas)
        
        principal.setLayout(layout_principal)

        # =========================
        # ESTILOS HOC
        # =========================
        self.setStyleSheet("""
            QMainWindow{
                background:#F4F6F9;
            }
            #menu{
                background:#1E293B;
            }
            #logo{
                color:white;
                font-size:28px;
                font-weight:bold;
                padding:20px;
            }
            #botonMenu{
                background:transparent;
                color:white;
                border:none;
                text-align:left;
                padding-left:20px;
                font-size:15px;
            }
            #botonMenu:hover{
                background:#334155;
                border-radius:8px;
            }
            #barraSuperior{
                background:white;
                border-radius:12px;
            }
            #tituloPrincipal{
                font-size:26px;
                font-weight:bold;
            }
            #usuario{
                font-size:14px;
            }
            #tarjeta{
                background:white;
                border-radius:15px;
                min-height:120px;
            }
            #tituloTarjeta{
                color:#64748B;
                font-size:14px;
            }
            #valorTarjeta{
                font-size:28px;
                font-weight:bold;
            }
            #grafico{
                background:white;
                border-radius:15px;
                min-height:350px;
            }
            #textoGrafico{
                font-size:22px;
                font-weight:bold;
            }
        """)