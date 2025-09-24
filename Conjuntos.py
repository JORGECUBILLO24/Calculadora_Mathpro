from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib_venn import venn2


class CalculadoraConjuntos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Conjuntos con Venn")
        self.setGeometry(100, 100, 750, 650)
        self.setStyleSheet("background-color: #f7f7f7;")
        self.initUI()

    def initUI(self):
        # Fuentes
        font_label = QFont("Arial", 12)
        font_input = QFont("Arial", 11)
        font_btn = QFont("Arial", 12, QFont.Weight.Bold)
        font_result = QFont("Consolas", 12)

        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(10, 10, 10, 10)
        layout_principal.setSpacing(10)

        # ----- Entradas -----
        self.label_a = QLabel("Conjunto A (separar elementos con coma):")
        self.label_a.setFont(font_label)
        self.input_a = QLineEdit()
        self.input_a.setFont(font_input)
        self.input_a.setPlaceholderText("Ej: 1, 2, 3")

        self.label_b = QLabel("Conjunto B (separar elementos con coma):")
        self.label_b.setFont(font_label)
        self.input_b = QLineEdit()
        self.input_b.setFont(font_input)
        self.input_b.setPlaceholderText("Ej: 2, 3, 4")

        layout_principal.addWidget(self.label_a)
        layout_principal.addWidget(self.input_a)
        layout_principal.addWidget(self.label_b)
        layout_principal.addWidget(self.input_b)

        # ----- Botones de operaciones -----
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(5)

        self.btn_union = QPushButton("A ∪ B")
        self.btn_interseccion = QPushButton("A ∩ B")
        self.btn_diff_ab = QPushButton("A - B")
        self.btn_diff_ba = QPushButton("B - A")

        for btn in [self.btn_union, self.btn_interseccion, self.btn_diff_ab, self.btn_diff_ba]:
            btn.setFont(font_btn)
            btn.setStyleSheet(
                """
                QPushButton {
                background-color: #00BFFF;  /* Celeste brillante (DeepSkyBlue) */
                color: white;
                border-radius: 5px;
                padding: 15px;
    }
                QPushButton:hover {
                background-color: #009ACD;  /* Celeste más oscuro al pasar el mouse */
    }

                """
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout_botones.addWidget(btn)

        layout_principal.addLayout(layout_botones)

        # ----- Área de resultado -----
        self.resultado = QTextEdit()
        self.resultado.setFont(font_result)
        self.resultado.setReadOnly(True)
        self.resultado.setStyleSheet("background-color: #e0f7fa; border: 1px solid #b2ebf2;")
        self.resultado.setFixedHeight(100)

        layout_principal.addWidget(QLabel("Resultado:"))
        layout_principal.addWidget(self.resultado)

        # ----- Área de gráfico Venn -----
        self.figure, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvas(self.figure)
        layout_principal.addWidget(self.canvas)

        # Conectar botones a funciones
        self.btn_union.clicked.connect(self.oper_union)
        self.btn_interseccion.clicked.connect(self.oper_interseccion)
        self.btn_diff_ab.clicked.connect(self.oper_diff_ab)
        self.btn_diff_ba.clicked.connect(self.oper_diff_ba)

        self.setLayout(layout_principal)

    # -------------------------------
    # Funciones auxiliares
    # -------------------------------
    def obtener_conjunto(self, texto):
        """Convierte el texto en conjunto de enteros o strings"""
        conjunto = set()
        for e in texto.split(","):
            e = e.strip()
            if e != "":
                try:
                    conjunto.add(int(e))  # intenta convertir a número
                except ValueError:
                    conjunto.add(e)  # si no, lo guarda como texto
        return conjunto

    def dibujar_venn(self, A, B, titulo):
        """Dibuja el diagrama de Venn"""
        self.ax.clear()
        if not A and not B:
            self.ax.text(0.5, 0.5, "Conjuntos vacíos",
                         ha='center', va='center', fontsize=14)
        elif not A:
            venn2([set(), B], set_labels=("A", "B"), ax=self.ax)
        elif not B:
            venn2([A, set()], set_labels=("A", "B"), ax=self.ax)
        else:
            venn2([A, B], set_labels=("A", "B"), ax=self.ax)
        self.ax.set_title(titulo)
        self.canvas.draw()

    def mostrar_resultado(self, texto, conjunto):
        """Muestra resultado ordenado en pantalla"""
        if not conjunto:
            self.resultado.setText(f"{texto} = ∅ (conjunto vacío)")
        else:
            self.resultado.setText(f"{texto} = {sorted(conjunto)}")

    # -------------------------------
    # Funciones de operaciones
    # -------------------------------
    def oper_union(self):
        A = self.obtener_conjunto(self.input_a.text())
        B = self.obtener_conjunto(self.input_b.text())
        resultado = A.union(B)
        self.mostrar_resultado("A ∪ B", resultado)
        self.dibujar_venn(A, B, "A ∪ B")

    def oper_interseccion(self):
        A = self.obtener_conjunto(self.input_a.text())
        B = self.obtener_conjunto(self.input_b.text())
        resultado = A.intersection(B)
        self.mostrar_resultado("A ∩ B", resultado)
        self.dibujar_venn(A, B, "A ∩ B")

    def oper_diff_ab(self):
        A = self.obtener_conjunto(self.input_a.text())
        B = self.obtener_conjunto(self.input_b.text())
        resultado = A.difference(B)
        self.mostrar_resultado("A - B", resultado)
        self.dibujar_venn(A, B, "A - B")

    def oper_diff_ba(self):
        A = self.obtener_conjunto(self.input_a.text())
        B = self.obtener_conjunto(self.input_b.text())
        resultado = B.difference(A)
        self.mostrar_resultado("B - A", resultado)
        self.dibujar_venn(A, B, "B - A")


# -------------------------------
# Ejecutar la aplicación
# -------------------------------
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ventana = CalculadoraConjuntos()
    ventana.show()
    sys.exit(app.exec())
