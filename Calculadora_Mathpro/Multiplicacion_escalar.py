from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QTextEdit, QSizePolicy, QComboBox
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

        # Tablas para dos matrices (A y B) lado a lado
        tablas_layout = QHBoxLayout()

        col_a_layout = QVBoxLayout()
        col_a_layout.addWidget(QLabel("Matriz A:"))
        self.tabla = QTableWidget()
        self.tabla.setRowCount(3)
        self.tabla.setColumnCount(3)
        self.tabla.setFont(QFont("Consolas", 12))
        self._rellenar_celdas_con_ceros(self.tabla)
        col_a_layout.addWidget(self.tabla)

        col_b_layout = QVBoxLayout()
        col_b_layout.addWidget(QLabel("Matriz B:"))
        self.tabla2 = QTableWidget()
        self.tabla2.setRowCount(3)
        self.tabla2.setColumnCount(3)
        self.tabla2.setFont(QFont("Consolas", 12))
        self._rellenar_celdas_con_ceros(self.tabla2)
        col_b_layout.addWidget(self.tabla2)

        tablas_layout.addLayout(col_a_layout)
        tablas_layout.addLayout(col_b_layout)
        layout.addLayout(tablas_layout)

        # Escalar y botones
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Escalar:"))
        self.escalar_input = QLineEdit("2")
        self.escalar_input.setFixedWidth(120)
        self.escalar_input.setFont(font_input)
        ctrl.addWidget(self.escalar_input)
        # Opción para operar (sumar/restar) resultados después de multiplicar
        self.op_combo = QComboBox()
        self.op_combo.setFont(font_input)
        self.op_combo.addItems(["No operar", "Sumar resultados", "Restar resultados (A - B)"])
        self.op_combo.setFixedWidth(200)
        ctrl.addWidget(self.op_combo)
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

    def _rellenar_celdas_con_ceros(self, table: QTableWidget):
        filas = table.rowCount()
        cols = table.columnCount()
        for i in range(filas):
            for j in range(cols):
                item = table.item(i, j)
                if item is None:
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # forzar texto negro y fuente legible
                    item.setForeground(Qt.GlobalColor.black)
                    item.setFont(QFont("Consolas", 12))
                    table.setItem(i, j, item)

    def actualizar_dimensiones(self):
        try:
            f = int(self.filas_input.text())
            c = int(self.cols_input.text())
            if f <= 0 or c <= 0:
                return
            # actualizar ambas tablas
            for t in (self.tabla, self.tabla2):
                t.setRowCount(f)
                t.setColumnCount(c)
                self._rellenar_celdas_con_ceros(t)
        except Exception:
            return

    def leer_tabla(self, table: QTableWidget):
        filas = table.rowCount()
        cols = table.columnCount()
        M = []
        for i in range(filas):
            row = []
            for j in range(cols):
                item = table.item(i, j)
                val = item.text().strip() if item and item.text() else "0"
                try:
                    val_norm = val.replace(",", ".")
                    row.append(Fraction(val_norm))
                except Exception:
                    row.append(Fraction(0))
            M.append(row)
        return M

    def _operar_matrices_resultado(self, A, B, oper: str):
        """
        Opera las matrices A y B (listas de Fraction) según oper: 'sum' o 'sub'.
        Devuelve (R, texto) donde R es la matriz resultado o None si no compatible.
        """
        filas_a = len(A)
        cols_a = len(A[0]) if filas_a > 0 else 0
        filas_b = len(B)
        cols_b = len(B[0]) if filas_b > 0 else 0

        if filas_a != filas_b or cols_a != cols_b:
            return None, "Las dimensiones de las matrices resultantes no coinciden; no se puede operar."

        R = [[None for _ in range(cols_a)] for _ in range(filas_a)]

        def fmt(x: Fraction):
            return str(x.numerator) if x.denominator == 1 else str(x)

        texto = "Pasos de la operación entre resultados:\n"
        texto += f"Operación: {'Suma' if oper=='sum' else 'Resta'}\n"
        for i in range(filas_a):
            for j in range(cols_a):
                if oper == 'sum':
                    R[i][j] = A[i][j] + B[i][j]
                    texto += f"Elemento ({i+1},{j+1}): {A[i][j]} + {B[i][j]} = {R[i][j]}\n"
                else:
                    R[i][j] = A[i][j] - B[i][j]
                    texto += f"Elemento ({i+1},{j+1}): {A[i][j]} - {B[i][j]} = {R[i][j]}\n"

        texto += "\nResultado final:\n"
        for fila in R:
            texto += "[ " + "  ".join(fmt(x) for x in fila) + " ]\n"

        return R, texto

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
        A = self.leer_tabla(self.tabla)
        esc_text = self.escalar_input.text().strip()
        try:
            esc = Fraction(esc_text.replace(",", "."))
        except Exception:
            self.mostrar_procedimiento("Escalar inválido")
            return
        # Multiplicar matriz A
        C_a, texto_a = multiplicar_matriz_por_escalar(A, esc)

        # Multiplicar matriz B
        B = self.leer_tabla(self.tabla2)
        C_b, texto_b = multiplicar_matriz_por_escalar(B, esc)

        # Combinar textos de procedimiento
        texto_completo = "--- Resultado para Matriz A ---\n" + texto_a + "\n\n"
        texto_completo += "--- Resultado para Matriz B ---\n" + texto_b

        # Revisar si el usuario pidió operar los resultados
        op_text = self.op_combo.currentText()
        if op_text != "No operar":
            oper = 'sum' if op_text.startswith('Sumar') else 'sub'
            R, texto_op = self._operar_matrices_resultado(C_a, C_b, oper)
            texto_completo += "\n\n--- Operación entre resultados ---\n"
            texto_completo += texto_op

        self.mostrar_procedimiento(texto_completo)
