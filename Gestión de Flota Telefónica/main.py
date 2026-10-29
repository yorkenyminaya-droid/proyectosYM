import os
import sys
import csv
import re
from pathlib import Path
from datetime import datetime



from PySide6.QtCore import Qt, QRectF, QUrl
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QTextDocument, QImage, QPixmap
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QMessageBox, QHeaderView,
    QTextEdit, QStackedWidget, QFrame, QGridLayout, QScrollArea,
    QSizePolicy, QFileDialog,
)

from sqlalchemy import (
    create_engine, String, Integer, DateTime, ForeignKey,
    select, or_,
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
    serial: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    imei: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    numero: Mapped[str] = mapped_column(String(30), default="", nullable=False)
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
    cedula: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), default="", nullable=False)


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


class TarjetaSIM(Base):
    __tablename__ = "tarjetas_sim"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    iccid: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    operador: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default="Disponible", nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class AsignacionSIM(Base):
    __tablename__ = "asignaciones_sim"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sim_id: Mapped[int] = mapped_column(ForeignKey("tarjetas_sim.id"), nullable=False)
    telefono_id: Mapped[int] = mapped_column(ForeignKey("telefonos.id"), nullable=False)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"), nullable=False)
    fecha_entrega: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    fecha_devolucion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="Activa", nullable=False)
    observaciones: Mapped[str] = mapped_column(String(500), default="", nullable=False)


# Crea solo las tablas que no existan. No borra los datos existentes.
Base.metadata.create_all(engine)


# =========================================================
# UTILIDADES
# =========================================================

AZUL = "#183C86"
VERDE = "#629534"
DORADO = "#BDA839"
FONDO = "#F5F6F2"


def mostrar_error(parent, titulo, error):
    QMessageBox.critical(parent, titulo, str(error))


def normalizar_texto(valor):
    """Ignora mayúsculas y espacios al comparar identificadores."""
    return "".join(str(valor or "").split()).casefold()


def normalizar_numero(valor):
    """Compara números telefónicos usando solamente sus dígitos."""
    return re.sub(r"\D", "", str(valor or ""))


def asignacion_no_cerrada():
    """
    Considera pendiente una asignación si está marcada como Activa
    o si todavía no tiene fecha de devolución.
    """
    return or_(
        Asignacion.estado == "Activa",
        Asignacion.fecha_devolucion.is_(None),
    )


def crear_tabla(encabezados):
    tabla = QTableWidget()
    tabla.setColumnCount(len(encabezados))
    tabla.setHorizontalHeaderLabels(encabezados)
    tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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

    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            item = QTableWidgetItem(
                "" if valor is None else str(valor)
            )
            if j == 0:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabla.setItem(i, j, item)

    tabla.setUpdatesEnabled(True)


def confirmar_salida(parent, mensaje):
    return QMessageBox.question(
        parent,
        "Confirmar operación",
        mensaje,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    ) == QMessageBox.StandardButton.Yes


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

        for clave, etiqueta in [
            ("marca", "Marca"),
            ("modelo", "Modelo"),
            ("serial", "Número de serie"),
            ("imei", "IMEI"),
            ("color", "Color"),
            ("numero", "Número telefónico"),
        ]:
            campo = QLineEdit()
            campo.setClearButtonEnabled(True)
            self.campos[clave] = campo
            formulario.addRow(etiqueta + ":", campo)

        self.estado = QComboBox()
        self.estado.addItems([
            "Disponible", "En reparación", "Perdido",
            "Robado", "Dado de baja",
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

        obligatorios = ["marca", "modelo", "serial", "imei", "color"]
        if not all(datos[campo] for campo in obligatorios):
            QMessageBox.warning(
                self, "Datos incompletos",
                "Completa marca, modelo, serial, IMEI y color.",
            )
            return

        if len(datos["imei"]) < 8 or not datos["imei"].isdigit():
            QMessageBox.warning(
                self, "IMEI no válido",
                "El IMEI debe contener al menos 8 dígitos.",
            )
            return

        numero = datos["numero"]
        if numero and not re.fullmatch(r"\+?[\d\s()\-]+", numero):
            QMessageBox.warning(
                self, "Número no válido",
                "Introduce un número telefónico válido.",
            )
            return

        if numero and not normalizar_numero(numero):
            QMessageBox.warning(
                self, "Número no válido",
                "El número telefónico debe contener dígitos.",
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

        for clave, etiqueta in [
            ("nombre", "Nombre y apellido"),
            ("cedula", "Cédula"),
            ("cargo", "Cargo"),
            ("departamento", "Departamento"),
            ("correo", "Correo electrónico"),
        ]:
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
        obligatorios = ["nombre", "cedula", "cargo", "departamento"]

        if not all(datos[campo] for campo in obligatorios):
            QMessageBox.warning(
                self, "Datos incompletos",
                "Completa nombre, cédula, cargo y departamento.",
            )
            return

        correo = datos["correo"]
        if correo and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            QMessageBox.warning(
                self, "Correo no válido",
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

                telefonos_validos = []
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
                        telefonos_validos.append(telefono)

                empleados = sesion.scalars(
                    select(Empleado).order_by(Empleado.nombre)
                ).all()

                for telefono in telefonos_validos:
                    self.telefono.addItem(
                        f"{telefono.marca} {telefono.modelo} | "
                        f"{telefono.serial} | "
                        f"{telefono.numero or 'Sin número'}",
                        telefono.id,
                    )

                for empleado in empleados:
                    self.empleado.addItem(
                        f"{empleado.nombre} | Cédula: {empleado.cedula}",
                        empleado.id,
                    )

        except SQLAlchemyError as error:
            mostrar_error(self, "Error al cargar los datos", error)

        formulario.addRow("Teléfono disponible:", self.telefono)
        formulario.addRow("Empleado:", self.empleado)
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
                self, "Sin teléfonos disponibles",
                "No hay teléfonos disponibles sin asignaciones pendientes. "
                "Revisa el inventario o registra un teléfono disponible.",
            )
            return

        if self.empleado.count() == 0:
            QMessageBox.warning(
                self, "Sin empleados",
                "Primero registra al menos un empleado.",
            )
            return

        if self.telefono.currentData() is None or self.empleado.currentData() is None:
            QMessageBox.warning(
                self, "Selección incompleta",
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
# FORMULARIOS DE TARJETAS SIM
# =========================================================

class FormularioSIM(QDialog):
    def __init__(self, parent=None, sim=None):
        super().__init__(parent)
        self.sim_original = sim
        self.setWindowTitle("Editar tarjeta SIM" if sim else "Registrar tarjeta SIM física")
        self.setMinimumWidth(440)
        self.setModal(True)
        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        formulario.setSpacing(12)

        self.iccid = QLineEdit()
        self.iccid.setClearButtonEnabled(True)
        self.iccid.setPlaceholderText("Número serial impreso en la SIM")
        self.numero = QLineEdit()
        self.numero.setClearButtonEnabled(True)
        self.numero.setPlaceholderText("Ej. 809-555-1234")
        self.operador = QComboBox()
        self.operador.addItems(["Claro", "Altice"])
        self.estado = QComboBox()
        self.estado.addItems(["Disponible", "Suspendida", "Dañada"])
        if sim is not None:
            self.iccid.setText(sim.iccid)
            self.numero.setText(sim.numero)
            self.operador.setCurrentText(sim.operador)
            if sim.estado not in [self.estado.itemText(i) for i in range(self.estado.count())]:
                self.estado.addItem(sim.estado)
            self.estado.setCurrentText(sim.estado)
            if sim.estado == "Asignada":
                self.estado.setEnabled(False)

        formulario.addRow("ICCID / serial de SIM:", self.iccid)
        formulario.addRow("Número telefónico:", self.numero)
        formulario.addRow("Operador:", self.operador)
        formulario.addRow("Estado inicial:", self.estado)
        layout.addLayout(formulario)

        botones = QHBoxLayout()
        guardar = QPushButton("Guardar cambios" if sim else "Guardar tarjeta SIM")
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
            "iccid": self.iccid.text().strip(),
            "numero": self.numero.text().strip(),
            "operador": self.operador.currentText(),
            "estado": self.estado.currentText(),
        }

    def validar(self):
        datos = self.obtener_datos()
        if not datos["iccid"] or not datos["numero"]:
            QMessageBox.warning(self, "Datos incompletos", "Completa el ICCID y el número telefónico.")
            return
        if not re.fullmatch(r"[A-Za-z0-9]+", datos["iccid"]):
            QMessageBox.warning(self, "ICCID no válido", "El ICCID debe contener únicamente letras y números, sin espacios.")
            return
        if not re.fullmatch(r"\+?[\d\s()\-]+", datos["numero"]) or not normalizar_numero(datos["numero"]):
            QMessageBox.warning(self, "Número no válido", "Introduce un número telefónico válido.")
            return
        self.accept()


class FormularioAsignacionSIM(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asignar tarjeta SIM")
        self.setMinimumWidth(520)
        self.setModal(True)
        layout = QVBoxLayout(self)
        formulario = QFormLayout()
        formulario.setSpacing(12)
        self.sim = QComboBox()
        self.telefono = QComboBox()
        self.empleado = QComboBox()
        self.observaciones = QTextEdit()
        self.observaciones.setMaximumHeight(90)
        self.observaciones.setPlaceholderText("Detalles de la entrega...")
        try:
            with Session(engine) as sesion:
                sims = sesion.scalars(select(TarjetaSIM).where(TarjetaSIM.estado == "Disponible").order_by(TarjetaSIM.operador, TarjetaSIM.numero)).all()
                for sim in sims:
                    pendiente = sesion.scalar(select(AsignacionSIM.id).where(AsignacionSIM.sim_id == sim.id, AsignacionSIM.estado == "Activa", AsignacionSIM.fecha_devolucion.is_(None)).limit(1))
                    if pendiente is None:
                        self.sim.addItem(f"{sim.numero} | {sim.operador} | ICCID: {sim.iccid}", sim.id)
                telefonos = sesion.scalars(select(Telefono).order_by(Telefono.marca, Telefono.modelo)).all()
                for telefono in telefonos:
                    self.telefono.addItem(f"{telefono.marca} {telefono.modelo} | {telefono.serial}", telefono.id)
                empleados = sesion.scalars(select(Empleado).order_by(Empleado.nombre)).all()
                for empleado in empleados:
                    self.empleado.addItem(f"{empleado.nombre} | Cédula: {empleado.cedula}", empleado.id)
        except SQLAlchemyError as error:
            mostrar_error(self, "Error al cargar los datos", error)
        formulario.addRow("SIM disponible:", self.sim)
        formulario.addRow("Teléfono:", self.telefono)
        formulario.addRow("Empleado responsable:", self.empleado)
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
        if self.sim.currentData() is None:
            QMessageBox.warning(self, "Sin SIM disponibles", "Registra una SIM disponible antes de asignarla.")
            return
        if self.telefono.currentData() is None or self.empleado.currentData() is None:
            QMessageBox.warning(self, "Datos incompletos", "Registra al menos un teléfono y un empleado antes de asignar la SIM.")
            return
        self.accept()

    def obtener_datos(self):
        return {
            "sim_id": self.sim.currentData(),
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
                rect, Qt.AlignmentFlag.AlignCenter,
                "No hay teléfonos registrados",
            )
            painter.end()
            return

        diametro = max(90, min(145, rect.height() - 24))
        circulo = QRectF(
            15, (rect.height() - diametro) / 2, diametro, diametro
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
                x_leyenda + 22, y + 2,
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
                font-size: 18pt;
                font-weight: bold;
                padding: 8px;
            }
            QLabel#submarca {
                color: #E0E7F5;
                font-size: 9pt;
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
                font-size: 23pt;
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
            QScrollArea QWidget {
                background-color: transparent;
            }
        """)

        raiz = QWidget()
        raiz.setObjectName("raiz")
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

        # LOGO ENCIMA DE FLOTACORP
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setMinimumHeight(150)

        # Guarda el archivo del logo como "logo.png" junto a main.py.
        ruta_logo = Path(__file__).resolve().parent / "logo_2.png"
        pixmap = QPixmap(str(ruta_logo))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    350, 300,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            # No interrumpe la aplicación si todavía no se ha colocado el logo.
            logo.setVisible(False)

        menu.addWidget(logo)

        marca = QLabel("◈  FLOTACORP")
        marca.setObjectName("marca")
        marca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu.addWidget(marca)

        submarca = QLabel("GESTIÓN DE DISPOSITIVOS")
        submarca.setObjectName("submarca")
        menu.addWidget(submarca)
        menu.addSpacing(25)

        self.botones_nav = {}
        opciones = [
            ("Inicio", "⌂"),
            ("Teléfonos", "▣"),
            ("Empleados", "♙"),
            ("Asignaciones", "⇄"),
            ("Tarjetas SIM", "▤"),
            ("Formulario de salida", "✍"),
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

        pie_menu = QLabel("SISTEMA DE INVENTARIO\nVersión 2.1\n© 2026 Yorkeny de Jesús Minaya. Todos los derechos reservados.")
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
        self.pagina_sim = self.crear_pagina_sim()
        self.pagina_salida = self.crear_pagina_salida()

        for pagina in [
            self.pagina_inicio,
            self.pagina_telefonos,
            self.pagina_empleados,
            self.pagina_asignaciones,
            self.pagina_sim,
            self.pagina_salida,
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
        etiqueta.setStyleSheet("font-weight: bold; font-size: 11pt;")
        return etiqueta

    def crear_pagina_con_scroll(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        pagina = QWidget()
        pagina.setObjectName("contenido_pagina")
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(14)

        scroll.setWidget(pagina)
        return scroll, layout

    # -----------------------------------------------------
    # INICIO
    # -----------------------------------------------------

    def crear_pagina_inicio(self):
        scroll, layout = self.crear_pagina_con_scroll()
        layout.addWidget(self.crear_titulo_seccion("Indicadores de la flota"))

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
            tarjeta, numero, detalle = self.crear_tarjeta(nombre, color)
            tarjetas.addWidget(tarjeta, i // 3, i % 3)
            self.indicadores[nombre] = (numero, detalle)

        layout.addLayout(tarjetas)
        layout.addWidget(self.crear_titulo_seccion("Distribución de la flota"))

        tarjeta_grafico = QFrame()
        tarjeta_grafico.setObjectName("tarjeta")
        layout_grafico = QVBoxLayout(tarjeta_grafico)
        layout_grafico.setContentsMargins(12, 8, 12, 8)

        self.grafico_distribucion = GraficoDistribucion()
        layout_grafico.addWidget(self.grafico_distribucion)
        tarjeta_grafico.setMinimumHeight(220)
        tarjeta_grafico.setMaximumHeight(240)
        layout.addWidget(tarjeta_grafico)

        layout.addWidget(self.crear_titulo_seccion("Accesos rápidos"))
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
            titulo.setStyleSheet("font-size: 12pt; font-weight: bold;")
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
        layout.addWidget(self.crear_titulo_seccion("Últimas asignaciones"))

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
        self.buscar_telefono.textChanged.connect(self.cargar_telefonos)

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
            "ID", "Marca", "Modelo", "Serial", "IMEI", "Número", "Estado"
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
        self.buscar_empleado.textChanged.connect(self.cargar_empleados)

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
            "ID", "Nombre", "Cédula", "Cargo", "Departamento", "Correo"
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
            "Fecha entrega", "Devolución", "Estado", "Observaciones"
        ])
        layout.addWidget(self.tabla_asignaciones, 1)
        return pagina

    # -----------------------------------------------------
    # PÁGINA DE TARJETAS SIM
    # -----------------------------------------------------

    def crear_pagina_sim(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        barra = QHBoxLayout()
        self.buscar_sim = QLineEdit()
        self.buscar_sim.setPlaceholderText("Buscar por número, ICCID, operador, teléfono o empleado...")
        self.buscar_sim.setClearButtonEnabled(True)
        self.buscar_sim.textChanged.connect(self.cargar_sims)
        registrar = QPushButton("+ Registrar SIM")
        registrar.setObjectName("primario")
        registrar.setMinimumHeight(44)
        registrar.clicked.connect(self.nueva_sim)
        editar = QPushButton("Editar SIM seleccionada")
        editar.setObjectName("secundario")
        editar.setMinimumHeight(44)
        editar.clicked.connect(self.editar_sim)
        asignar = QPushButton("Asignar SIM")
        asignar.setObjectName("secundario")
        asignar.setMinimumHeight(44)
        asignar.clicked.connect(self.nueva_asignacion_sim)
        devolver = QPushButton("Registrar devolución")
        devolver.setObjectName("secundario")
        devolver.setMinimumHeight(44)
        devolver.clicked.connect(self.devolver_sim)
        exportar = QPushButton("Exportar CSV")
        exportar.setObjectName("secundario")
        exportar.setMinimumHeight(44)
        exportar.clicked.connect(self.exportar_reporte_sim)
        barra.addWidget(self.buscar_sim, 1)
        barra.addWidget(registrar)
        barra.addWidget(editar)
        barra.addWidget(asignar)
        barra.addWidget(devolver)
        barra.addWidget(exportar)
        layout.addLayout(barra)
        self.tabla_sims = crear_tabla([
            "ID", "Número", "ICCID", "Operador", "Estado", "Teléfono", "Empleado", "Entrega"
        ])
        layout.addWidget(self.tabla_sims, 1)
        return pagina

    # -----------------------------------------------------
    # FORMULARIO DE SALIDA / ENTREGA DE EQUIPOS
    # -----------------------------------------------------

    def crear_pagina_salida(self):
        
        scroll, layout = self.crear_pagina_con_scroll()
        layout.addWidget(self.crear_titulo_seccion("Acta de entrega de teléfono y tarjeta SIM"))
        intro = QLabel(
            "Selecciona una asignación activa y escribe los nombres de quien entrega y quien recibe. "
            "Se generará un PDF para imprimir y firmar."
        )
        intro.setWordWrap(True)
        intro.setObjectName("subtitulo")
        layout.addWidget(intro)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        formulario = QFormLayout(tarjeta)
        formulario.setContentsMargins(20, 18, 20, 18)
        formulario.setSpacing(12)

        self.salida_empleado = QComboBox()
        self.salida_telefono = QComboBox()
        self.salida_sim = QComboBox()
        self.salida_recibe = QLineEdit()
        self.salida_recibe.setPlaceholderText("Se completará con el empleado seleccionado")
        self.salida_recibe.setReadOnly(True)
        self.salida_entrega = QLineEdit()
        self.salida_entrega.setPlaceholderText("Nombre completo de quien entrega")
        self.salida_observaciones = QTextEdit()
        self.salida_observaciones.setPlaceholderText("Estado de los equipos, accesorios u otras observaciones")
        self.salida_observaciones.setMaximumHeight(95)

        formulario.addRow("Empleado asignado:", self.salida_empleado)
        formulario.addRow("Teléfono asignado:", self.salida_telefono)
        formulario.addRow("Tarjeta SIM asignada:", self.salida_sim)
        formulario.addRow("Nombre de quien recibe:", self.salida_recibe)
        formulario.addRow("Nombre de quien entrega:", self.salida_entrega)
        formulario.addRow("Observaciones:", self.salida_observaciones)
        layout.addWidget(tarjeta)

        botones = QHBoxLayout()
        actualizar = QPushButton("Actualizar asignaciones")
        actualizar.setObjectName("secundario")
        actualizar.clicked.connect(self.cargar_opciones_formulario_salida)
        generar = QPushButton("Generar documento PDF")
        generar.setObjectName("primario")
        generar.setMinimumHeight(46)
        generar.clicked.connect(self.generar_documento_salida)
        botones.addWidget(actualizar)
        botones.addStretch()
        botones.addWidget(generar)
        layout.addLayout(botones)
        layout.addStretch()

        self.salida_empleado.currentIndexChanged.connect(self.actualizar_telefonos_salida)
        self.salida_empleado.currentIndexChanged.connect(self.actualizar_nombre_receptor)
        self.salida_telefono.currentIndexChanged.connect(self.actualizar_sims_salida)

        self.cargar_opciones_formulario_salida()
        self.actualizar_nombre_receptor()
        return scroll

    def actualizar_nombre_receptor(self):
        empleado_id = self.salida_empleado.currentData()

        if not empleado_id:
            self.salida_recibe.clear()
            return

        try:
            with Session(engine) as sesion:
                empleado = sesion.get(Empleado, empleado_id)

            if empleado:
                self.salida_recibe.setText(empleado.nombre)
            else:
                self.salida_recibe.clear()

        except SQLAlchemyError as error:
            mostrar_error(
            self,
            "No se pudo cargar el nombre del receptor",
            error
        )

    def cargar_opciones_formulario_salida(self):
        try:
            with Session(engine) as sesion:
                asignaciones = sesion.scalars(
                    select(Asignacion).where(
                        Asignacion.estado == "Activa",
                        Asignacion.fecha_devolucion.is_(None),
                    ).order_by(Asignacion.id.desc())
                ).all()
                empleados_ids = []
                for a in asignaciones:
                    if a.empleado_id not in empleados_ids:
                        empleados_ids.append(a.empleado_id)
                datos_empleados = []
                for empleado_id in empleados_ids:
                    empleado = sesion.get(Empleado, empleado_id)
                    if empleado:
                        datos_empleados.append((empleado.id, f"{empleado.nombre} — {empleado.cedula}"))

            self.salida_empleado.blockSignals(True)
            anterior = self.salida_empleado.currentData()
            self.salida_empleado.clear()
            for empleado_id, etiqueta in datos_empleados:
                self.salida_empleado.addItem(etiqueta, empleado_id)
            idx = self.salida_empleado.findData(anterior)
            if idx >= 0:
                self.salida_empleado.setCurrentIndex(idx)
            self.salida_empleado.blockSignals(False)
            self.actualizar_telefonos_salida()
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudieron cargar las asignaciones", error)

    def actualizar_telefonos_salida(self, *args):
        if not hasattr(self, "salida_telefono"):
            return
        empleado_id = self.salida_empleado.currentData()
        try:
            with Session(engine) as sesion:
                filas = []
                if empleado_id is not None:
                    asignaciones = sesion.scalars(select(Asignacion).where(
                        Asignacion.empleado_id == int(empleado_id),
                        Asignacion.estado == "Activa",
                        Asignacion.fecha_devolucion.is_(None),
                    ).order_by(Asignacion.id.desc())).all()
                    vistos = set()
                    for a in asignaciones:
                        if a.telefono_id in vistos:
                            continue
                        vistos.add(a.telefono_id)
                        t = sesion.get(Telefono, a.telefono_id)
                        if t:
                            filas.append((t.id, f"{t.marca} {t.modelo} — Serial: {t.serial} — IMEI: {t.imei}"))
            self.salida_telefono.blockSignals(True)
            self.salida_telefono.clear()
            for telefono_id, etiqueta in filas:
                self.salida_telefono.addItem(etiqueta, telefono_id)
            self.salida_telefono.blockSignals(False)
            self.actualizar_sims_salida()
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudieron cargar los teléfonos", error)

    def actualizar_sims_salida(self, *args):
        if not hasattr(self, "salida_sim"):
            return
        empleado_id = self.salida_empleado.currentData()
        telefono_id = self.salida_telefono.currentData()
        try:
            with Session(engine) as sesion:
                filas = []
                if empleado_id is not None and telefono_id is not None:
                    asignaciones = sesion.scalars(select(AsignacionSIM).where(
                        AsignacionSIM.empleado_id == int(empleado_id),
                        AsignacionSIM.telefono_id == int(telefono_id),
                        AsignacionSIM.estado == "Activa",
                        AsignacionSIM.fecha_devolucion.is_(None),
                    ).order_by(AsignacionSIM.id.desc())).all()
                    vistos = set()
                    for a in asignaciones:
                        if a.sim_id in vistos:
                            continue
                        vistos.add(a.sim_id)
                        sim = sesion.get(TarjetaSIM, a.sim_id)
                        if sim:
                            filas.append((sim.id, f"{sim.numero} — {sim.operador} — ICCID: {sim.iccid}"))
            self.salida_sim.clear()
            for sim_id, etiqueta in filas:
                self.salida_sim.addItem(etiqueta, sim_id)
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudieron cargar las tarjetas SIM", error)

    
    def generar_documento_salida(self):
        empleado_id = self.salida_empleado.currentData()
        telefono_id = self.salida_telefono.currentData()
        sim_id = self.salida_sim.currentData()
        nombre_entrega = self.salida_entrega.text().strip()

        if not empleado_id:
            QMessageBox.warning(
                self,
                "Empleado no seleccionado",
                "Selecciona un empleado antes de generar el acta."
            )
            return

        if not telefono_id or not sim_id:
            QMessageBox.warning(
                self,
                "Asignación incompleta",
                "Debe existir una asignación activa del teléfono y de la SIM "
                "para el mismo empleado. Verifica las asignaciones o actualiza la lista."
            )
            return

        if not nombre_entrega:
            QMessageBox.warning(
                self,
                "Falta el nombre",
                "Escribe el nombre de quien entrega."
            )
            return

        try:
            with Session(engine) as sesion:
                empleado = sesion.get(Empleado, int(empleado_id))
                telefono = sesion.get(Telefono, int(telefono_id))
                sim = sesion.get(TarjetaSIM, int(sim_id))

                if not all([empleado, telefono, sim]):
                    QMessageBox.warning(
                        self,
                        "Datos no disponibles",
                        "No se encontraron todos los registros seleccionados."
                    )
                    return

                # El receptor siempre será el empleado seleccionado.
                nombre_recibe = empleado.nombre.strip()

                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                observaciones = (
                    self.salida_observaciones.toPlainText().strip()
                    or "Sin observaciones."
                )

                import html
                e = html.escape

                contenido = f'''<!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #222;
            font-size: 11pt;
        }}
        .encabezado {{
            width: 100%;
            border: none;
            margin-bottom: 10px;
        }}
        .encabezado td {{
            border: none;
            vertical-align: middle;
        }}
        .logo {{
            width: 400px !important;
            height:  auto !important;
            max-width: 400px !important;
}}
        .titulo {{
            text-align: center;
            color: #183C86;
            font-size: 16pt;
            font-weight: bold;
        }}
        h2 {{
            color: #183C86;
            border-bottom: 1px solid #bbb;
            font-size: 13pt;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        td, th {{
            border: 1px solid #bbb;
            padding: 7px;
            text-align: left;
        }}
        th {{
            background: #eef1f7;
        }}
        .firma {{
            width: 55%;
            text-align: center;
            padding-top: 55px;
        }}
        .linea {{
            border-top: 1px solid #333;
            padding-top: 8px;
        }}
        .pie {{
            text-align: center;
            color: #666;
            font-size: 9pt;
        }}
    </style>
    </head>
    <body>
    <table class="encabezado">
        <tr>
            <td style="text-align:center;">
                <img src="logo_embebido" class="logo" width="400" style="width:4000px; height:auto;">
            </td>
        </tr>
        <tr>
            <td class="titulo">ACTA DE ENTREGA DE EQUIPOS</td>
        </tr>
    </table>

    <p><b>Fecha de entrega del documento:</b> {e(fecha)}</p>
    <p>Por medio del presente documento se deja constancia de la entrega
    de los equipos y servicios detallados a continuación.</p>

    <h2>1. Datos del empleado</h2>
    <table>
        <tr><th>Nombre</th><td>{e(empleado.nombre)}</td></tr>
        <tr><th>Cédula / identificación</th><td>{e(empleado.cedula)}</td></tr>
        <tr><th>Cargo</th><td>{e(empleado.cargo)}</td></tr>
        <tr><th>Departamento</th><td>{e(empleado.departamento)}</td></tr>
        <tr><th>Correo</th><td>{e(empleado.correo or '—')}</td></tr>
    </table>

    <h2>2. Equipos entregados</h2>
    <table>
        <tr><th>Tipo</th><th>Detalle</th></tr>
        <tr>
            <td>Teléfono</td>
            <td>
                Marca: {e(telefono.marca)}<br>
                Modelo: {e(telefono.modelo)}<br>
                Serial: {e(telefono.serial)}<br>
                IMEI: {e(telefono.imei)}<br>
                Número: {e(telefono.numero or '—')}
            </td>
        </tr>
        <tr>
            <td>Tarjeta SIM física</td>
            <td>
                Número: {e(sim.numero)}<br>
                Operador: {e(sim.operador)}<br>
                ICCID: {e(sim.iccid)}
            </td>
        </tr>
    </table>

    <h2>3. Observaciones</h2>
    <p>{e(observaciones).replace(chr(10), '<br>')}</p>

    <p>La persona que recibe declara haber recibido los equipos indicados
    y se compromete a utilizarlos y conservarlos conforme a las políticas
    aplicables de la organización.</p>

    <table style="border:none; margin-top:30px;">
        <tr>
            <td class="firma" style="border:none;">
                <div class="linea">{e(nombre_recibe)}<br><b>RECIBE</b></div>
            </td>
            <td style="border:none; width:10%;"></td>
            <td class="firma" style="border:none;">
                <div class="linea">{e(nombre_entrega)}<br><b>ENTREGA</b></div>
            </td>
        </tr>
    </table>

    <p class="pie">Documento generado por Gestión de Flota Telefónica</p>
    </body>
    </html>'''

            sugerido = (
                f"Acta_entrega_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            )
            ruta, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar acta de entrega",
                sugerido,
                "Documento PDF (*.pdf)"
            )

            if not ruta:
                return

            if not ruta.lower().endswith(".pdf"):
                ruta += ".pdf"

            impresora = QPrinter(
                QPrinter.PrinterMode.HighResolution
            )
            impresora.setOutputFormat(
                QPrinter.OutputFormat.PdfFormat
            )
            impresora.setOutputFileName(ruta)

            documento = QTextDocument()

            # Buscar el logo junto a main.py o en la carpeta de datos.
            logo_path = Path(__file__).resolve().parent / "logo.png"

            if not logo_path.exists():
                logo_path = APP_DIR / "logo.png"

            if logo_path.exists():
                logo = QImage(str(logo_path))

                if not logo.isNull():
                    documento.addResource(
                        QTextDocument.ResourceType.ImageResource,
                        QUrl("logo_embebido"),
                        logo
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Logo inválido",
                        "No se pudo cargar logo.png. El PDF se generará sin logo."
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Logo no encontrado",
                    "No se encontró logo.png. Colócalo junto a main.py "
                    "para incluirlo en el PDF."
                )

            documento.setHtml(contenido)
            documento.setDocumentMargin(48)
            documento.print_(impresora)

            QMessageBox.information(
                self,
                "Documento generado",
                f"El acta de entrega se guardó correctamente en:\n{ruta}"
            )

        except (OSError, SQLAlchemyError, RuntimeError) as error:
            mostrar_error(self, "No se pudo generar el documento", error)


    def cargar_sims(self, *args):
        if not hasattr(self, "tabla_sims"):
            return
        termino = normalizar_texto(self.buscar_sim.text() if hasattr(self, "buscar_sim") else "")
        try:
            with Session(engine) as sesion:
                sims = sesion.scalars(select(TarjetaSIM).order_by(TarjetaSIM.id.desc())).all()
                filas = []
                for sim in sims:
                    asignacion = sesion.scalar(select(AsignacionSIM).where(
                        AsignacionSIM.sim_id == sim.id,
                        AsignacionSIM.estado == "Activa",
                        AsignacionSIM.fecha_devolucion.is_(None),
                    ).order_by(AsignacionSIM.id.desc()).limit(1))
                    telefono = sesion.get(Telefono, asignacion.telefono_id) if asignacion else None
                    empleado = sesion.get(Empleado, asignacion.empleado_id) if asignacion else None
                    nombre_telefono = f"{telefono.marca} {telefono.modelo} ({telefono.serial})" if telefono else "—"
                    nombre_empleado = empleado.nombre if empleado else "—"
                    fecha = asignacion.fecha_entrega.strftime("%d/%m/%Y") if asignacion and asignacion.fecha_entrega else "—"
                    valores_busqueda = normalizar_texto(" ".join([
                        sim.numero, sim.iccid, sim.operador, sim.estado,
                        nombre_telefono, nombre_empleado,
                    ]))
                    if termino and termino not in valores_busqueda:
                        continue
                    filas.append([sim.id, sim.numero, sim.iccid, sim.operador, sim.estado, nombre_telefono, nombre_empleado, fecha])
            poner_filas(self.tabla_sims, filas)
        except SQLAlchemyError as error:
            mostrar_error(self, "Error al cargar tarjetas SIM", error)

    def nueva_sim(self):
        dialogo = FormularioSIM(self)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        datos = dialogo.obtener_datos()
        try:
            with Session(engine) as sesion:
                existentes = sesion.scalars(select(TarjetaSIM)).all()
                iccid_norm = normalizar_texto(datos["iccid"])
                numero_norm = normalizar_numero(datos["numero"])
                for existente in existentes:
                    if normalizar_texto(existente.iccid) == iccid_norm:
                        QMessageBox.warning(self, "ICCID duplicado", "Ya existe una tarjeta SIM con ese ICCID.")
                        return
                    if normalizar_numero(existente.numero) == numero_norm:
                        QMessageBox.warning(self, "Número duplicado", "Ya existe una tarjeta SIM registrada con ese número telefónico.")
                        return
                sesion.add(TarjetaSIM(**datos))
                sesion.commit()
            self.actualizar_todo()
            QMessageBox.information(self, "Registro correcto", "La tarjeta SIM se registró correctamente.")
        except IntegrityError:
            QMessageBox.warning(self, "Registro duplicado", "El ICCID o el número telefónico ya está registrado.")
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudo registrar la SIM", error)

    def editar_sim(self):
        fila = self.tabla_sims.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selecciona una SIM", "Selecciona una tarjeta SIM de la tabla para editarla.")
            return
        try:
            sim_id = int(self.tabla_sims.item(fila, 0).text())
        except (ValueError, TypeError, AttributeError):
            QMessageBox.warning(self, "Selección no válida", "No se pudo identificar la SIM seleccionada.")
            return
        try:
            with Session(engine) as sesion:
                sim = sesion.get(TarjetaSIM, sim_id)
                if sim is None:
                    QMessageBox.warning(self, "SIM no encontrada", "La tarjeta seleccionada ya no existe.")
                    return
                datos_originales = {"iccid": sim.iccid, "numero": sim.numero, "operador": sim.operador, "estado": sim.estado}
            dialogo = FormularioSIM(self, sim=type("SIMEdicion", (), datos_originales)())
            if dialogo.exec() != QDialog.DialogCode.Accepted:
                return
            datos = dialogo.obtener_datos()
            with Session(engine) as sesion:
                sim = sesion.get(TarjetaSIM, sim_id)
                if sim is None:
                    QMessageBox.warning(self, "SIM no encontrada", "La tarjeta seleccionada ya no existe.")
                    return
                otras = sesion.scalars(select(TarjetaSIM).where(TarjetaSIM.id != sim_id)).all()
                for otra in otras:
                    if normalizar_texto(otra.iccid) == normalizar_texto(datos["iccid"]):
                        QMessageBox.warning(self, "ICCID duplicado", "Ya existe otra SIM con ese ICCID.")
                        return
                    if normalizar_numero(otra.numero) == normalizar_numero(datos["numero"]):
                        QMessageBox.warning(self, "Número duplicado", "Ya existe otra SIM con ese número telefónico.")
                        return
                sim.iccid = datos["iccid"]
                sim.numero = datos["numero"]
                sim.operador = datos["operador"]
                # El estado de una SIM asignada se controla con la devolución.
                if sim.estado != "Asignada":
                    sim.estado = datos["estado"]
                sesion.commit()
            self.actualizar_todo()
            QMessageBox.information(self, "Cambios guardados", "La tarjeta SIM se actualizó correctamente.")
        except IntegrityError:
            QMessageBox.warning(self, "Registro duplicado", "El ICCID o el número ya pertenece a otra SIM.")
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudo editar la SIM", error)

    def exportar_reporte_sim(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte de tarjetas SIM",
            str(Path.home() / f"reporte_tarjetas_sim_{datetime.now():%Y%m%d_%H%M%S}.csv"),
            "Archivo CSV (*.csv)",
        )
        if not ruta:
            return
        if not ruta.lower().endswith(".csv"):
            ruta += ".csv"
        encabezados = ["ID SIM", "Número", "ICCID", "Operador", "Estado", "Teléfono", "Serial del teléfono", "Empleado", "Cédula", "Fecha de entrega", "Fecha de devolución", "Observaciones"]
        try:
            with Session(engine) as sesion:
                sims = sesion.scalars(select(TarjetaSIM).order_by(TarjetaSIM.id.asc())).all()
                filas = []
                for sim in sims:
                    asignacion = sesion.scalar(select(AsignacionSIM).where(
                        AsignacionSIM.sim_id == sim.id,
                        AsignacionSIM.estado == "Activa",
                        AsignacionSIM.fecha_devolucion.is_(None),
                    ).order_by(AsignacionSIM.id.desc()).limit(1))
                    if asignacion is None:
                        asignacion = sesion.scalar(select(AsignacionSIM).where(
                            AsignacionSIM.sim_id == sim.id
                        ).order_by(AsignacionSIM.id.desc()).limit(1))
                    telefono = sesion.get(Telefono, asignacion.telefono_id) if asignacion else None
                    empleado = sesion.get(Empleado, asignacion.empleado_id) if asignacion else None
                    filas.append([
                        sim.id, sim.numero, sim.iccid, sim.operador, sim.estado,
                        f"{telefono.marca} {telefono.modelo}" if telefono else "",
                        telefono.serial if telefono else "",
                        empleado.nombre if empleado else "", empleado.cedula if empleado else "",
                        asignacion.fecha_entrega.strftime("%d/%m/%Y %H:%M") if asignacion and asignacion.fecha_entrega else "",
                        asignacion.fecha_devolucion.strftime("%d/%m/%Y %H:%M") if asignacion and asignacion.fecha_devolucion else "",
                        asignacion.observaciones if asignacion else "",
                    ])
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo, delimiter=";")
                escritor.writerow(encabezados)
                escritor.writerows(filas)
            QMessageBox.information(self, "Reporte generado", f"Se exportaron {len(filas)} tarjetas SIM.\n\nArchivo: {ruta}")
        except (OSError, SQLAlchemyError, csv.Error) as error:
            mostrar_error(self, "No se pudo exportar el reporte", error)

    def nueva_asignacion_sim(self):
        dialogo = FormularioAsignacionSIM(self)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        datos = dialogo.obtener_datos()
        try:
            with Session(engine) as sesion:
                sim = sesion.get(TarjetaSIM, datos["sim_id"])
                telefono = sesion.get(Telefono, datos["telefono_id"])
                empleado = sesion.get(Empleado, datos["empleado_id"])
                if not sim or not telefono or not empleado:
                    QMessageBox.warning(self, "Registro no encontrado", "La SIM, el teléfono o el empleado seleccionado ya no existe.")
                    return
                if sim.estado != "Disponible":
                    QMessageBox.warning(self, "SIM no disponible", f"La tarjeta tiene estado «{sim.estado}» y no se puede asignar.")
                    return
                pendiente_sim = sesion.scalar(select(AsignacionSIM.id).where(
                    AsignacionSIM.sim_id == sim.id,
                    AsignacionSIM.estado == "Activa",
                    AsignacionSIM.fecha_devolucion.is_(None),
                ).limit(1))
                if pendiente_sim is not None:
                    QMessageBox.warning(self, "SIM ya asignada", "Esta tarjeta SIM ya tiene una asignación pendiente.")
                    return
                pendiente_telefono = sesion.scalar(select(AsignacionSIM.id).where(
                    AsignacionSIM.telefono_id == telefono.id,
                    AsignacionSIM.estado == "Activa",
                    AsignacionSIM.fecha_devolucion.is_(None),
                ).limit(1))
                if pendiente_telefono is not None:
                    QMessageBox.warning(self, "Teléfono ya tiene SIM", "Este teléfono ya tiene una SIM asignada. Registra su devolución antes de asignarle otra.")
                    return
                sesion.add(AsignacionSIM(
                    sim_id=sim.id,
                    telefono_id=telefono.id,
                    empleado_id=empleado.id,
                    observaciones=datos["observaciones"],
                    estado="Activa",
                    fecha_entrega=datetime.now(),
                    fecha_devolucion=None,
                ))
                sim.estado = "Asignada"
                nombre_empleado = empleado.nombre
                numero_sim = sim.numero
                sesion.commit()
            self.actualizar_todo()
            QMessageBox.information(self, "Asignación correcta", f"La SIM {numero_sim} fue asignada a {nombre_empleado} y vinculada al teléfono seleccionado.")
        except IntegrityError:
            QMessageBox.warning(self, "Asignación duplicada", "No se pudo crear la asignación porque existe un registro duplicado.")
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudo asignar la SIM", error)

    def devolver_sim(self):
        fila = self.tabla_sims.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selecciona una SIM", "Selecciona una tarjeta en la tabla antes de registrar la devolución.")
            return
        item = self.tabla_sims.item(fila, 0)
        try:
            sim_id = int(item.text())
        except (ValueError, TypeError, AttributeError):
            QMessageBox.warning(self, "Selección no válida", "No se pudo identificar la SIM seleccionada.")
            return
        if not confirmar_salida(self, "¿Confirmas la devolución de esta tarjeta SIM?"):
            return
        try:
            with Session(engine) as sesion:
                sim = sesion.get(TarjetaSIM, sim_id)
                if sim is None:
                    QMessageBox.warning(self, "SIM no encontrada", "La tarjeta seleccionada ya no existe.")
                    return
                asignacion = sesion.scalar(select(AsignacionSIM).where(
                    AsignacionSIM.sim_id == sim.id,
                    AsignacionSIM.estado == "Activa",
                    AsignacionSIM.fecha_devolucion.is_(None),
                ).order_by(AsignacionSIM.id.desc()).limit(1))
                if asignacion is None:
                    QMessageBox.information(self, "Sin asignación activa", "La SIM seleccionada no tiene una asignación activa.")
                    return
                asignacion.fecha_devolucion = datetime.now()
                asignacion.estado = "Devuelta"
                sim.estado = "Disponible"
                sesion.commit()
            self.actualizar_todo()
            QMessageBox.information(self, "Devolución correcta", "La devolución de la SIM se registró correctamente. La tarjeta quedó disponible.")
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudo registrar la devolución", error)

# -----------------------------------------------------
    # NAVEGACIÓN
    # -----------------------------------------------------

    def mostrar_pagina(self, nombre):
        paginas = {
            "Inicio": (
                0, "Panel principal",
                "Resumen general de los dispositivos corporativos",
            ),
            "Teléfonos": (
                1, "Inventario de teléfonos",
                "Consulta y administra los dispositivos",
            ),
            "Empleados": (
                2, "Directorio de empleados",
                "Consulta y administra el personal",
            ),
            "Asignaciones": (
                3, "Asignaciones",
                "Control de entregas y devoluciones de teléfonos",
            ),
            "Tarjetas SIM": (
                4, "Tarjetas SIM físicas",
                "Inventario, asignación y devolución de SIM Claro y Altice",
            ),
            "Formulario de salida": (
                5, "Formulario de salida",
                "Genera un acta PDF de entrega de teléfono y tarjeta SIM",
            ),
        }

        if nombre not in paginas:
            return

        indice, titulo, subtitulo = paginas[nombre]
        self.paginas.setCurrentIndex(indice)
        self.titulo_pagina.setText(titulo)
        self.subtitulo_pagina.setText(subtitulo)

        for nombre_boton, boton in self.botones_nav.items():
            boton.setProperty("active", nombre_boton == nombre)
            boton.style().unpolish(boton)
            boton.style().polish(boton)
            boton.update()

        if nombre == "Teléfonos":
            self.cargar_telefonos()
        elif nombre == "Empleados":
            self.cargar_empleados()
        elif nombre == "Asignaciones":
            self.cargar_asignaciones()
        elif nombre == "Tarjetas SIM":
            self.cargar_sims()
        elif nombre == "Formulario de salida":
            self.cargar_opciones_formulario_salida()
        elif nombre == "Inicio":
            self.cargar_inicio()

    # -----------------------------------------------------
    # ACTUALIZACIÓN GENERAL
    # -----------------------------------------------------

    def actualizar_todo(self):
        self.cargar_telefonos()
        self.cargar_empleados()
        self.cargar_asignaciones()
        self.cargar_sims()
        self.cargar_inicio()

    # -----------------------------------------------------
    # DASHBOARD
    # -----------------------------------------------------

    def cargar_inicio(self):
        try:
            with Session(engine) as sesion:
                telefonos = list(sesion.scalars(select(Telefono)).all())
                empleados_total = len(sesion.scalars(select(Empleado)).all())
                total = len(telefonos)

                asignaciones_pendientes = sesion.scalars(
                    select(Asignacion).where(asignacion_no_cerrada())
                ).all()
                telefonos_pendientes = {
                    a.telefono_id for a in asignaciones_pendientes
                }
                asignados = len(telefonos_pendientes)

                disponibles = sum(
                    t.estado == "Disponible" and t.id not in telefonos_pendientes
                    for t in telefonos
                )
                reparacion = sum(
                    t.estado == "En reparación" and t.id not in telefonos_pendientes
                    for t in telefonos
                )
                otros = sum(
                    t.id not in telefonos_pendientes
                    and t.estado not in {
                        "Disponible", "Asignado", "En reparación"
                    }
                    for t in telefonos
                )
                otros += sum(
                    t.estado == "Asignado" and t.id not in telefonos_pendientes
                    for t in telefonos
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
                        porcentaje = valor / total * 100 if total else 0
                        detalle.setText(f"{porcentaje:.0f}% de la flota")

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
                    telefono = sesion.get(Telefono, asignacion.telefono_id)
                    empleado = sesion.get(Empleado, asignacion.empleado_id)
                    filas.append([
                        f"{telefono.marca} {telefono.modelo}" if telefono else "No disponible",
                        telefono.serial if telefono else "",
                        empleado.nombre if empleado else "No disponible",
                        asignacion.fecha_entrega.strftime("%d/%m/%Y")
                        if asignacion.fecha_entrega else "",
                        asignacion.estado,
                    ])

            poner_filas(self.tabla_inicio, filas)

        except SQLAlchemyError as error:
            mostrar_error(self, "Error al actualizar el panel", error)

    # -----------------------------------------------------
    # TELÉFONOS
    # -----------------------------------------------------

    def cargar_telefonos(self, *args):
        if not hasattr(self, "tabla_telefonos"):
            return

        termino = self.buscar_telefono.text().strip().casefold()

        try:
            with Session(engine) as sesion:
                telefonos = list(
                    sesion.scalars(
                        select(Telefono).order_by(Telefono.id.desc())
                    ).all()
                )

            encontrados = [
                t for t in telefonos
                if termino in " ".join([
                    t.marca or "", t.modelo or "", t.serial or "",
                    t.imei or "", t.numero or "", t.color or "", t.estado or "",
                ]).casefold()
            ]

            poner_filas(self.tabla_telefonos, [
                [t.id, t.marca, t.modelo, t.serial, t.imei, t.numero, t.estado]
                for t in encontrados
            ])

        except SQLAlchemyError as error:
            mostrar_error(self, "Error al cargar teléfonos", error)

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
                # Revisar duplicados normalizados, no solo coincidencias exactas.
                existentes = sesion.scalars(select(Telefono)).all()

                for telefono in existentes:
                    if normalizar_texto(telefono.serial) == serial_normalizado:
                        QMessageBox.warning(
                            self, "Serial duplicado",
                            f"El serial «{datos['serial']}» ya está registrado "
                            f"en el teléfono ID {telefono.id}.",
                        )
                        return

                    if normalizar_texto(telefono.imei) == imei_normalizado:
                        QMessageBox.warning(
                            self, "IMEI duplicado",
                            f"El IMEI «{datos['imei']}» ya está registrado "
                            f"en el teléfono ID {telefono.id}.",
                        )
                        return

                    if (
                        numero_normalizado
                        and normalizar_numero(telefono.numero) == numero_normalizado
                    ):
                        QMessageBox.warning(
                            self, "Número telefónico duplicado",
                            f"El número «{datos['numero']}» ya está registrado "
                            f"en el teléfono ID {telefono.id}.",
                        )
                        return

                sesion.add(Telefono(**datos))
                sesion.commit()

            self.actualizar_todo()
            QMessageBox.information(
                self, "Registro correcto",
                "El teléfono se registró correctamente.",
            )

        except IntegrityError:
            QMessageBox.warning(
                self, "Registro duplicado",
                "El serial o IMEI ya existe en la base de datos.",
            )
        except SQLAlchemyError as error:
            mostrar_error(self, "No se pudo registrar el teléfono", error)

    # -----------------------------------------------------
    # EMPLEADOS
    # -----------------------------------------------------

    def cargar_empleados(self, *args):
        if not hasattr(self, "tabla_empleados"):
            return

        termino = self.buscar_empleado.text().strip().casefold()

        try:
            with Session(engine) as sesion:
                empleados = list(
                    sesion.scalars(
                        select(Empleado).order_by(Empleado.nombre)
                    ).all()
                )

            encontrados = [
                e for e in empleados
                if termino in " ".join([
                    e.nombre or "",
                    e.cedula or "",
                    e.cargo or "",
                    e.departamento or "",
                    e.correo or "",
                ]).casefold()
            ]

            poner_filas(self.tabla_empleados, [
                [e.id, e.nombre, e.cedula, e.cargo, e.departamento, e.correo]
                for e in encontrados
            ])

        except SQLAlchemyError as error:
            mostrar_error(self, "Error al cargar empleados", error)

    def nuevo_empleado(self):
        dialogo = FormularioEmpleado(self)

        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return

        datos = dialogo.obtener_datos()
        cedula_normalizada = normalizar_texto(datos["cedula"])

        try:
            with Session(engine) as sesion:
                existentes = sesion.scalars(select(Empleado)).all()

                for empleado in existentes:
                    if normalizar_texto(empleado.cedula) == cedula_normalizada:
                        QMessageBox.warning(
                            self,
                            "Cédula duplicada",
                            f"La cédula «{datos['cedula']}» ya está registrada "
                            f"para {empleado.nombre}.",
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
            mostrar_error(self, "No se pudo registrar el empleado", error)

    # -----------------------------------------------------
    # ASIGNACIONES
    # -----------------------------------------------------

    def cargar_asignaciones(self):
        if not hasattr(self, "tabla_asignaciones"):
            return

        try:
            with Session(engine) as sesion:
                asignaciones = sesion.scalars(
                    select(Asignacion).order_by(Asignacion.id.desc())
                ).all()

                filas = []

                for asignacion in asignaciones:
                    telefono = sesion.get(Telefono, asignacion.telefono_id)
                    empleado = sesion.get(Empleado, asignacion.empleado_id)

                    filas.append([
                        asignacion.id,
                        f"{telefono.marca} {telefono.modelo}"
                        if telefono else "No disponible",
                        telefono.serial if telefono else "",
                        empleado.nombre if empleado else "No disponible",
                        empleado.cedula if empleado else "",
                        asignacion.fecha_entrega.strftime("%d/%m/%Y %H:%M")
                        if asignacion.fecha_entrega else "",
                        asignacion.fecha_devolucion.strftime("%d/%m/%Y %H:%M")
                        if asignacion.fecha_devolucion else "",
                        asignacion.estado,
                        asignacion.observaciones or "",
                    ])

            poner_filas(self.tabla_asignaciones, filas)

        except SQLAlchemyError as error:
            mostrar_error(self, "Error al cargar asignaciones", error)

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

        nombre_empleado = ""

        try:
            with Session(engine) as sesion:
                telefono = sesion.get(Telefono, telefono_id)
                empleado = sesion.get(Empleado, empleado_id)

                if telefono is None or empleado is None:
                    QMessageBox.warning(
                        self,
                        "Registro no encontrado",
                        "El teléfono o el empleado seleccionado ya no existe.",
                    )
                    return

                nombre_empleado = empleado.nombre

                # Un teléfono no puede tener dos asignaciones abiertas.
                asignacion_telefono = sesion.scalar(
                    select(Asignacion).where(
                        Asignacion.telefono_id == telefono_id,
                        asignacion_no_cerrada(),
                    ).limit(1)
                )

                if asignacion_telefono is not None:
                    QMessageBox.warning(
                        self,
                        "Teléfono ya asignado",
                        f"El teléfono {telefono.marca} {telefono.modelo} "
                        f"(serial: {telefono.serial}) ya tiene una asignación "
                        "pendiente de devolución.\n\n"
                        "No se puede asignar nuevamente.",
                    )
                    return

                # Un empleado no puede tener dos teléfonos abiertos.
                asignacion_empleado = sesion.scalar(
                    select(Asignacion).where(
                        Asignacion.empleado_id == empleado_id,
                        asignacion_no_cerrada(),
                    ).limit(1)
                )

                if asignacion_empleado is not None:
                    telefono_actual = sesion.get(
                        Telefono,
                        asignacion_empleado.telefono_id,
                    )

                    detalle_telefono = (
                        f"{telefono_actual.marca} {telefono_actual.modelo} "
                        f"(serial: {telefono_actual.serial})"
                        if telefono_actual
                        else "un teléfono registrado"
                    )

                    QMessageBox.warning(
                        self,
                        "Empleado ya tiene teléfono",
                        f"{empleado.nombre} ya tiene asignado "
                        f"{detalle_telefono}.\n\n"
                        "Debes registrar la devolución de ese teléfono "
                        "antes de asignarle otro.",
                    )
                    return

                if telefono.estado != "Disponible":
                    QMessageBox.warning(
                        self,
                        "Teléfono no disponible",
                        f"El teléfono tiene el estado «{telefono.estado}».\n\n"
                        "Solo se pueden asignar teléfonos disponibles.",
                    )
                    return

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
                f"El teléfono fue asignado correctamente a "
                f"{nombre_empleado}.",
            )

        except IntegrityError:
            QMessageBox.warning(
                self,
                "Asignación duplicada",
                "No se pudo crear la asignación porque existe "
                "un registro duplicado.",
            )

        except SQLAlchemyError as error:
            mostrar_error(
                self,
                "No se pudo registrar la asignación",
                error,
            )

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
                asignacion = sesion.get(Asignacion, asignacion_id)

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

                telefono = sesion.get(Telefono, asignacion.telefono_id)

                if telefono is None:
                    QMessageBox.warning(
                        self,
                        "Teléfono no encontrado",
                        "La asignación no tiene un teléfono válido asociado. "
                        "No se modificó ningún dato.",
                    )
                    return

                otras_pendientes = sesion.scalars(
                    select(Asignacion).where(
                        Asignacion.telefono_id == telefono.id,
                        Asignacion.id != asignacion.id,
                        asignacion_no_cerrada(),
                    )
                ).all()

                if otras_pendientes:
                    QMessageBox.warning(
                        self,
                        "Conflicto de asignaciones",
                        "No se puede completar la devolución porque el "
                        "teléfono tiene otra asignación activa o un registro "
                        "sin cerrar.\n\nEl historial no se modificó.",
                    )
                    return

                asignacion.fecha_devolucion = datetime.now()
                asignacion.estado = "Devuelto"

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
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte de asignaciones",
            str(Path.home() / f"reporte_asignaciones_{datetime.now():%Y%m%d_%H%M%S}.csv"),
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
                    select(Asignacion).order_by(Asignacion.id.asc())
                ).all()

                filas = []
                for asignacion in asignaciones:
                    telefono = sesion.get(Telefono, asignacion.telefono_id)
                    empleado = sesion.get(Empleado, asignacion.empleado_id)

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
                        asignacion.fecha_entrega.strftime("%d/%m/%Y %H:%M")
                        if asignacion.fecha_entrega else "",
                        asignacion.fecha_devolucion.strftime("%d/%m/%Y %H:%M")
                        if asignacion.fecha_devolucion else "",
                        asignacion.estado,
                        asignacion.observaciones or "",
                    ])

            # utf-8-sig permite abrir caracteres acentuados correctamente
            # en programas como Microsoft Excel.
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo, delimiter=";")
                escritor.writerow(encabezados)
                escritor.writerows(filas)

            QMessageBox.information(
                self,
                "Reporte generado",
                f"El reporte se guardó correctamente.\n\n"
                f"Registros exportados: {len(filas)}\n"
                f"Archivo: {ruta}",
            )

        except (OSError, SQLAlchemyError, csv.Error) as error:
            mostrar_error(self, "No se pudo generar el reporte", error)


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
        QMessageBox.critical(None, "Error al iniciar la aplicación", str(error))
        sys.exit(1)

import sys
import traceback

def mostrar_error_detallado(tipo, valor, traza):
    traceback.print_exception(tipo, valor, traza)

sys.excepthook = mostrar_error_detallado
if __name__ == "__main__":
    main()
