import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate

from Logica_simbolica_inferencial import LogicaSimbolicaTeclado
from Conjuntos import CalculadoraConjuntos
from Funciones import CalculadoraFunciones
from Limites import CalculadoraLimites
from Matrices import VentanaMatrices

class MenuElegante(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú Principal Mathpro")
        self.setGeometry(200, 100, 1200, 700)
        self.tema = "claro"
        self.idioma = "Español"
        self.orientacion_barra = "horizontal"
        self.setStyleSheet("background-color: #F0F2F5; color: #000000;")

        # ------------------- Layout principal -------------------
        self.layout_principal = QVBoxLayout()
        self.layout_principal.setSpacing(0)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_principal)

        # ------------------- Layout de menú -------------------
        self.layout_menu = QVBoxLayout()
        self.layout_menu.setSpacing(5)
        self.layout_menu.setContentsMargins(0, 0, 0, 0)
        self.layout_menu.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.layout_menu)
        self.menu_widget.setFixedWidth(250)

        # ------------------- Botones -------------------
        self.botones_info = [
            ("📘 Matemática Básica", ["Logica simbolica y inferencial", "Conjuntos", "Funciones"]),
            ("📗 Cálculo", ["Límites", "Derivadas"]),
            ("📙 Cálculo II", ["Integrales indefinidas", "Integrales definidas"]),
            ("📐 Álgebra Lineal", ["Vectores", "Determinantes", "Matrices"]),
        ]
        self.botones = []
        for texto, opciones in self.botones_info:
            boton = self.crear_boton(texto, opciones)
            self.botones.append((boton, opciones))
            self.layout_menu.addWidget(boton)

        # Botón configuración
        self.boton_config = QPushButton("⚙️ Configuración")
        self.boton_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_config.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.boton_config.setFixedHeight(50)
        self.estilo_boton_y_menu(self.boton_config, ["Cambiar orientación barra", "Cambiar idioma", "Cambiar tema"])
        self.layout_menu.addWidget(self.boton_config)

        # ------------------- Barra horizontal -------------------
        self.barra_horizontal_widget = QWidget()
        self.barra_horizontal_layout = QHBoxLayout(self.barra_horizontal_widget)
        self.barra_horizontal_layout.setSpacing(0)
        self.barra_horizontal_layout.setContentsMargins(0, 0, 0, 0)

        # ------------------- Contenido -------------------
        self.contenido_widget = QWidget()
        self.contenido_layout = QVBoxLayout(self.contenido_widget)
        self.contenido_layout.setContentsMargins(0, 0, 0, 0)
        self.contenido_layout.setSpacing(0)
        self.contenido_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Etiqueta de fecha y hora
        self.etiqueta_fecha = QLabel()
        self.etiqueta_fecha.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.etiqueta_fecha.setStyleSheet("""
            font-weight: bold; 
            font-size: 18px; 
            color: #000000;
            padding: 10px;
        """)
        self.contenido_layout.addWidget(self.etiqueta_fecha)

        # Timer de hora y fecha
        temporizador = QTimer(self)
        temporizador.timeout.connect(self.actualizar_hora)
        temporizador.start(1000)
        self.actualizar_hora()

        # Aplicar orientación inicial
        self.cambiar_orientacion_barra("horizontal")

    # ------------------- Crear botón con menú -------------------
    def crear_boton(self, texto, opciones):
        boton = QPushButton(texto)
        boton.setCursor(Qt.CursorShape.PointingHandCursor)
        boton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        boton.setFixedHeight(50)
        self.estilo_boton_y_menu(boton, opciones)
        return boton

    # ------------------- Estilo botón + reconstrucción de menú -------------------
    def estilo_boton_y_menu(self, boton, opciones):
        self.estilo_boton(boton)
        if boton.menu():
            boton.menu().deleteLater()
        menu = QMenu()
        self.estilo_menu(menu)
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
            elif opcion == "Cambiar orientación barra":
                action.triggered.connect(self.toggle_orientacion)
            elif opcion == "Cambiar idioma":
                action.triggered.connect(self.toggle_idioma)
            elif opcion == "Cambiar tema":
                action.triggered.connect(self.toggle_tema)
        boton.setMenu(menu)

    # ------------------- Estilo de botón -------------------
    def estilo_boton(self, boton):
        if self.tema == "oscuro":
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 5px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)
        else:
            boton.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #00A8CC, stop:1 #007B8A);
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 5px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #00CED1;
                }
            """)

    # ------------------- Estilo de menú -------------------
    def estilo_menu(self, menu):
        if self.tema == "oscuro":
            menu.setStyleSheet("""
                QMenu {
                    background-color: #444444;
                    border-radius: 10px;
                    border: 1px solid #AAAAAA;
                    padding: 5px;
                    font-size: 15px;
                    color: white;
                }
                QMenu::item {
                    color: white;
                    padding: 8px 25px;
                }
                QMenu::item:selected {
                    background-color: #666666;
                    color: white;
                }
            """)
        else:
            menu.setStyleSheet("""
                QMenu {
                    background-color: #FFFFFF;
                    border-radius: 10px;
                    border: 1px solid #AAAAAA;
                    padding: 5px;
                    font-size: 15px;
                    color: black;
                }
                QMenu::item {
                    color: black;
                    padding: 8px 25px;
                }
                QMenu::item:selected {
                    background-color: #00A8CC;
                    color: black;
                }
            """)

    # ------------------- Toggle -------------------
    def toggle_orientacion(self):
        nueva = "vertical" if self.orientacion_barra == "horizontal" else "horizontal"
        self.cambiar_orientacion_barra(nueva)

    def toggle_idioma(self):
        self.idioma = "Inglés" if self.idioma == "Español" else "Español"

    def toggle_tema(self):
        nueva = "oscuro" if self.tema == "claro" else "claro"
        self.cambiar_tema(nueva)

    # ------------------- Cambiar tema -------------------
    def cambiar_tema(self, tema):
        self.tema = tema
        if tema == "oscuro":
            self.setStyleSheet("background-color: #2E2E2E; color: white;")
            self.etiqueta_fecha.setStyleSheet("font-weight:bold; font-size:18px; color:white; padding:10px;")
        else:
            self.setStyleSheet("background-color: #F0F2F5; color: black;")
            self.etiqueta_fecha.setStyleSheet("font-weight:bold; font-size:18px; color:black; padding:10px;")
        # Reconstruir todos los botones y sus menús
        for boton, opciones in self.botones:
            self.estilo_boton_y_menu(boton, opciones)
        # Reconstruir botón de configuración
        self.estilo_boton_y_menu(self.boton_config, ["Cambiar orientación barra", "Cambiar idioma", "Cambiar tema"])

    # ------------------- Cambiar orientación -------------------
    def cambiar_orientacion_barra(self, orientacion):
        self.orientacion_barra = orientacion.lower()
        while self.layout_principal.count():
            item = self.layout_principal.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                layout = item.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)

        if self.orientacion_barra == "horizontal":
            for i in reversed(range(self.layout_menu.count())):
                w = self.layout_menu.itemAt(i).widget()
                if w:
                    self.layout_menu.removeWidget(w)
                    w.setParent(None)
                    self.barra_horizontal_layout.addWidget(w)
            layout_final = QVBoxLayout()
            layout_final.setContentsMargins(0,0,0,0)
            layout_final.setSpacing(0)
            layout_final.addWidget(self.barra_horizontal_widget)
            layout_final.addWidget(self.contenido_widget)
            self.layout_principal.addLayout(layout_final)
        else:
            for i in reversed(range(self.barra_horizontal_layout.count())):
                w = self.barra_horizontal_layout.itemAt(i).widget()
                if w:
                    self.barra_horizontal_layout.removeWidget(w)
                    w.setParent(None)
                    self.layout_menu.addWidget(w)
            self.menu_widget.setLayout(self.layout_menu)
            layout_final = QHBoxLayout()
            layout_final.setContentsMargins(0,0,0,0)
            layout_final.setSpacing(0)
            layout_final.addWidget(self.menu_widget)
            layout_final.addWidget(self.contenido_widget)
            self.layout_principal.addLayout(layout_final)

    # ------------------- Mostrar widgets -------------------
    def mostrar_widget(self, widget):
        for i in reversed(range(self.contenido_layout.count())):
            w = self.contenido_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contenido_layout.addWidget(widget)
        self.contenido_layout.addWidget(self.etiqueta_fecha)

    def mostrar_logica(self):
        self.mostrar_widget(LogicaSimbolicaTeclado())

    def mostrar_conjuntos(self):
        self.mostrar_widget(CalculadoraConjuntos())

    def mostrar_funciones(self):
        self.mostrar_widget(CalculadoraFunciones())

    def mostrar_limites(self):
        self.mostrar_widget(CalculadoraLimites())

    def mostrar_eliminacion(self):
        self.mostrar_widget(VentanaMatrices())

    # ------------------- Actualizar hora y fecha -------------------
    def actualizar_hora(self):
        fecha = QDate.currentDate().toString("dddd, dd MMMM yyyy")
        hora = QTime.currentTime().toString("hh:mm:ss AP")
        self.etiqueta_fecha.setText(f"{fecha} | {hora}")

# ------------------- MAIN -------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MenuElegante()
    ventana.show()
    sys.exit(app.exec())

