import sys
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QSizePolicy
)
from PyQt6.QtGui import QFont

class CalculadoraLimites(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Límites PRO - Plano cartesiano")
        self.setGeometry(100, 50, 1000, 700)
        self.setStyleSheet("background-color: white;")
        self.campo_activo = 'funcion'

        # Layout principal vertical
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        # Layout de entradas y teclado
        self.layout_entrada = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_entrada)

        # Panel de entradas
        panel_entradas = QVBoxLayout()
        self.layout_entrada.addLayout(panel_entradas, 1)

        # Entrada de función
        self.func_input = QLineEdit()
        self.func_input.setFont(QFont("Arial", 16))
        self.func_input.setPlaceholderText("Función: ej. (x**2-4)/(x-2)")
        self.func_input.setStyleSheet("border: 2px solid #00bfff; border-radius: 10px; padding:5px;")
        self.func_input.focusInEvent = lambda event: self.set_campo_activo('funcion')
        panel_entradas.addWidget(QLabel("Función:"))
        panel_entradas.addWidget(self.func_input)

        # Entrada del límite
        self.punto_input = QLineEdit()
        self.punto_input.setFont(QFont("Arial", 16))
        self.punto_input.setPlaceholderText("Punto del límite: ej. 2, oo o -oo")
        self.punto_input.setStyleSheet("border: 2px solid #00bfff; border-radius: 10px; padding:5px;")
        self.punto_input.focusInEvent = lambda event: self.set_campo_activo('limite')
        panel_entradas.addWidget(QLabel("Límite en x → "))
        panel_entradas.addWidget(self.punto_input)

        # Teclado matemático
        self.teclado_layout = QGridLayout()
        self.botones = [
            "∞", "-∞", "→", "Δx", "ε", "δ",
            "lim", "Σ", "Π", "√", "|x|", "^",
            "sin", "cos", "tan", "ln", "log", "π"
        ]
        positions = [(i,j) for i in range(3) for j in range(6)]
        for pos, texto in zip(positions, self.botones):
            boton = QPushButton(texto)
            boton.setFont(QFont("Arial", 14))
            boton.setFixedSize(60,50)
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #00bfff;
                    color: white;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #009acd;
                }
            """)
            boton.clicked.connect(lambda checked, t=texto: self.insertar_texto(t))
            self.teclado_layout.addWidget(boton, *pos)
        panel_entradas.addLayout(self.teclado_layout)

        # Botón calcular límite
        self.calc_btn = QPushButton("Calcular Límite")
        self.calc_btn.setFont(QFont("Arial", 16))
        self.calc_btn.setFixedHeight(50)
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #00bfff;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #009acd;
            }
        """)
        self.calc_btn.clicked.connect(self.calcular_limite)
        panel_entradas.addWidget(self.calc_btn)

        # Resultado
        self.resultado = QTextEdit()
        self.resultado.setFont(QFont("Arial", 14))
        self.resultado.setReadOnly(True)
        self.resultado.setStyleSheet("border: 2px solid #00bfff; border-radius: 10px; padding:5px;")
        panel_entradas.addWidget(self.resultado)

        # Panel de gráfica
        self.canvas = FigureCanvas(plt.Figure(figsize=(4,4)))
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout_entrada.addWidget(self.canvas, 2)

    def set_campo_activo(self, campo):
        self.campo_activo = campo

    def insertar_texto(self, texto):
        target = self.func_input if self.campo_activo == 'funcion' else self.punto_input
        if texto == "∞":
            target.insert("oo")
        elif texto == "-∞":
            target.insert("-oo")
        else:
            target.insert(texto)

    def calcular_limite(self):
        x = sp.symbols('x')
        expr_text = self.func_input.text()
        punto_text = self.punto_input.text().strip()
        if not expr_text or not punto_text:
            self.resultado.setText("Por favor, completa la función y el punto del límite.")
            return
        try:
            expr_text = expr_text.replace("√","sqrt").replace("|x|","Abs(x)").replace("π","pi")
            expr_text = expr_text.replace("Δx","Delta(x)").replace("ε","Epsilon").replace("δ","Delta").replace("lim","")
            funcion = sp.sympify(expr_text)

            # Punto del límite
            if punto_text.lower() == "oo":
                punto = sp.oo
            elif punto_text.lower() == "-oo":
                punto = -sp.oo
            else:
                punto = sp.sympify(punto_text)

            # Calcular límites
            limite_izq = sp.limit(funcion, x, punto, dir='-')
            limite_der = sp.limit(funcion, x, punto, dir='+')
            limite_general = sp.limit(funcion, x, punto)
            self.resultado.setText(f"Límite por la izquierda: {limite_izq}\nLímite por la derecha: {limite_der}\nLímite general: {limite_general}")

            # Graficar
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)

            # Rango X
            if punto not in [sp.oo, -sp.oo]:
                rango = 5
                x_vals = np.linspace(float(punto)-rango, float(punto)+rango, 400)
            elif punto == sp.oo:
                x_vals = np.linspace(10,50,400)
            else:
                x_vals = np.linspace(-50,-10,400)

            f_lambdified = sp.lambdify(x, funcion, "numpy")
            y_vals = f_lambdified(x_vals)

            # Eje Y automático
            y_finite = y_vals[np.isfinite(y_vals)]
            if len(y_finite) > 0:
                y_min, y_max = min(y_finite), max(y_finite)
                margen = (y_max - y_min)*0.2
                ax.set_ylim(y_min-margen, y_max+margen)

            # Función
            ax.plot(x_vals, y_vals, color="#00bfff", label=str(funcion))

            # Puntos de límite
            if punto not in [sp.oo, -sp.oo]:
                if limite_izq != limite_der:
                    ax.plot(float(punto), float(limite_izq), 'o', markerfacecolor='white', markeredgecolor='red', markersize=8)
                    ax.plot(float(punto), float(limite_der), 'o', markerfacecolor='white', markeredgecolor='green', markersize=8)
                else:
                    ax.plot(float(punto), float(limite_general), 'o', color='purple', markersize=8)
                ax.axvline(float(punto), color='gray', linestyle='--', alpha=0.5)

            # Plano cartesiano tipo libro
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
            ax.grid(True, linestyle='--', alpha=0.5)

            ax.set_aspect('equal')
            ax.legend()
            ax.set_title("Gráfica alrededor del límite")
            self.canvas.draw()

        except Exception as e:
            self.resultado.setText(f"Error al calcular: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculadoraLimites()
    window.show()
    sys.exit(app.exec())
