from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
# Importamos la ventana del Dashboard para poder llamarla
from views.dashboard import Dashboard 

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Agua Vere - Inicio de Sesión")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        titulo = QLabel("AGUA BERE")
        titulo.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuario")

        self.clave = QLineEdit()
        self.clave.setPlaceholderText("Contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)

        boton = QPushButton("Iniciar Sesión")
        boton.clicked.connect(self.iniciar_sesion)

        layout.addWidget(titulo)
        layout.addWidget(self.usuario)
        layout.addWidget(self.clave)
        layout.addWidget(boton)

        self.setLayout(layout)

    def iniciar_sesion(self):
        usuario = self.usuario.text()
        clave = self.clave.text()

        if usuario == "admin" and clave == "1234":
            QMessageBox.information(
                self,
                "Bienvenido",
                "Acceso correcto"
            )
            
            # 1. Creamos la instancia del Dashboard asignándola a self.dashboard
            # (Usar self. es vital para que Python no borre la ventana de la memoria)
            self.dashboard = Dashboard()
            
            # 2. Mostramos el Dashboard
            self.dashboard.show()
            
            # 3. Cerramos la ventana de Login actual
            self.close()
            
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Usuario o contraseña incorrectos"
            )