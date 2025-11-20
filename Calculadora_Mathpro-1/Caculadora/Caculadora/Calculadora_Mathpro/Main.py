# Main.py
import sys
from PyQt6.QtWidgets import QApplication
from MenuPrincipal import MenuElegante

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MenuElegante()
    ventana.show()
    sys.exit(app.exec())
