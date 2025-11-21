# -*- coding: utf-8 -*-
"""
main.py
Punto de entrada principal para la Suite MathPro.
"""
import sys
import os

# =============================================================================
#  CONFIGURACIÓN INICIAL (PARCHE GPU)
#  Es vital definir esto ANTES de importar PyQt6 para tu Lenovo T460s.
# =============================================================================
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
#  EJECUCIÓN
# =============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Opcional: Configurar un icono global para la app si tienes uno
    # app.setWindowIcon(QIcon("icono.png")) 

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())