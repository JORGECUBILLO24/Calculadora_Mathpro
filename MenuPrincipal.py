import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate

from Logica_simbolica_inferencial import LogicaSimbolicaTeclado
from Conjuntos import CalculadoraConjuntos
from Funciones import CalculadoraFunciones
from Limites import CalculadoraLimites
from  Matrices import VentanaMatrices  # <-- Nueva clase integrada

class MenuElegante(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú Principal Mathpro")
        self.setGeometry(200, 100, 1200, 700)
        self.setStyleSheet("background-color: #F0F2F5; color: #000000;")

        # Layout principal
        layout_principal = QHBoxLayout()
        layout_principal.setSpacing(0)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # ------------------- COLUMNA IZQUIERDA (MENÚ) -------------------
        layout_menu = QVBoxLayout()
        layout_menu.setSpacing(0)
        layout_menu.setContentsMargins(0, 0, 0, 0)

        botones_info = [
            ("📘 Matemática Básica", ["Logica simbolica y inferencial", "Conjuntos", "Funciones"]),
            ("📗 Cálculo", ["Límites", "Derivadas"]),
            ("📙 Cálculo II", ["Integrales indefinidas", "Integrales definidas"]),
            ("📐 Álgebra Lineal", ["Vectores", "Determinantes", "Matrices",]),
            ("⚙️ Configuración", ["Preferencias", "Temas", "Acerca de"]),
        ]

        for texto, opciones in botones_info:
            boton = self.crear_boton(texto, opciones)
            layout_menu.addWidget(boton)

        layout_principal.addLayout(layout_menu, 2)

        # ------------------- SEPARADOR -------------------
        linea_separadora = QLabel()
        linea_separadora.setFixedWidth(2)
        linea_separadora.setStyleSheet("background-color: #CCCCCC; color: #000000;")
        layout_principal.insertWidget(1, linea_separadora)

        # ------------------- COLUMNA DERECHA (CONTENIDO) -------------------
        self.layout_derecha = QVBoxLayout()
        self.layout_derecha.setContentsMargins(0, 0, 0, 0)

        self.contenido_widget = QWidget()
        self.contenido_layout = QVBoxLayout()
        self.contenido_layout.setContentsMargins(0, 0, 0, 0)
        self.contenido_widget.setLayout(self.contenido_layout)
        self.layout_derecha.addWidget(self.contenido_widget)

        # Etiqueta de fecha y hora
        self.etiqueta_fecha = QLabel()
        self.etiqueta_fecha.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.etiqueta_fecha.setStyleSheet("""
            font-weight: bold; 
            font-size: 18px; 
            color: #000000;
            padding: 10px;
            text-shadow: 1px 1px 2px #AAAAAA;
        """)
        self.layout_derecha.addWidget(self.etiqueta_fecha)

        layout_principal.addLayout(self.layout_derecha, 5)
        self.setLayout(layout_principal)

        # Timer de hora y fecha
        temporizador = QTimer(self)
        temporizador.timeout.connect(self.actualizar_hora)
        temporizador.start(1000)
        self.actualizar_hora()

    # ------------------- Crear botón con menú -------------------
    def crear_boton(self, texto, opciones):
        boton = QPushButton(texto)
        boton.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #00A8CC, stop:1 #007B8A);
                color: white;
                font-weight: bold;
                font-size: 22px;
                padding: 40px;
                border-radius: 0px;
                border: none;
            }
            QPushButton:hover {
                background-color: #00CED1;
            }
            QPushButton::menu-indicator {
                image: none;
            }
        """)
        boton.setCursor(Qt.CursorShape.PointingHandCursor)
        boton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #AAAAAA;
                padding: 5px;
                font-size: 15px;
            }
            QMenu::item {
                color: #000000;
                padding: 8px 25px;
            }
            QMenu::item:selected {
                background-color: #00A8CC;
                color: black;
            }
        """)
        for opcion in opciones:
            action = menu.addAction(opcion)
            if opcion == "Logica simbolica y inferencial":
                action.triggered.connect(self.mostrar_logica)
            elif opcion == "Conjuntos":
                action.triggered.connect(self.mostrar_conjuntos)
            elif opcion == "Funciones":
                action.triggered.connect(self.mostrar_funciones)
            elif opcion == "Límites":
                action.triggered.connect(self.mostrar_limites)
            elif opcion == "Matrices":
                action.triggered.connect(self.mostrar_eliminacion)

        boton.setMenu(menu)
        return boton

    # ------------------- Métodos para mostrar clases -------------------
    def mostrar_logica(self):
        self.limpiar_contenido()
        widget = LogicaSimbolicaTeclado()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contenido_layout.addWidget(widget)

    def mostrar_conjuntos(self):
        self.limpiar_contenido()
        widget = CalculadoraConjuntos()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contenido_layout.addWidget(widget)

    def mostrar_funciones(self):
        self.limpiar_contenido()
        widget = CalculadoraFunciones()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contenido_layout.addWidget(widget)

    def mostrar_limites(self):
        self.limpiar_contenido()
        widget = CalculadoraLimites()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contenido_layout.addWidget(widget)

    def mostrar_eliminacion(self):
        self.limpiar_contenido()
        widget = VentanaMatrices()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contenido_layout.addWidget(widget)

    # ------------------- Limpiar contenido -------------------
    def limpiar_contenido(self):
        for i in reversed(range(self.contenido_layout.count())):
            widget_ant = self.contenido_layout.itemAt(i).widget()
            if widget_ant is not None:
                widget_ant.setParent(None)

    # ------------------- Actualizar hora y fecha -------------------
    def actualizar_hora(self):
        fecha = QDate.currentDate().toString("dddd, dd MMMM yyyy")
        hora = QTime.currentTime().toString("hh:mm:ss AP")
        self.etiqueta_fecha.setText(f"{fecha} | {hora}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MenuElegante()
    ventana.show()
    sys.exit(app.exec())
