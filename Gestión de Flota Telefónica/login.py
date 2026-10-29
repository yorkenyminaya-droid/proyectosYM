
"""
Login de FLOTACORP
Guarda este archivo como login.py en la misma carpeta que main.py.

Logo: Flotacorp.png (en la misma carpeta).

Usuario inicial: admin
Contraseña inicial: Flota2026*
"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFrame,
    QMessageBox,
)
from PySide6.QtGui import QPixmap



from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtCore import Qt


# Credenciales de acceso
ADMIN_USER = os.environ.get("FLOTACORP_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get(
    "FLOTACORP_ADMIN_PASSWORD", "Flota2026*"
)

# Carpeta donde se encuentran login.py, main.py y el logo
CARPETA_APP = Path(__file__).resolve().parent
RUTA_LOGO = CARPETA_APP / "Flotacorp.png"


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FLOTACORP | Inicio de sesión")
        self.setFixedSize(00, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: #f2f6fc;
                color: #24364b;
                font-family: "Segoe UI", Arial;
                font-size: 14px;
            }

            QFrame#panel {
                background-color: white;
                border: 1px solid #dce5f1;
                border-radius: 18px;
            }

            QLabel#logo {
                background: transparent;
                border: none;
            }

            QLabel.fieldLabel {
                background: transparent;
                color: #34445b;
                font-size: 12px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #fbfcff;
                border: 1px solid #d4deeb;
                border-radius: 9px;
                padding: 12px;
                color: #24364b;
                selection-background-color: #155eef;
            }

            QLineEdit:focus {
                border: 1px solid #155eef;
                background-color: white;
            }

            QPushButton#loginButton {
                background-color: #155eef;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 13px;
                font-weight: bold;
            }

            QPushButton#loginButton:hover {
                background-color: #0d4ed8;
            }

            QPushButton#loginButton:pressed {
                background-color: #0a3eae;
            }

            QLabel#footer {
                background: transparent;
                color: #8997aa;
                font-size: 11px;
            }
        """)

        # Diseño principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 18)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        # Panel del formulario
        panel = QFrame()
        panel.setObjectName("panel")

        form = QVBoxLayout(panel)
        form.setContentsMargins(25, 20, 25, 22)
        form.setSpacing(11)

        # Logo de FLOTACORP
        logo = QLabel()
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedHeight(115)

        pixmap = QPixmap(str(RUTA_LOGO))

        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    245,
                    110,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            logo.setText("FLOTACORP")
            logo.setStyleSheet("""
                QLabel#logo {
                    color: #123b75;
                    font-size: 25px;
                    font-weight: bold;
                }
            """)

        form.addWidget(logo)
        form.addSpacing(5)

        # Usuario
        user_label = QLabel("USUARIO")
        user_label.setProperty("class", "fieldLabel")

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingresa tu usuario")
        self.user_input.setClearButtonEnabled(True)
        self.user_input.setAccessibleName("Usuario")

        # Contraseña
        password_label = QLabel("CONTRASEÑA")
        password_label.setProperty("class", "fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(
            "Ingresa tu contraseña"
        )
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.password_input.setAccessibleName("Contraseña")
        self.password_input.returnPressed.connect(self.login)

        # Botón de inicio de sesión
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.login_button.clicked.connect(self.login)

        # Agregar controles al formulario
        form.addWidget(user_label)
        form.addWidget(self.user_input)
        form.addSpacing(3)
        form.addWidget(password_label)
        form.addWidget(self.password_input)
        form.addSpacing(8)
        form.addWidget(self.login_button)
        form.addSpacing(6)

        footer = QLabel("Acceso autorizado únicamente")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addWidget(footer)

        layout.addWidget(panel)

        # Pie de la ventana
        bottom = QLabel("© 2026 Yorkeny de Jesús Minaya. Todos los derechos reservados.")
        bottom.setObjectName("footer")
        bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)
        layout.addWidget(bottom)

        self.user_input.setFocus()

                # Transición suave de entrada
        self.setWindowOpacity(0.0)

        self.animacion_entrada = QPropertyAnimation(
            self, b"windowOpacity", self
        )
        self.animacion_entrada.setDuration(650)
        self.animacion_entrada.setStartValue(0.0)
        self.animacion_entrada.setEndValue(1.0)
        self.animacion_entrada.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )
        self.animacion_entrada.start()

    
    def login(self):
        usuario = self.user_input.text().strip()
        contraseña = self.password_input.text()

        if (
            usuario != ADMIN_USER
            or contraseña != ADMIN_PASSWORD
        ):
            QMessageBox.warning(
                self,
                "Acceso denegado",
                "El usuario o la contraseña son incorrectos.",
            )
            self.password_input.clear()
            self.password_input.setFocus()
            return

        try:
            from main import VentanaPrincipal

            self.ventana_principal = VentanaPrincipal()
            self.ventana_principal.show()
            self.close()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al iniciar",
                f"No se pudo abrir la ventana principal:\n{error}",
            )

        self.close()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    ventana = LoginWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
