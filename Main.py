import sys
import os

os.environ["QT_OPENGL"] = "software"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Importamos la clase MainWindow desde tu archivo MenuPrincipal.py
try:
    from MenuPrincipal import MainWindow
except ImportError:
    print("Error: No se encontró el archivo 'MenuPrincipal.py'.")
    print("Asegúrate de que el código del menú esté guardado con ese nombre en esta carpeta.")
    sys.exit(1)

# =============================================================================
#  EJECUCIÓN brutal que lanza la aplicación
# =============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
  
    window = MainWindow()
    window.show()
    

    sys.exit(app.exec())