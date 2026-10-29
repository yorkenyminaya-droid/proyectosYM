
import sys
from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
)


class VentanaBienvenida(QWidget):
    def __init__(self):
        
        
        super().__init__()

        

        self.setWindowTitle("FLOTACORP")
        self.setFixedSize(700, 460)
        self.setWindowFlags(
            Qt.Window
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
        
        )

        self.setStyleSheet("""
        
            QWidget {
                background-color: #123B75;
                color: white;
                font-family: "Segoe UI", Arial;
                
            }

            QLabel#simbolo {
                font-size: 55px;
                color: white;
            }

            QLabel#marca {
                font-size: 34px;
                font-weight: bold;
                letter-spacing: 5px;
            }

            QLabel#descripcion {
                color: #DCE9FF;
                font-size: 13px;
                letter-spacing: 1px;
            }

            QLabel#mensaje {
                color: #FFFFFF;
                font-size: 15px;
            }

            QLabel#pie {
                color: #B8D0F5;
                font-size: 11px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 8, 35, 24)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(3)

        
        # Logo oficial de FLOTACORP
        ruta_logo = Path(__file__).resolve().parent / "Flotacorp.png"

        simbolo = QLabel()
        simbolo.setAlignment(Qt.AlignCenter)
        simbolo.setFixedHeight(350)
        simbolo.setStyleSheet(
            "background: transparent; border: none;"
            
        )

        if ruta_logo.exists():
            pixmap = QPixmap(str(ruta_logo))
            simbolo.setPixmap(
                pixmap.scaled(
                    350,
                    350,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            simbolo.setText("◈")
            simbolo.setStyleSheet(
                "color: white; font-size: 55px;"
            )


        marca = QLabel("FLOTACORP")
        marca.setObjectName("marca")
        marca.setAlignment(Qt.AlignCenter)

        descripcion = QLabel(
            "GESTIÓN DE FLOTA TELEFÓNICA"
        )
        descripcion.setObjectName("descripcion")
        descripcion.setAlignment(Qt.AlignCenter)

        separador = QLabel("━━━━━━━━━━━━━━━━━━")
        separador.setAlignment(Qt.AlignCenter)
        separador.setStyleSheet("color: #4D8DFF;")

        mensaje = QLabel(
            "Bienvenido al sistema de gestión"
        )
        mensaje.setObjectName("mensaje")
        mensaje.setAlignment(Qt.AlignCenter)

        pie = QLabel("SISTEMA INTERNO")
        pie.setObjectName("pie")
        pie.setAlignment(Qt.AlignCenter)

        layout.addWidget(simbolo)
        layout.addWidget(marca)
        layout.addWidget(descripcion)
        layout.addSpacing(8)
        layout.addWidget(separador)
        layout.addSpacing(8)
        layout.addWidget(mensaje)
        layout.addStretch()
        layout.addWidget(pie)

                # Transición suave de entrada
        self.setWindowOpacity(0.0)

        self.animacion_entrada = QPropertyAnimation(
            self, b"windowOpacity", self
        )
        self.animacion_entrada.setDuration(900)
        self.animacion_entrada.setStartValue(0.0)
        self.animacion_entrada.setEndValue(1.0)
        self.animacion_entrada.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )
        self.animacion_entrada.start()

        # Centrar la ventana en la pantalla
        pantalla = QApplication.primaryScreen()
        if pantalla:
            geometria = pantalla.availableGeometry()
            x = geometria.x() + (
                geometria.width() - self.width()
            ) // 2
            y = geometria.y() + (
                geometria.height() - self.height()
            ) // 2
            self.move(x, y)

        # Mostrar el login después de 5 segundos
        QTimer.singleShot(5000, self.abrir_login)

    def abrir_login(self):
        from login import LoginWindow

        self.login = LoginWindow()
        self.login.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    bienvenida = VentanaBienvenida()
    bienvenida.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
