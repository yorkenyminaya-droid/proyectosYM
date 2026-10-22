import sys

from PySide6.QtWidgets import QApplication

from app.ui.windows.main_window import MainWindow


from app.core.database.create_database import create_database



def run():

    app = QApplication(sys.argv)

    create_database()

    window = MainWindow()

    window.show()

    sys.exit(app.exec())