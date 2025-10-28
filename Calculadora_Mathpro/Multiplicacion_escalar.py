from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QTextEdit, QSizePolicy
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt, QTimer
from fractions import Fraction


def multiplicar_matriz_por_escalar(A, escalar: Fraction):
    """
    Multiplica la matriz A por el escalar dado.
    A: lista de listas de Fraction
    escalar: Fraction
    Devuelve (C, texto_pasos)
    """
    filas = len(A)
    cols = len(A[0]) if filas > 0 else 0
    C = [[A[i][j] * escalar for j in range(cols)] for i in range(filas)]

    def fmt(x: Fraction):
        return str(x.numerator) if x.denominator == 1 else str(x)

    texto = f"Escalar: {fmt(escalar)}\nMatriz A:\n"
    for fila in A:
        texto += "[ " + "  ".join(fmt(x) for x in fila) + " ]\n"

    texto += "\nPasos de la multiplicación por escalar:\n"
    for i in range(filas):
        for j in range(cols):
            texto += f"Elemento ({i+1},{j+1}): {A[i][j]} · {fmt(escalar)} = {C[i][j]}\n"

    texto += "\nResultado A · escalar:\n"
    for fila in C:
        texto += "[ " + "  ".join(fmt(x) for x in fila) + " ]\n"

    return C, texto


class VentanaMultiplicacionEscalar(QWidget):
    """Ventana independiente para multiplicación de una matriz por un escalar.

    Similar en estilo a `Determinantes.py`: permite ingresar dimensiones,
    editar la matriz, elegir un escalar y ver el procedimiento. Se fuerza el
    color de texto de las celdas a negro para garantizar visibilidad.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiplicación por escalar")
        self.setStyleSheet("background-color:#F0F4F8; color: #000000;")

        font_label = QFont("Segoe UI", 12, QFont.Weight.Bold)
        font_input = QFont("Segoe UI", 11)
        font_btn = QFont("Segoe UI", 11, QFont.Weight.Bold)

        layout = QVBoxLayout()

        # Dimensiones
        dims = QHBoxLayout()
        dims.addWidget(QLabel("Filas:"))
        self.filas_input = QLineEdit("3")
        self.filas_input.setFixedWidth(50)
        self.filas_input.setFont(font_input)
        dims.addWidget(self.filas_input)
        dims.addWidget(QLabel("Columnas:"))
        self.cols_input = QLineEdit("3")
        self.cols_input.setFixedWidth(50)
        self.cols_input.setFont(font_input)
        dims.addWidget(self.cols_input)

        layout.addLayout(dims)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setRowCount(3)
        self.tabla.setColumnCount(3)
        self.tabla.setFont(QFont("Consolas", 12))
        self._rellenar_celdas_con_ceros()
        layout.addWidget(self.tabla)

        # Escalar y botones
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Escalar:"))
        self.escalar_input = QLineEdit("2")
        self.escalar_input.setFixedWidth(120)
        self.escalar_input.setFont(font_input)
        ctrl.addWidget(self.escalar_input)
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setFont(font_btn)
        ctrl.addWidget(self.btn_calcular)
        self.btn_actualizar = QPushButton("Actualizar dimensiones")
        self.btn_actualizar.setFont(font_btn)
        ctrl.addWidget(self.btn_actualizar)

        layout.addLayout(ctrl)

        # Procedimiento
        self.procedimiento = QTextEdit()
        self.procedimiento.setFont(QFont("Consolas", 11))
        self.procedimiento.setMinimumHeight(200)
        self.procedimiento.setStyleSheet("background-color:white; color:#000; border:2px solid #B0BEC5; border-radius:8px;")
        layout.addWidget(self.procedimiento)

        self.setLayout(layout)

        # Conexiones
        self.btn_calcular.clicked.connect(self.calcular)
        self.btn_actualizar.clicked.connect(self.actualizar_dimensiones)

    def _rellenar_celdas_con_ceros(self):
        filas = self.tabla.rowCount()
        cols = self.tabla.columnCount()
        for i in range(filas):
            for j in range(cols):
                item = self.tabla.item(i, j)
                if item is None:
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # forzar texto negro y fuente legible
                    item.setForeground(Qt.GlobalColor.black)
                    item.setFont(QFont("Consolas", 12))
                    self.tabla.setItem(i, j, item)

    def actualizar_dimensiones(self):
        try:
            f = int(self.filas_input.text())
            c = int(self.cols_input.text())
            if f <= 0 or c <= 0:
                return
            self.tabla.setRowCount(f)
            self.tabla.setColumnCount(c)
            self._rellenar_celdas_con_ceros()
        except Exception:
            return

    def leer_tabla(self):
        filas = self.tabla.rowCount()
        cols = self.tabla.columnCount()
        M = []
        for i in range(filas):
            row = []
            for j in range(cols):
                item = self.tabla.item(i, j)
                val = item.text().strip() if item and item.text() else "0"
                try:
                    val_norm = val.replace(",", ".")
                    row.append(Fraction(val_norm))
                except Exception:
                    row.append(Fraction(0))
            M.append(row)
        return M

    def mostrar_procedimiento(self, texto: str):
        self.procedimiento.setPlainText(texto)
        try:
            cursor = self.procedimiento.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.procedimiento.setTextCursor(cursor)
            self.procedimiento.ensureCursorVisible()
        except Exception:
            pass

    def calcular(self):
        A = self.leer_tabla()
        esc_text = self.escalar_input.text().strip()
        try:
            esc = Fraction(esc_text.replace(",", "."))
        except Exception:
            self.mostrar_procedimiento("Escalar inválido")
            return
        C, texto = multiplicar_matriz_por_escalar(A, esc)
        self.mostrar_procedimiento(texto)
