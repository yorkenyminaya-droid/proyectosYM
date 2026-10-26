import os
import sys
import csv
import re
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QMessageBox, QHeaderView,
    QTextEdit, QStackedWidget, QFrame, QGridLayout, QScrollArea,
    QSizePolicy, QFileDialog,
)

from sqlalchemy import (
    create_engine, String, Integer, DateTime, ForeignKey, select, or_,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# =========================================================
# CONFIGURACIÓN Y BASE DE DATOS
# =========================================================

APP_DIR = Path(
    os.environ.get("LOCALAPPDATA", str(Path.home()))
) / "GestionFlotaTelefonica"

APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "flota.db"

engine = create_engine(
    f"sqlite:///{DB_PATH.as_posix()}",
    connect_args={"timeout": 15},
)


class Base(DeclarativeBase):
    pass


class Telefono(Base):
    __tablename__ = "telefonos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marca: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    serial: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )
    imei: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(
        String(30), default="", nullable=False
    )
    estado: Mapped[str] = mapped_column(
        String(30), default="Disponible", nullable=False
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )


class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    cedula: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(
        String(150), default="", nullable=False
    )


class Asignacion(Base):
    __tablename__ = "asignaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telefono_id: Mapped[int] = mapped_column(
        ForeignKey("telefonos.id"), nullable=False
    )
    empleado_id: Mapped[int] = mapped_column(
        ForeignKey("empleados.id"), nullable=False
    )
    fecha_entrega: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    fecha_devolucion: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    estado: Mapped[str] = mapped_column(
        String(30), default="Activa", nullable=False
    )
    observaciones: Mapped[str] = mapped_column(
        String(500), default="", nullable=False
    )


# Crea solamente las tablas que falten. No borra los datos existentes.
Base.metadata.create_all(engine)


# =========================================================
# CONSTANTES Y UTILIDADES
# =========================================================

AZUL = "#183C86"
VERDE = "#629534"
DORADO = "#BDA839"


def mostrar_error(parent, titulo, error):
    QMessageBox.critical(parent, titulo, str(error))


def normalizar_texto(valor):
    """Ignora mayúsculas y espacios al comparar identificadores."""
    return "".join(str(valor or "").split()).casefold()


def normalizar_numero(valor):
    """Devuelve solamente los dígitos de un número telefónico."""
    return re.sub(r"\D", "", str(valor or ""))


def asignacion_no_cerrada():
    """
    Una asignación se considera pendiente si está activa o no tiene
    fecha de devolución.
    """
    return or_(
        Asignacion.estado == "Activa",
        Asignacion.fecha_devolucion.is_(None),
    )


def crear_tabla(encabezados):
    tabla = QTableWidget()
    tabla.setColumnCount(len(encabezados))
    tabla.setHorizontalHeaderLabels(encabezados)
    tabla.setSelectionBehavior(
        QTableWidget.SelectionBehavior.SelectRows
    )
    tabla.setSelectionMode(
        QTableWidget.SelectionMode.SingleSelection
    )
    tabla.setEditTriggers(
        QTableWidget.EditTrigger.NoEditTriggers
    )
    tabla.setAlternatingRowColors(True)
    tabla.setShowGrid(False)
    tabla.verticalHeader().setVisible(False)
    tabla.verticalHeader().setDefaultSectionSize(36)
    tabla.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch
    )
    tabla.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding,
    )
    return tabla


def poner_filas(tabla, filas):
    tabla.setUpdatesEnabled(False)
    tabla.setRowCount(0)
    tabla.setRowCount(len(filas))

    for indice_fila, fila in enumerate(filas):
        for indice_columna, valor in enumerate(fila):
            item = QTableWidgetItem(
                "" if valor is None else str(valor)
            )

            if indice_columna == 0:
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

            tabla.setItem(indice_fila, indice_columna, item)

    tabla.setUpdatesEnabled(True)


def confirmar_salida(parent, mensaje):
    respuesta = QMessageBox.question(
        parent,
        "Confirmar operación",
        mensaje,
        QMessageBox.StandardButton.Yes
        | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return respuesta == QMessageBox.StandardButton.Yes


# =========================================================
# FORMULARIO DE TELÉFONOS
# =========================================================

class FormularioTelefono(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Registrar teléfono")
        self.setMinimumWidth(440)
        self.setModal(True)

        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        formulario.setSpacing(12)

        self.campos = {}

        campos = [
            ("marca", "Marca"),
            ("modelo", "Modelo"),
            ("serial", "Número de serie"),
            ("imei", "IMEI"),
            ("color", "Color"),
            ("numero", "Número telefónico"),
        ]

        for clave, etiqueta in campos:
            campo = QLineEdit()
            campo.setClearButtonEnabled(True)
            self.campos[clave] = campo
            formulario.addRow(etiqueta + ":", campo)

        self.estado = QComboBox()
        self.estado.addItems([
            "Disponible",
            "En reparación",
            "Perdido",
            "Robado",
            "Dado de baja",
        ])
        formulario.addRow("Estado:", self.estado)
        layout.addLayout(formulario)

        botones = QHBoxLayout()

        guardar = QPushButton("Guardar teléfono")
        guardar.setObjectName("primario")
        guardar.setMinimumHeight(40)

        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("secundario")
        cancelar.setMinimumHeight(40)

        guardar.clicked.connect(self.validar)
        cancelar.clicked.connect(self.reject)

        botones.addWidget(guardar)
        botones.addWidget(cancelar)
        layout.addLayout(botones)

    def obtener_datos(self):
        datos = {
            clave: campo.text().strip()
            for clave, campo in self.campos.items()
        }
        datos["estado"] = self.estado.currentText()
        return datos

    def validar(self):
        datos = self.obtener_datos()

        obligatorios = [
            "marca", "modelo", "serial", "imei", "color"
        ]

        if not all(datos[campo] for campo in obligatorios):
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Completa marca, modelo, serial, IMEI y color.",
            )
            return

        if not datos["imei"].isdigit() or len(datos["imei"]) < 8:
            QMessageBox.warning(
                self,
                "IMEI no válido",
                "El IMEI debe contener al menos 8 dígitos.",
            )
            return

        numero = datos["numero"]

        if numero and not re.fullmatch(r"\+?[\d\s()\-]+", numero):
            QMessageBox.warning(
                self,
                "Número no válido",
                "Introduce un número telefónico válido.",
            )
            return

        if numero and not normalizar_numero(numero):
            QMessageBox.warning(
                self,
                "Número no válido",
                "El número debe contener dígitos.",
            )
            return

        self.accept()


# =========================================================
# FORMULARIO DE EMPLEADOS
# =========================================================

class FormularioEmpleado(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Registrar empleado")
        self.setMinimumWidth(440)
        self.setModal(True)

        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        formulario.setSpacing(12)

        self.campos = {}

        campos = [
            ("nombre", "Nombre y apellido"),
            ("cedula", "Cédula"),
            ("cargo", "Cargo"),
            ("departamento", "Departamento"),
            ("correo", "Correo electrónico"),
        ]

        for clave, etiqueta in campos:
            campo = QLineEdit()
            campo.setClearButtonEnabled(True)
            self.campos[clave] = campo
            formulario.addRow(etiqueta + ":", campo)

        layout.addLayout(formulario)

        botones = QHBoxLayout()

        guardar = QPushButton("Guardar empleado")
        guardar.setObjectName("primario")
        guardar.setMinimumHeight(40)

        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("secundario")
        cancelar.setMinimumHeight(40)

        guardar.clicked.connect(self.validar)
        cancelar.clicked.connect(self.reject)

        botones.addWidget(guardar)
        botones.addWidget(cancelar)
        layout.addLayout(botones)

    def obtener_datos(self):
        return {
            clave: campo.text().strip()
            for clave, campo in self.campos.items()
        }

    def validar(self):
        datos = self.obtener_datos()

        obligatorios = [
            "nombre", "cedula", "cargo", "departamento"
        ]

        if not all(datos[campo] for campo in obligatorios):
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Completa nombre, cédula, cargo y departamento.",
            )
            return

        correo = datos["correo"]

        if correo and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", correo
        ):
            QMessageBox.warning(
                self,
                "Correo no válido",
                "Introduce un correo electrónico válido.",
            )
            return

        self.accept()


# =========================================================
# FORMULARIO DE ASIGNACIÓN
# =========================================================

class FormularioAsignacion(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Asignar teléfono")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        formulario.setSpacing(12)

        self.telefono = QComboBox()
        self.empleado = QComboBox()

        self.observaciones = QTextEdit()
        self.observaciones.setMaximumHeight(100)
        self.observaciones.setPlaceholderText(
            "Detalles adicionales de la entrega..."
        )

        try:
            with Session(engine) as sesion:
                telefonos = sesion.scalars(
                    select(Telefono)
                    .where(Telefono.estado == "Disponible")
                    .order_by(Telefono.marca, Telefono.modelo)
                ).all()

                for telefono in telefonos:
                    pendiente = sesion.scalar(
                        select(Asignacion.id)
                        .where(
                            Asignacion.telefono_id == telefono.id,
                            asignacion_no_cerrada(),
                        )
                        .limit(1)
                    )

                    if pendiente is None:
                        self.telefono.addItem(
                            f"{telefono.marca} {telefono.modelo} | "
                            f"{telefono.serial} | "
                            f"{telefono.numero or 'Sin número'}",
                            telefono.id,
                        )

                empleados = sesion.scalars(
                    select(Empleado).order_by(Empleado.nombre)
                ).all()

                for empleado in empleados:
                    pendiente = sesion.scalar(
                        select(Asignacion.id)
                        .where(
                            Asignacion.empleado_id == empleado.id,
                            asignacion_no_cerrada(),
                        )
                        .limit(1)
                    )

                    if pendiente is None:
                        self.empleado.addItem(
                            f"{empleado.nombre} | "
                            f"Cédula: {empleado.cedula}",
                            empleado.id,
                        )

        except SQLAlchemyError as error:
            mostrar_error(self, "Error al cargar los datos", error)

        formulario.addRow("Teléfono disponible:", self.telefono)
        formulario.addRow("Empleado disponible:", self.empleado)
        formulario.addRow("Observaciones:", self.observaciones)
        layout.addLayout(formulario)

        botones = QHBoxLayout()

        guardar = QPushButton("Confirmar asignación")
        guardar.setObjectName("primario")
        guardar.setMinimumHeight(40)

        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("secundario")
        cancelar.setMinimumHeight(40)

        guardar.clicked.connect(self.validar)
        cancelar.clicked.connect(self.reject)

        botones.addWidget(guardar)
        botones.addWidget(cancelar)
        layout.addLayout(botones)

    def validar(self):
        if self.telefono.count() == 0:
            QMessageBox.warning(
                self,
                "Sin teléfonos disponibles",
                "No hay teléfonos disponibles para asignar. "
                "Revisa el inventario o registra un teléfono disponible.",
            )
            return

        if self.empleado.count() == 0:
            QMessageBox.warning(
                self,
                "Sin empleados disponibles",
                "No hay empleados sin asignaciones pendientes. "
                "Registra primero la devolución del teléfono actual.",
            )
            return

        if (
            self.telefono.currentData() is None
            or self.empleado.currentData() is None
        ):
            QMessageBox.warning(
                self,
                "Selección incompleta",
                "Selecciona un teléfono y un empleado.",
            )
            return

        self.accept()

    def obtener_datos(self):
        return {
            "telefono_id": self.telefono.currentData(),
            "empleado_id": self.empleado.currentData(),
            "observaciones": self.observaciones.toPlainText().strip(),
        }


# =========================================================
# GRÁFICO DE DISTRIBUCIÓN
# =========================================================

class GraficoDistribucion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.datos = []
        self.setMinimumHeight(210)

    def actualizar_datos(self, datos):
        self.datos = [
            (nombre, cantidad, color)
            for nombre, cantidad, color in datos
            if cantidad > 0
        ]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        total = sum(cantidad for _, cantidad, _ in self.datos)

        if total == 0:
            painter.setPen(QPen(QColor("#64748B")))
            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                "No hay teléfonos registrados",
            )
            painter.end()
            return

        diametro = max(90, min(145, rect.height() - 24))
        circulo = QRectF(
            15,
            (rect.height() - diametro) / 2,
            diametro,
            diametro,
        )

        inicio = 90 * 16

        for nombre, cantidad, color in self.datos:
            angulo = round(cantidad / total * 360 * 16)

            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor(color)))
            painter.drawPie(circulo, inicio, -angulo)

            inicio -= angulo

        y = 36
        x_leyenda = diametro + 40

        for nombre, cantidad, color in self.datos:
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor(color)))
            painter.drawEllipse(x_leyenda, y - 9, 12, 12)

            painter.setPen(QPen(QColor("#334155")))
            porcentaje = cantidad / total * 100

            painter.drawText(
                x_leyenda + 22,
                y + 2,
                f"{nombre}: {cantidad} ({porcentaje:.0f}%)",
            )

            y += 31

        painter.end()


# =========================================================
# VENTANA PRINCIPAL
# =========================================================

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestión de Flota Telefónica")
        self.resize(1280, 780)
        self.setMinimumSize(1000, 650)

        self.setStyleSheet("""
            QMainWindow, QWidget#contenido {
                background-color: #F5F6F2;
                color: #183C86;
                font-family: Segoe UI;
                font-size: 10pt;
            }
            QWidget#sidebar {
                background-color: #183C86;
                color: white;
            }
            QLabel#marca {
                color: white;
                font-size: 35pt;
                font-weight: bold;
                padding: 8px;
            }
            QLabel#submarca {
                color: #E0E7F5;
                font-size: 10pt;
                padding-left: 10px;
            }
            QPushButton#nav {
                color: white;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 13px 12px;
                text-align: left;
                font-size: 10pt;
            }
            QPushButton#nav:hover {
                background-color: #31569B;
                color: white;
            }
            QPushButton#nav[active="true"] {
                background-color: #629534;
                color: white;
                font-weight: bold;
            }
            QLabel#titulo {
                font-size: 25pt;
                font-weight: bold;
                color: #183C86;
            }
            QLabel#subtitulo {
                color: #64748B;
                font-size: 10pt;
            }
            QFrame#tarjeta {
                background-color: white;
                border: 1px solid #E0E5D8;
                border-radius: 12px;
            }
            QLabel#numero {
                font-size: 25pt;
                font-weight: bold;
                color: #183C86;
            }
            QLabel#etiqueta {
                color: #64748B;
                font-size: 10pt;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: white;
                border: 1px solid #D5DCCB;
                border-radius: 7px;
                padding: 9px;
                color: #183C86;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #629534;
            }
            QPushButton#primario {
                background-color: #629534;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 15px;
                min-height: 20px;
                font-weight: bold;
            }
            QPushButton#primario:hover {
                background-color: #4F7929;
            }
            QPushButton#secundario {
                background-color: white;
                color: #183C86;
                border: 1px solid #BDA839;
                border-radius: 7px;
                padding: 9px 13px;
                min-height: 20px;
            }
            QPushButton#secundario:hover {
                background-color: #F7F2DC;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #F7F8F4;
                color: #183C86;
                border: 1px solid #E0E5D8;
                border-radius: 8px;
                gridline-color: #E7E9E1;
                selection-background-color: #E5EDD9;
                selection-color: #183C86;
            }
            QHeaderView::section {
                background-color: #183C86;
                color: white;
                border: none;
                padding: 11px 7px;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        raiz = QWidget()
        self.setCentralWidget(raiz)

        principal = QHBoxLayout(raiz)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        # MENÚ LATERAL
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(225)

        menu = QVBoxLayout(self.sidebar)
        menu.setContentsMargins(14, 22, 14, 18)
        menu.setSpacing(7)

        marca = QLabel("SICOF")
        marca.setObjectName("marca")
        menu.addWidget(marca)

        submarca = QLabel("Sistema de Control de Flotas")
        submarca.setObjectName("submarca")
        menu.addWidget(submarca)
        menu.addSpacing(25)

        self.botones_nav = {}

        opciones = [
            ("Inicio", "⌂"),
            ("Teléfonos", "▣"),
            ("SIM", "▣"),
            ("Empleados", "♙"),
            ("Asignaciones", "⇄"),
        ]

        for nombre, icono in opciones:
            boton = QPushButton(f"{icono}    {nombre}")
            boton.setObjectName("nav")
            boton.setProperty("active", nombre == "Inicio")
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.setMinimumHeight(44)
            boton.clicked.connect(
                lambda checked=False, n=nombre: self.mostrar_pagina(n)
            )

            self.botones_nav[nombre] = boton
            menu.addWidget(boton)

        menu.addStretch()

        pie_menu = QLabel(
            "SISTEMA DE INVENTARIO\nVersión 2.1"
        )
        pie_menu.setStyleSheet(
            "color: #D4DFF0; padding: 10px; font-size: 9pt;"
        )
        menu.addWidget(pie_menu)

        principal.addWidget(self.sidebar)

        # ÁREA PRINCIPAL
        area = QWidget()
        area.setObjectName("contenido")

        area_layout = QVBoxLayout(area)
        area_layout.setContentsMargins(26, 22, 26, 22)
        area_layout.setSpacing(16)

        principal.addWidget(area, 1)

        cabecera = QHBoxLayout()
        textos = QVBoxLayout()

        self.titulo_pagina = QLabel("Panel principal")
        self.titulo_pagina.setObjectName("titulo")

        self.subtitulo_pagina = QLabel(
            "Resumen general de los dispositivos corporativos"
        )
        self.subtitulo_pagina.setObjectName("subtitulo")
        self.subtitulo_pagina.setWordWrap(True)

        textos.addWidget(self.titulo_pagina)
        textos.addWidget(self.subtitulo_pagina)

        cabecera.addLayout(textos)
        cabecera.addStretch()

        boton_actualizar = QPushButton("↻  Actualizar")
        boton_actualizar.setObjectName("secundario")
        boton_actualizar.setCursor(Qt.CursorShape.PointingHandCursor)
        boton_actualizar.clicked.connect(self.actualizar_todo)

        cabecera.addWidget(boton_actualizar)
        area_layout.addLayout(cabecera)

        self.paginas = QStackedWidget()
        area_layout.addWidget(self.paginas, 1)

        self.pagina_inicio = self.crear_pagina_inicio()
        self.pagina_telefonos = self.crear_pagina_telefonos()
        self.pagina_empleados = self.crear_pagina_empleados()
        self.pagina_asignaciones = self.crear_pagina_asignaciones()

        for pagina in [
            self.pagina_inicio,
            self.pagina_telefonos,
            self.pagina_empleados,
            self.pagina_asignaciones,
        ]:
            self.paginas.addWidget(pagina)

        self.mostrar_pagina("Inicio")
        self.actualizar_todo()

    # -----------------------------------------------------
    # COMPONENTES VISUALES
    # -----------------------------------------------------

    def crear_tarjeta(self, titulo, color):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setMinimumHeight(112)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("etiqueta")
        etiqueta.setWordWrap(True)

        numero = QLabel("0")
        numero.setObjectName("numero")
        numero.setStyleSheet(f"color: {color};")

        detalle = QLabel("Inventario registrado")
        detalle.setObjectName("etiqueta")
        detalle.setWordWrap(True)

        layout.addWidget(etiqueta)
        layout.addWidget(numero)
        layout.addWidget(detalle)

        return tarjeta, numero, detalle

    def crear_titulo_seccion(self, texto):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("subtitulo")
        etiqueta.setStyleSheet(
            "font-weight: bold; font-size: 11pt;"
        )
        return etiqueta

    def crear_pagina_con_scroll(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(14)

        scroll.setWidget(pagina)
        return scroll, layout

    # -----------------------------------------------------
    # PÁGINA DE INICIO
    # -----------------------------------------------------

    def crear_pagina_inicio(self):
        scroll, layout = self.crear_pagina_con_scroll()

        layout.addWidget(
            self.crear_titulo_seccion("Indicadores de la flota")
        )

        tarjetas = QGridLayout()
        tarjetas.setSpacing(12)

        configuracion = [
            ("Total de teléfonos", AZUL),
            ("Disponibles", VERDE),
            ("Asignados", DORADO),
            ("En reparación", DORADO),
            ("Empleados", AZUL),
        ]

        self.indicadores = {}

        for i, (nombre, color) in enumerate(configuracion):
            tarjeta, numero, detalle = self.crear_tarjeta(
                nombre, color
            )
            tarjetas.addWidget(tarjeta, i // 3, i % 3)
            self.indicadores[nombre] = (numero, detalle)

        layout.addLayout(tarjetas)

        layout.addWidget(
            self.crear_titulo_seccion("Distribución de la flota")
        )

        tarjeta_grafico = QFrame()
        tarjeta_grafico.setObjectName("tarjeta")

        layout_grafico = QVBoxLayout(tarjeta_grafico)
        layout_grafico.setContentsMargins(12, 8, 12, 8)

        self.grafico_distribucion = GraficoDistribucion()
        layout_grafico.addWidget(self.grafico_distribucion)

        tarjeta_grafico.setMinimumHeight(220)
        tarjeta_grafico.setMaximumHeight(240)
        layout.addWidget(tarjeta_grafico)

        layout.addWidget(
            self.crear_titulo_seccion("Accesos rápidos")
        )

        accesos = QHBoxLayout()
        accesos.setSpacing(12)

        for nombre, descripcion in [
            ("Teléfonos", "Consultar inventario"),
            ("Empleados", "Gestionar personal"),
            ("Asignaciones", "Entregas y devoluciones"),
        ]:
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjeta")

            v = QVBoxLayout(tarjeta)
            v.setContentsMargins(12, 10, 12, 10)

            titulo = QLabel(nombre)
            titulo.setStyleSheet(
                "font-size: 12pt; font-weight: bold;"
            )
            v.addWidget(titulo)

            desc = QLabel(descripcion)
            desc.setObjectName("subtitulo")
            desc.setWordWrap(True)
            v.addWidget(desc)

            boton = QPushButton("Abrir sección →")
            boton.setObjectName("primario")
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            boton.clicked.connect(
                lambda checked=False, n=nombre: self.mostrar_pagina(n)
            )
            v.addWidget(boton)

            accesos.addWidget(tarjeta)

        layout.addLayout(accesos)

        layout.addWidget(
            self.crear_titulo_seccion("Últimas asignaciones")
        )

        self.tabla_inicio = crear_tabla([
            "Teléfono", "Serial", "Empleado", "Fecha", "Estado"
        ])
        self.tabla_inicio.setMinimumHeight(160)
        self.tabla_inicio.setMaximumHeight(200)

        layout.addWidget(self.tabla_inicio)
        layout.addStretch()

        return scroll

    # -----------------------------------------------------
    # PÁGINA DE TELÉFONOS
    # -----------------------------------------------------

    def crear_pagina_telefonos(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        barra = QHBoxLayout()

        self.buscar_telefono = QLineEdit()
        self.buscar_telefono.setPlaceholderText(
            "Buscar por marca, modelo, serial, IMEI o número..."
        )
        self.buscar_telefono.setClearButtonEnabled(True)
        self.buscar_telefono.textChanged.connect(
            self.cargar_telefonos
        )

        nuevo = QPushButton("+ Registrar teléfono")
        nuevo.setObjectName("primario")
        nuevo.setMinimumWidth(190)
        nuevo.setMinimumHeight(44)
        nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        nuevo.clicked.connect(self.nuevo_telefono)

        barra.addWidget(self.buscar_telefono, 1)
        barra.addWidget(nuevo)
        layout.addLayout(barra)

        self.tabla_telefonos = crear_tabla([
            "ID", "Marca", "Modelo", "Serial",
            "IMEI", "Número", "Estado",
        ])

        layout.addWidget(self.tabla_telefonos, 1)
        return pagina

    # -----------------------------------------------------
    # PÁGINA DE EMPLEADOS
    # -----------------------------------------------------

    def crear_pagina_empleados(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        barra = QHBoxLayout()

        self.buscar_empleado = QLineEdit()
        self.buscar_empleado.setPlaceholderText(
            "Buscar por nombre, cédula, cargo o departamento..."
        )
        self.buscar_empleado.setClearButtonEnabled(True)
        self.buscar_empleado.textChanged.connect(
            self.cargar_empleados
        )

        nuevo = QPushButton("+ Registrar empleado")
        nuevo.setObjectName("primario")
        nuevo.setMinimumWidth(190)
        nuevo.setMinimumHeight(44)
        nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        nuevo.clicked.connect(self.nuevo_empleado)

        barra.addWidget(self.buscar_empleado, 1)
        barra.addWidget(nuevo)
        layout.addLayout(barra)

        self.tabla_empleados = crear_tabla([
            "ID", "Nombre", "Cédula",
            "Cargo", "Departamento", "Correo",
        ])

        layout.addWidget(self.tabla_empleados, 1)
        return pagina

    # -----------------------------------------------------
    # PÁGINA DE ASIGNACIONES
    # -----------------------------------------------------

    def crear_pagina_asignaciones(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        barra = QHBoxLayout()

        asignar = QPushButton("+ Asignar teléfono")
        asignar.setObjectName("primario")
        asignar.setMinimumHeight(44)
        asignar.setCursor(Qt.CursorShape.PointingHandCursor)
        asignar.clicked.connect(self.nueva_asignacion)

        devolver = QPushButton("Registrar devolución")
        devolver.setObjectName("secundario")
        devolver.setMinimumHeight(44)
        devolver.setCursor(Qt.CursorShape.PointingHandCursor)
        devolver.clicked.connect(self.devolver_telefono)

        reporte = QPushButton("Generar reporte")
        reporte.setObjectName("secundario")
        reporte.setMinimumHeight(44)
        reporte.setCursor(Qt.CursorShape.PointingHandCursor)
        reporte.clicked.connect(self.generar_reporte)

        barra.addWidget(asignar)
        barra.addWidget(devolver)
        barra.addWidget(reporte)
        barra.addStretch()

        layout.addLayout(barra)

        self.tabla_asignaciones = crear_tabla([
            "ID", "Teléfono", "Serial", "Empleado", "Cédula",
            "Fecha entrega", "Devolución", "Estado", "Observaciones",
        ])

        layout.addWidget(self.tabla_asignaciones, 1)
        return pagina

    # -----------------------------------------------------
    # NAVEGACIÓN
    # -----------------------------------------------------

    def mostrar_pagina(self, nombre):
        paginas = {
            "Inicio": (
                0,
                "Panel principal",
                "Resumen general de los dispositivos corporativos",
            ),
            "Teléfonos": (
                1,
                "Inventario de teléfonos",
                "Consulta y administra los dispositivos",
            ),
            "Empleados": (
                2,
                "Directorio de empleados",
                "Consulta y administra el personal",
            ),
            "Asignaciones": (
                3,
                "Asignaciones",
                "Control de entregas y devoluciones",
            ),
        }

        if nombre not in paginas:
            return

        indice, titulo, subtitulo = paginas[nombre]

        self.paginas.setCurrentIndex(indice)
        self.titulo_pagina.setText(titulo)
        self.subtitulo_pagina.setText(subtitulo)

        for nombre_boton, boton in self.botones_nav.items():
            boton.setProperty(
                "active", nombre_boton == nombre
            )
            boton.style().unpolish(boton)
            boton.style().polish(boton)
            boton.update()

        if nombre == "Teléfonos":
            self.cargar_telefonos()
        elif nombre == "Empleados":
            self.cargar_empleados()
        elif nombre == "Asignaciones":
            self.cargar_asignaciones()
        elif nombre == "Inicio":
            self.cargar_inicio()

    # -----------------------------------------------------
    # ACTUALIZACIÓN GENERAL
    # -----------------------------------------------------

    def actualizar_todo(self):
        self.cargar_telefonos()
        self.cargar_empleados()
        self.cargar_asignaciones()
        self.cargar_inicio()

    # -----------------------------------------------------
    # PANEL PRINCIPAL
    # -----------------------------------------------------

    def cargar_inicio(self):
        try:
            with Session(engine) as sesion:
                telefonos = list(
                    sesion.scalars(select(Telefono)).all()
                )
                empleados_total = len(
                    sesion.scalars(select(Empleado)).all()
                )
                total = len(telefonos)

                pendientes = sesion.scalars(
                    select(Asignacion).where(
                        asignacion_no_cerrada()
                    )
                ).all()

                telefonos_pendientes = {
                    asignacion.telefono_id
                    for asignacion in pendientes
                }

                asignados = len(telefonos_pendientes)

                disponibles = sum(
                    telefono.estado == "Disponible"
                    and telefono.id not in telefonos_pendientes
                    for telefono in telefonos
                )

                reparacion = sum(
                    telefono.estado == "En reparación"
                    and telefono.id not in telefonos_pendientes
                    for telefono in telefonos
                )

                otros = sum(
                    telefono.id not in telefonos_pendientes
                    and telefono.estado not in {
                        "Disponible",
                        "Asignado",
                        "En reparación",
                    }
                    for telefono in telefonos
                )

                otros += sum(
                    telefono.estado == "Asignado"
                    and telefono.id not in telefonos_pendientes
                    for telefono in telefonos
                )

                valores = {
                    "Total de teléfonos": total,
                    "Disponibles": disponibles,
                    "Asignados": asignados,
                    "En reparación": reparacion,
                    "Empleados": empleados_total,
                }

                for nombre, valor in valores.items():
                    numero, detalle = self.indicadores[nombre]
                    numero.setText(str(valor))

                    if nombre == "Empleados":
                        detalle.setText("Personal registrado")
                    elif nombre == "Total de teléfonos":
                        detalle.setText("Equipos registrados")
                    else:
                        porcentaje = (
                            valor / total * 100 if total else 0
                        )
                        detalle.setText(
                            f"{porcentaje:.0f}% de la flota"
                        )

                self.grafico_distribucion.actualizar_datos([
                    ("Disponible", disponibles, VERDE),
                    ("Asignado", asignados, AZUL),
                    ("En reparación", reparacion, DORADO),
                    ("Otros estados", otros, "#64748B"),
                ])

                asignaciones = sesion.scalars(
                    select(Asignacion)
                    .order_by(Asignacion.id.desc())
                    .limit(8)
                ).all()

                filas = []

                for asignacion in asignaciones:
                    telefono = sesion.get(
                        Telefono, asignacion.telefono_id
                    )
                    empleado = sesion.get(
                        Empleado, asignacion.empleado_id
                    )

                    filas.append([
                        (
                            f"{telefono.marca} {telefono.modelo}"
                            if telefono else "No disponible"
                        ),
                        telefono.serial if telefono else "",
                        empleado.nombre if empleado else "No disponible",
                        (
                            asignacion.fecha_entrega.strftime("%d/%m/%Y")
                            if asignacion.fecha_entrega else ""
                        ),
                        asignacion.estado,
                    ])

            poner_filas(self.tabla_inicio, filas)

        except SQLAlchemyError as error:
            mostrar_error(
                self, "Error al actualizar el panel", error
            )

    # -----------------------------------------------------
    # TELÉFONOS: CARGAR Y BUSCAR
    # -----------------------------------------------------

    def cargar_telefonos(self, *args):
        if not hasattr(self, "tabla_telefonos"):
            return

        termino = self.buscar_telefono.text().strip().casefold()

        try:
            with Session(engine) as sesion:
                telefonos = list(
                    sesion.scalars(
                        select(Telefono).order_by(
                            Telefono.id.desc()
                        )
                    ).all()
                )

            encontrados = [
                telefono for telefono in telefonos
                if termino in " ".join([
                    telefono.marca or "",
                    telefono.modelo or "",
                    telefono.serial or "",
                    telefono.imei or "",
                    telefono.numero or "",
                    telefono.color or "",
                    telefono.estado or "",
                ]).casefold()
            ]

            poner_filas(self.tabla_telefonos, [
                [
                    telefono.id,
                    telefono.marca,
                    telefono.modelo,
                    telefono.serial,
                    telefono.imei,
                    telefono.numero,
                    telefono.estado,
                ]
                for telefono in encontrados
            ])

        except SQLAlchemyError as error:
            mostrar_error(
                self, "Error al cargar teléfonos", error
            )

    # -----------------------------------------------------
    # TELÉFONOS: REGISTRAR
    # -----------------------------------------------------

    def nuevo_telefono(self):
        dialogo = FormularioTelefono(self)

        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return

        datos = dialogo.obtener_datos()
        serial_normalizado = normalizar_texto(datos["serial"])
        imei_normalizado = normalizar_texto(datos["imei"])
        numero_normalizado = normalizar_numero(datos["numero"])

        try:
            with Session(engine) as sesion:
                existentes = sesion.scalars(
                    select(Telefono)
                ).all()

                for telefono in existentes:
                    if (
                        normalizar_texto(telefono.serial)
                        == serial_normalizado
                    ):
                        QMessageBox.warning(
                            self,
                            "Serial duplicado",
                            f"El serial «{datos['serial']}» ya está "
                            f"registrado en el teléfono ID {telefono.id}.",
                        )
                        return

                    if (
                        normalizar_texto(telefono.imei)
                        == imei_normalizado
                    ):
                        QMessageBox.warning(
                            self,
                            "IMEI duplicado",
                            f"El IMEI «{datos['imei']}» ya está "
                            f"registrado en el teléfono ID {telefono.id}.",
                        )
                        return

                    if (
                        numero_normalizado
                        and normalizar_numero(telefono.numero)
                        == numero_normalizado
                    ):
                        QMessageBox.warning(
                            self,
                            "Número duplicado",
                            f"El número «{datos['numero']}» ya está "
                            f"registrado en el teléfono ID {telefono.id}.",
                        )
                        return

                sesion.add(Telefono(**datos))
                sesion.commit()

            self.actualizar_todo()

            QMessageBox.information(
                self,
                "Registro correcto",
                "El teléfono se registró correctamente.",
            )

        except IntegrityError:
            QMessageBox.warning(
                self,
                "Registro duplicado",
                "El serial o IMEI ya existe en la base de datos.",
            )

        except SQLAlchemyError as error:
            mostrar_error(
                self, "No se pudo registrar el teléfono", error
            )

    # -----------------------------------------------------
    # EMPLEADOS: CARGAR Y BUSCAR
    # -----------------------------------------------------

    def cargar_empleados(self, *args):
        if not hasattr(self, "tabla_empleados"):
            return

        termino = self.buscar_empleado.text().strip().casefold()

        try:
            with Session(engine) as sesion:
                empleados = list(
                    sesion.scalars(
                        select(Empleado).order_by(
                            Empleado.nombre
                        )
                    ).all()
                )

            encontrados = [
                empleado for empleado in empleados
                if termino in " ".join([
                    empleado.nombre or "",
                    empleado.cedula or "",
                    empleado.cargo or "",
                    empleado.departamento or "",
                    empleado.correo or "",
                ]).casefold()
            ]

            poner_filas(self.tabla_empleados, [
                [
                    empleado.id,
                    empleado.nombre,
                    empleado.cedula,
                    empleado.cargo,
                    empleado.departamento,
                    empleado.correo,
                ]
                for empleado in encontrados
            ])

        except SQLAlchemyError as error:
            mostrar_error(
                self, "Error al cargar empleados", error
            )

    # -----------------------------------------------------
    # EMPLEADOS: REGISTRAR
    # -----------------------------------------------------

    def nuevo_empleado(self):
        dialogo = FormularioEmpleado(self)

        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return

        datos = dialogo.obtener_datos()
        cedula_normalizada = normalizar_texto(datos["cedula"])

        try:
            with Session(engine) as sesion:
                existentes = sesion.scalars(
                    select(Empleado)
                ).all()

                for empleado in existentes:
                    if (
                        normalizar_texto(empleado.cedula)
                        == cedula_normalizada
                    ):
                        QMessageBox.warning(
                            self,
                            "Cédula duplicada",
                            f"La cédula «{datos['cedula']}» ya está "
                            f"registrada para {empleado.nombre}.",
                        )
                        return

                sesion.add(Empleado(**datos))
                sesion.commit()

            self.actualizar_todo()

            QMessageBox.information(
                self,
                "Registro correcto",
                "El empleado se registró correctamente.",
            )

        except IntegrityError:
            QMessageBox.warning(
                self,
                "Cédula duplicada",
                "Ya existe un empleado con esa cédula.",
            )

        except SQLAlchemyError as error:
            mostrar_error(
                self, "No se pudo registrar el empleado", error
            )

    # -----------------------------------------------------
    # ASIGNACIONES: CARGAR
    # -----------------------------------------------------

    def cargar_asignaciones(self):
        if not hasattr(self, "tabla_asignaciones"):
            return

        try:
            with Session(engine) as sesion:
                asignaciones = sesion.scalars(
                    select(Asignacion).order_by(
                        Asignacion.id.desc()
                    )
                ).all()

                filas = []

                for asignacion in asignaciones:
                    telefono = sesion.get(
                        Telefono, asignacion.telefono_id
                    )
                    empleado = sesion.get(
                        Empleado, asignacion.empleado_id
                    )

                    filas.append([
                        asignacion.id,
                        (
                            f"{telefono.marca} {telefono.modelo}"
                            if telefono else ""
                        ),
                        telefono.serial if telefono else "",
                        empleado.nombre if empleado else "",
                        empleado.cedula if empleado else "",
                        (
                            asignacion.fecha_entrega.strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            if asignacion.fecha_entrega else ""
                        ),
                        (
                            asignacion.fecha_devolucion.strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            if asignacion.fecha_devolucion else ""
                        ),
                        asignacion.estado,
                        asignacion.observaciones,
                    ])

            poner_filas(self.tabla_asignaciones, filas)

        except SQLAlchemyError as error:
            mostrar_error(
                self, "Error al cargar asignaciones", error
            )

    # -----------------------------------------------------
    # ASIGNACIONES: REGISTRAR
    # -----------------------------------------------------

    def nueva_asignacion(self):
        dialogo = FormularioAsignacion(self)

        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return

        datos = dialogo.obtener_datos()
        telefono_id = datos.get("telefono_id")
        empleado_id = datos.get("empleado_id")

        if telefono_id is None or empleado_id is None:
            QMessageBox.warning(
                self,
                "Selección incompleta",
                "Selecciona un teléfono y un empleado.",
            )
            return

        try:
            with Session(engine) as sesion:
                # Evita asignaciones simultáneas desde varias instancias.
                sesion.connection().exec_driver_sql("BEGIN IMMEDIATE")

                telefono = sesion.get(Telefono, telefono_id)
                empleado = sesion.get(Empleado, empleado_id)

                if telefono is None or empleado is None:
                    QMessageBox.warning(
                        self,
                        "Registro no encontrado",
                        "El teléfono o el empleado seleccionado ya no existe.",
                    )
                    return

                # Evitar dos asignaciones pendientes para el mismo teléfono.
                asignacion_telefono = sesion.scalar(
                    select(Asignacion)
                    .where(
                        Asignacion.telefono_id == telefono_id,
                        asignacion_no_cerrada(),
                    )
                    .limit(1)
                )

                if asignacion_telefono is not None:
                    QMessageBox.warning(
                        self,
                        "Teléfono ya asignado",
                        f"El teléfono {telefono.marca} {telefono.modelo} "
                        f"(serial: {telefono.serial}) ya tiene una "
                        "asignación pendiente de devolución.",
                    )
                    return

                # Evitar que un empleado tenga más de un teléfono pendiente.
                asignacion_empleado = sesion.scalar(
                    select(Asignacion)
                    .where(
                        Asignacion.empleado_id == empleado_id,
                        asignacion_no_cerrada(),
                    )
                    .limit(1)
                )

                if asignacion_empleado is not None:
                    telefono_actual = sesion.get(
                        Telefono,
                        asignacion_empleado.telefono_id,
                    )

                    detalle = (
                        f"{telefono_actual.marca} "
                        f"{telefono_actual.modelo} "
                        f"(serial: {telefono_actual.serial})"
                        if telefono_actual
                        else "otro teléfono"
                    )

                    QMessageBox.warning(
                        self,
                        "Empleado ya tiene teléfono",
                        f"{empleado.nombre} ya tiene asignado {detalle}.\n\n"
                        "Registra primero la devolución antes de asignarle "
                        "otro teléfono.",
                    )
                    return

                # Solo se pueden asignar teléfonos disponibles.
                if telefono.estado != "Disponible":
                    QMessageBox.warning(
                        self,
                        "Teléfono no disponible",
                        f"El teléfono tiene el estado «{telefono.estado}».\n\n"
                        "Solo se pueden asignar teléfonos disponibles.",
                    )
                    return

                nombre_empleado = empleado.nombre

                nueva = Asignacion(
                    telefono_id=telefono_id,
                    empleado_id=empleado_id,
                    observaciones=datos.get("observaciones", ""),
                    estado="Activa",
                    fecha_entrega=datetime.now(),
                    fecha_devolucion=None,
                )

                sesion.add(nueva)
                telefono.estado = "Asignado"
                sesion.commit()

            self.actualizar_todo()

            QMessageBox.information(
                self,
                "Asignación correcta",
                "El teléfono fue asignado correctamente a "
                f"{nombre_empleado}.",
            )

        except SQLAlchemyError as error:
            mostrar_error(
                self,
                "No se pudo registrar la asignación",
                error,
            )

    # -----------------------------------------------------
    # ASIGNACIONES: DEVOLVER TELÉFONO
    # -----------------------------------------------------

    def devolver_telefono(self):
        fila = self.tabla_asignaciones.currentRow()

        if fila < 0:
            QMessageBox.warning(
                self,
                "Selecciona una asignación",
                "Selecciona una asignación en la tabla antes de registrar "
                "la devolución.",
            )
            return

        elemento_id = self.tabla_asignaciones.item(fila, 0)

        if elemento_id is None:
            QMessageBox.warning(
                self,
                "Selección no válida",
                "No se pudo identificar la asignación seleccionada.",
            )
            return

        try:
            asignacion_id = int(elemento_id.text())
        except (ValueError, TypeError):
            QMessageBox.warning(
                self,
                "Selección no válida",
                "El identificador de la asignación no es válido.",
            )
            return

        if not confirmar_salida(
            self,
            "¿Confirmas que el teléfono ha sido devuelto?",
        ):
            return

        try:
            with Session(engine) as sesion:
                sesion.connection().exec_driver_sql("BEGIN IMMEDIATE")

                asignacion = sesion.get(
                    Asignacion, asignacion_id
                )

                if asignacion is None:
                    QMessageBox.warning(
                        self,
                        "Asignación no encontrada",
                        "El registro seleccionado ya no existe. "
                        "Actualiza la tabla e inténtalo de nuevo.",
                    )
                    return

                if (
                    asignacion.estado != "Activa"
                    or asignacion.fecha_devolucion is not None
                ):
                    QMessageBox.warning(
                        self,
                        "Asignación no activa",
                        "Esta asignación ya fue devuelta o su estado es "
                        "inconsistente. No se modificó ningún dato.",
                    )
                    return

                telefono = sesion.get(
                    Telefono, asignacion.telefono_id
                )

                if telefono is None:
                    QMessageBox.warning(
                        self,
                        "Teléfono no encontrado",
                        "La asignación no tiene un teléfono válido asociado. "
                        "No se modificó ningún dato.",
                    )
                    return

                otras_pendientes = sesion.scalars(
                    select(Asignacion)
                    .where(
                        Asignacion.telefono_id == telefono.id,
                        Asignacion.id != asignacion.id,
                        asignacion_no_cerrada(),
                    )
                ).all()

                if otras_pendientes:
                    QMessageBox.warning(
                        self,
                        "Conflicto de asignaciones",
                        "El teléfono tiene otra asignación activa o un "
                        "registro sin cerrar.\n\nEl historial no se modificó.",
                    )
                    return

                asignacion.fecha_devolucion = datetime.now()
                asignacion.estado = "Devuelto"

                # No sobrescribir estados especiales por accidente.
                if telefono.estado == "Asignado":
                    telefono.estado = "Disponible"

                estado_final = telefono.estado
                sesion.commit()

            self.actualizar_todo()

            if estado_final == "Disponible":
                mensaje = (
                    "La devolución se registró correctamente y el teléfono "
                    "quedó disponible."
                )
            else:
                mensaje = (
                    "La devolución se registró correctamente. El estado del "
                    f"teléfono se conservó como «{estado_final}»."
                )

            QMessageBox.information(
                self,
                "Devolución correcta",
                mensaje,
            )

        except SQLAlchemyError as error:
            mostrar_error(
                self,
                "No se pudo registrar la devolución",
                error,
            )

    # -----------------------------------------------------
    # GENERAR REPORTE CSV
    # -----------------------------------------------------

    def generar_reporte(self):
        nombre_archivo = (
            f"reporte_asignaciones_{datetime.now():%Y%m%d_%H%M%S}.csv"
        )

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte de asignaciones",
            str(Path.home() / nombre_archivo),
            "Archivo CSV (*.csv)",
        )

        if not ruta:
            return

        if not ruta.lower().endswith(".csv"):
            ruta += ".csv"

        encabezados = [
            "ID asignación",
            "ID teléfono",
            "Marca",
            "Modelo",
            "Serial",
            "IMEI",
            "Número telefónico",
            "Estado del teléfono",
            "ID empleado",
            "Nombre del empleado",
            "Cédula",
            "Cargo",
            "Departamento",
            "Correo",
            "Fecha de entrega",
            "Fecha de devolución",
            "Estado de asignación",
            "Observaciones",
        ]

        try:
            with Session(engine) as sesion:
                asignaciones = sesion.scalars(
                    select(Asignacion).order_by(
                        Asignacion.id.asc()
                    )
                ).all()

                filas = []

                for asignacion in asignaciones:
                    telefono = sesion.get(
                        Telefono, asignacion.telefono_id
                    )
                    empleado = sesion.get(
                        Empleado, asignacion.empleado_id
                    )

                    filas.append([
                        asignacion.id,
                        telefono.id if telefono else "",
                        telefono.marca if telefono else "",
                        telefono.modelo if telefono else "",
                        telefono.serial if telefono else "",
                        telefono.imei if telefono else "",
                        telefono.numero if telefono else "",
                        telefono.estado if telefono else "",
                        empleado.id if empleado else "",
                        empleado.nombre if empleado else "",
                        empleado.cedula if empleado else "",
                        empleado.cargo if empleado else "",
                        empleado.departamento if empleado else "",
                        empleado.correo if empleado else "",
                        (
                            asignacion.fecha_entrega.strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            if asignacion.fecha_entrega else ""
                        ),
                        (
                            asignacion.fecha_devolucion.strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            if asignacion.fecha_devolucion else ""
                        ),
                        asignacion.estado,
                        asignacion.observaciones or "",
                    ])

            # La codificación utf-8-sig ayuda a Excel con las tildes.
            with open(
                ruta,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as archivo:
                escritor = csv.writer(archivo, delimiter=";")
                escritor.writerow(encabezados)
                escritor.writerows(filas)

            QMessageBox.information(
                self,
                "Reporte generado",
                "El reporte se guardó correctamente.\n\n"
                f"Registros exportados: {len(filas)}\n"
                f"Archivo: {ruta}",
            )

        except (OSError, SQLAlchemyError, csv.Error) as error:
            mostrar_error(
                self,
                "No se pudo generar el reporte",
                error,
            )


# =========================================================
# INICIO DEL PROGRAMA
# =========================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gestión de Flota Telefónica")
    app.setStyle("Fusion")

    try:
        ventana = VentanaPrincipal()
        ventana.show()
        sys.exit(app.exec())

    except Exception as error:
        QMessageBox.critical(
            None,
            "Error al iniciar la aplicación",
            str(error),
        )
        sys.exit(1)


if __name__ == "__main__":
    main()