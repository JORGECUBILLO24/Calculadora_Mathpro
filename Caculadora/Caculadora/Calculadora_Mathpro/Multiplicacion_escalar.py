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

        # Dimensiones para Matriz A
        dims_a = QHBoxLayout()
        dims_a.addWidget(QLabel("Filas A:"))
        self.filas_input_a = QLineEdit("3")
        self.filas_input_a.setFixedWidth(50)
        self.filas_input_a.setFont(font_input)
        dims_a.addWidget(self.filas_input_a)
        dims_a.addWidget(QLabel("Columnas A:"))
        self.cols_input_a = QLineEdit("3")
        self.cols_input_a.setFixedWidth(50)
        self.cols_input_a.setFont(font_input)
        dims_a.addWidget(self.cols_input_a)
        self.btn_actualizar_a = QPushButton("Actualizar A")
        self.btn_actualizar_a.setFont(font_btn)
        dims_a.addWidget(self.btn_actualizar_a)

        layout.addLayout(dims_a)

        # Dimensiones para Matriz B
        dims_b = QHBoxLayout()
        dims_b.addWidget(QLabel("Filas B:"))
        self.filas_input_b = QLineEdit("3")
        self.filas_input_b.setFixedWidth(50)
        self.filas_input_b.setFont(font_input)
        dims_b.addWidget(self.filas_input_b)
        dims_b.addWidget(QLabel("Columnas B:"))
        self.cols_input_b = QLineEdit("3")
        self.cols_input_b.setFixedWidth(50)
        self.cols_input_b.setFont(font_input)
        dims_b.addWidget(self.cols_input_b)
        self.btn_actualizar_b = QPushButton("Actualizar B")
        self.btn_actualizar_b.setFont(font_btn)
        dims_b.addWidget(self.btn_actualizar_b)

        layout.addLayout(dims_b)

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

        # Escalares y botones
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Escalar A:"))
        self.escalar_input_a = QLineEdit("2")
        self.escalar_input_a.setFixedWidth(120)
        self.escalar_input_a.setFont(font_input)
        ctrl.addWidget(self.escalar_input_a)
        ctrl.addWidget(QLabel("Escalar B:"))
        self.escalar_input_b = QLineEdit("3")
        self.escalar_input_b.setFixedWidth(120)
        self.escalar_input_b.setFont(font_input)
        ctrl.addWidget(self.escalar_input_b)
        # Opción para operar (sumar/restar) resultados después de multiplicar
        self.op_combo = QComboBox()
        self.op_combo.setFont(font_input)
        self.op_combo.addItems(["No operar", "Sumar resultados", "Restar resultados (A - B)"])
        self.op_combo.setFixedWidth(200)
        ctrl.addWidget(self.op_combo)
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setFont(font_btn)
        ctrl.addWidget(self.btn_calcular)

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
        self.btn_actualizar_a.clicked.connect(self.actualizar_dimensiones_a)
        self.btn_actualizar_b.clicked.connect(self.actualizar_dimensiones_b)

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

    def actualizar_dimensiones_a(self):
        try:
            f = int(self.filas_input_a.text())
            c = int(self.cols_input_a.text())
            if f <= 0 or c <= 0:
                return
            self.tabla.setRowCount(f)
            self.tabla.setColumnCount(c)
            self._rellenar_celdas_con_ceros(self.tabla)
        except Exception:
            return

    def actualizar_dimensiones_b(self):
        try:
            f = int(self.filas_input_b.text())
            c = int(self.cols_input_b.text())
            if f <= 0 or c <= 0:
                return
            self.tabla2.setRowCount(f)
            self.tabla2.setColumnCount(c)
            self._rellenar_celdas_con_ceros(self.tabla2)
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
        esc_text_a = self.escalar_input_a.text().strip()
        try:
            esc_a = Fraction(esc_text_a.replace(",", "."))
        except Exception:
            self.mostrar_procedimiento("Escalar A inválido")
            return
        # Multiplicar matriz A
        C_a, texto_a = multiplicar_matriz_por_escalar(A, esc_a)

        # Multiplicar matriz B
        B = self.leer_tabla(self.tabla2)
        esc_text_b = self.escalar_input_b.text().strip()
        try:
            esc_b = Fraction(esc_text_b.replace(",", "."))
        except Exception:
            self.mostrar_procedimiento("Escalar B inválido")
            return
        C_b, texto_b = multiplicar_matriz_por_escalar(B, esc_b)

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
