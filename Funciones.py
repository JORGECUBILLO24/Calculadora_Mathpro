import sys
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QTextEdit, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        fig.tight_layout()

    def clear(self):
        self.ax.cla()
        self.draw()

class CalculadoraFunciones(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Científica de Funciones")
        self.setGeometry(50, 50, 1200, 650)
        self.setStyleSheet("background-color: #f0f8ff; color: #000000;")

        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        self.tab_funcs = QWidget()
        tabs.addTab(self.tab_funcs, "Funciones & Gráficas")
        layout.addWidget(tabs)
        self.setLayout(layout)

        self._build_tab_funciones()

        # Símbolos especiales y mapeo para SymPy
        self.symbol_map = {
            "√(": "sqrt(",
            "|x|": "Abs(x)",
            "^": "**",
            "π": "pi",
            "e": "E"
        }

    def _build_tab_funciones(self):
        main = QHBoxLayout()
        controls = QVBoxLayout()

        # Entrada de función
        controls.addWidget(QLabel("Ingrese f(x):"))
        self.func_input = QLineEdit("(√(|x|+1)+2)/(x^2+1)")
        self.func_input.setStyleSheet("padding:5px; font-size:14px; color: #000000;")
        controls.addWidget(self.func_input)

        # Rango x
        self.xmin = QLineEdit("-10")
        self.xmax = QLineEdit("10")
        range_layout = QHBoxLayout()
        xmin_label = QLabel("x min:")
        xmin_label.setStyleSheet("color: #000000;")
        range_layout.addWidget(xmin_label)
        range_layout.addWidget(self.xmin)
        xmax_label = QLabel("x max:")
        xmax_label.setStyleSheet("color: #000000;")
        range_layout.addWidget(xmax_label)
        range_layout.addWidget(self.xmax)
        controls.addLayout(range_layout)

        # Botón graficar
        self.btn_plot = QPushButton("Graficar")
        self.btn_plot.setStyleSheet("background-color: #4da6ff; color:white; font-weight:bold;")
        self.btn_plot.clicked.connect(self.plot_function)
        controls.addWidget(self.btn_plot)

        # Teclado especial
        teclado_frame = QFrame()
        teclado_layout = QGridLayout()
        funciones = [
            "√","|x|","sin","cos","tan","arcsin","arccos","arctan",
            "sinh","cosh","tanh","exp","log","log10","Abs","π","e"
        ]
        for i, t in enumerate(funciones):
            btn = QPushButton(t)
            btn.setStyleSheet(
                "background-color:#80c1ff; color:white; font-weight:bold; font-size:13px; border-radius:5px;"
            )
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.clicked.connect(lambda checked, txt=t: self.insert_text(txt))
            teclado_layout.addWidget(btn, i // 4, i % 4)
        teclado_frame.setLayout(teclado_layout)
        controls.addWidget(QLabel("Teclado de funciones:"))
        controls.addWidget(teclado_frame)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(150)
        self.log.setStyleSheet("background-color:#ffffff; color: #000000; border-radius:5px; padding:5px;")
        controls.addWidget(QLabel("Registro:"))
        controls.addWidget(self.log)

        # Canvas de gráfica
        self.canvas = PlotCanvas(self, width=5, height=4, dpi=100)

        main.addLayout(controls, 3)
        main.addWidget(self.canvas, 5)
        self.tab_funcs.setLayout(main)

    def insert_text(self, text):
        cursor = self.func_input.cursorPosition()
        current = self.func_input.text()
        new_text = current[:cursor] + text + current[cursor:]
        self.func_input.setText(new_text)
        self.func_input.setCursorPosition(cursor + len(text))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.plot_function()

    def plot_function(self):
        self.log.clear()
        expr = self.func_input.text()

        try:
            xmin = float(self.xmin.text())
            xmax = float(self.xmax.text())
            if xmin >= xmax:
                self.log.append("Error: x min debe ser menor que x max")
                return
        except:
            self.log.append("Error: rango inválido")
            return

        # Reemplazo de símbolos especiales
        for k, v in self.symbol_map.items():
            expr = expr.replace(k, v)

        x = sp.symbols('x')
        transformations = standard_transformations + (implicit_multiplication_application,)
        try:
            func_sympy = parse_expr(expr, transformations=transformations)
            func_lambda = sp.lambdify(x, func_sympy, modules=['numpy'])
        except Exception as e:
            self.log.append(f"Error al interpretar la función: {e}")
            return

        x_vals = np.linspace(xmin, xmax, 1000)
        try:
            y_vals = func_lambda(x_vals)
        except Exception as e:
            self.log.append(f"Error al evaluar la función: {e}")
            return

        self.canvas.clear()
        self.canvas.ax.plot(x_vals, y_vals, color="#0059b3", label=f"f(x) = {expr}")
        self.canvas.ax.set_xlabel("x")
        self.canvas.ax.set_ylabel("f(x)")
        self.canvas.ax.grid(True, linestyle="--", alpha=0.7)
        self.canvas.ax.legend()
        self.canvas.draw()

        self.log.append(f"Función: {expr}")
        self.log.append(f"Rango: [{xmin}, {xmax}]")
        self.log.append("¡Gráfica generada correctamente!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CalculadoraFunciones()
    win.show()
    sys.exit(app.exec())
