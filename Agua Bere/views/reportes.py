import sqlite3
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QComboBox, QFileDialog
)
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtCore import Qt


class ReportesView(QWidget):
    def __init__(self):
        super().__init__()
        
        # Conexión a la base de datos
        self.conn = sqlite3.connect("agua_vere.db")
        self.cursor = self.conn.cursor()

        # Layout Principal
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # Título del módulo
        titulo = QLabel("Módulo de Reportes y Estadísticas")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 10px;")
        layout_principal.addWidget(titulo)

        # ==========================================
        # FILTROS DE TIEMPO
        # ==========================================
        layout_filtros = QHBoxLayout()

        lbl_filtro = QLabel("Agrupar Ventas Por:")
        lbl_filtro.setStyleSheet("font-weight: bold;")
        
        self.cb_periodo = QComboBox()
        self.cb_periodo.addItems([
            "Ventas Diarias (Hoy)",
            "Ventas Mensuales (Este Mes)",
            "Ventas Anuales (Este Año)",
            "Historial Histórico Completo"
        ])
        self.cb_periodo.setFixedWidth(250)
        self.cb_periodo.currentIndexChanged.connect(self.cargar_reporte)

        layout_filtros.addWidget(lbl_filtro)
        layout_filtros.addWidget(self.cb_periodo)
        layout_filtros.addStretch()

        # ==========================================
        # BOTONES DE EXPORTACIÓN
        # ==========================================
        self.btn_excel = QPushButton("📊 Exportar a Excel (.CSV)")
        self.btn_excel.setStyleSheet("background-color: #16A34A; color: white; font-weight: bold; padding: 6px 12px;")
        self.btn_excel.clicked.connect(self.exportar_excel)

        self.btn_pdf = QPushButton(" picture_as_pdf Exportar a PDF / Imprimir")
        self.btn_pdf.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold; padding: 6px 12px;")
        self.btn_pdf.clicked.connect(self.exportar_pdf)

        layout_filtros.addWidget(self.btn_excel)
        layout_filtros.addWidget(self.btn_pdf)
        
        layout_principal.addLayout(layout_filtros)

        # ==========================================
        # TABLA DE RESULTADOS
        # ==========================================
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Factura ID", "Fecha / Hora", "Cliente", "Impuesto (ITBIS)", "Total General"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.SectionResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout_principal.addWidget(self.tabla)

        # ==========================================
        # RESUMEN DE TOTALES EN PANTALLA
        # ==========================================
        layout_totales = QHBoxLayout()
        layout_totales.addStretch()
        
        self.lbl_gran_total = QLabel("Total Facturado en Periodo: RD$ 0.00")
        self.lbl_gran_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B; padding: 10px; background: white; border-radius: 8px;")
        layout_totales.addWidget(self.lbl_gran_total)
        
        layout_principal.addLayout(layout_totales)

        # Cargar datos iniciales (Ventas Diarias por defecto)
        self.cargar_reporte()

    # ==========================================
    # LÓGICA DE FILTRADO DE DATOS (SQL)
    # ==========================================

    def cargar_reporte(self):
        """Consulta las facturas guardadas aplicando filtros de fecha dinámicos"""
        filtro = self.cb_periodo.currentText()
        
        # Consultas base usando modificadores de tiempo de SQLite
        if "Diarias" in filtro:
            # Compara solo el año-mes-día actual
            query = "SELECT id, fecha, cliente, itbis, total FROM facturas WHERE date(fecha) = date('now', 'localtime')"
        elif "Mensuales" in filtro:
            # Compara el año y el mes actual (YYYY-MM)
            query = "SELECT id, fecha, cliente, itbis, total FROM facturas WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now', 'localtime')"
        elif "Anuales" in filtro:
            # Compara únicamente el año actual (YYYY)
            query = "SELECT id, fecha, cliente, itbis, total FROM facturas WHERE strftime('%Y', fecha) = strftime('%Y', 'now', 'localtime')"
        else:
            # Todo el historial sin discriminación
            query = "SELECT id, fecha, cliente, itbis, total FROM facturas ORDER BY id DESC"

        try:
            self.cursor.execute(query)
            self.datos_actuales = self.cursor.fetchall()
            self.redibujar_tabla()
        except sqlite3.OperationalError:
            self.datos_actuales = []
            self.tabla.setRowCount(0)
            self.lbl_gran_total.setText("Total Facturado en Periodo: RD$ 0.00")

    def redibujar_tabla(self):
        """Renderiza las filas de facturas y calcula la suma total del periodo"""
        self.tabla.setRowCount(0)
        suma_acumulada = 0.0

        for r_num, row_data in enumerate(self.datos_actuales):
            self.tabla.insertRow(r_num)
            
            # Sumar al total general del reporte
            suma_acumulada += float(row_data[4])

            for c_num, val in enumerate(row_data):
                item = QTableWidgetItem(str(val))
                
                # Alineaciones y formatos de dinero
                if c_num in [0, 1]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c_num in [3, 4]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    item.setText(f"RD$ {float(val):,.2f}")
                
                self.tabla.setItem(r_num, c_num, item)

        self.lbl_gran_total.setText(f"Total Facturado en Periodo: RD$ {suma_acumulada:,.2f}")

    # ==========================================
    # EXPORTACIÓN DE ARCHIVOS
    # ==========================================

    def exportar_excel(self):
        """Exporta los registros cargados en pantalla a un formato CSV nativo para Excel"""
        if not self.datos_actuales:
            QMessageBox.warning(self, "Sin datos", "No hay registros en el periodo seleccionado para exportar.")
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte de Ventas", "", "Archivo de Excel (*.csv)"
        )

        if ruta:
            try:
                with open(ruta, mode='w', newline='', encoding='utf-8-sig') as archivo:
                    escritor = csv.writer(archivo, delimiter=';')
                    # Encabezados del documento
                    escritor.writerow(["Factura ID", "Fecha y Hora", "Cliente", "ITBIS (Impuesto)", "Total Facturado"])
                    
                    # Escribir filas de datos
                    for fila in self.datos_actuales:
                        escritor.writerow([fila[0], fila[1], fila[2], f"{fila[3]:.2f}", f"{fila[4]:.2f}"])
                
                QMessageBox.information(self, "Exportación Exitosa", "El reporte se guardó correctamente para abrir en Excel.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")

    def exportar_pdf(self):
        """Genera una plantilla HTML limpia y levanta el gestor de impresión nativo de PDF"""
        if not self.datos_actuales:
            QMessageBox.warning(self, "Sin datos", "No hay registros disponibles para generar el PDF.")
            return

        # Construcción dinámica del cuerpo del reporte en HTML
        filtro_nombre = self.cb_periodo.currentText()
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                h1 {{ text-align: center; color: #1E293B; }}
                h3 {{ text-align: center; color: #64748B; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background-color: #F1F5F9; color: #1E293B; padding: 10px; border: 1px solid #CBD5E1; text-align: left; }}
                td {{ padding: 10px; border: 1px solid #E2E8F0; }}
                .total {{ text-align: right; font-size: 16px; font-weight: bold; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h1>AGUA VERE</h1>
            <h3>Reporte de {filtro_nombre}</h3>
            <hr>
            <table>
                <tr>
                    <th>Factura ID</th>
                    <th>Fecha / Hora</th>
                    <th>Cliente</th>
                    <th>Total</th>
                </tr>
        """
        
        total_acumulado = 0.0
        for fila in self.datos_actuales:
            total_acumulado += fila[4]
            html += f"""
                <tr>
                    <td>#{fila[0]}</td>
                    <td>{fila[1]}</td>
                    <td>{fila[2]}</td>
                    <td>RD$ {fila[4]:,.2f}</td>
                </tr>
            """
            
        html += f"""
            </table>
            <div class="total">Grand Total Periodo: RD$ {total_acumulado:,.2f}</div>
        </body>
        </html>
        """

        # Crear documento e inyectar el HTML
        documento = QTextDocument()
        documento.setHtml(html)

        # Configurar la impresora lógica del sistema operativo
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        
        # Cuadro de diálogo para que el usuario elija dónde guardar su archivo .pdf
        dialogo = QPrintDialog(printer, self)
        if dialogo.exec() == QPrintDialog.DialogCode.Accepted:
            documento.print_(printer)
            QMessageBox.information(self, "PDF Generado", "El reporte se procesó con éxito.")

    # Refrescar reporte de manera automática al abrir la sección
    def showEvent(self, event):
        self.cargar_reporte()
        super().showEvent(event)