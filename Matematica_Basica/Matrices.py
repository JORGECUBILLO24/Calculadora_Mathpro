from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QApplication
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from fractions import Fraction
import sys
import copy

# =================== VENTANA ===================
class VentanaMatrices(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:#F0F4F8; color: #000000;")
        self.setWindowTitle("Operaciones con Matrices")

        # Fuentes
        font_label = QFont("Segoe UI", 14, QFont.Weight.Bold)
        font_input = QFont("Segoe UI", 12)
        font_btn   = QFont("Segoe UI", 13, QFont.Weight.Bold)

        # --- Dimensiones ---
        input_layout = QHBoxLayout()

        # Matriz A
        self.a_widget = QWidget()
        a_layout = QVBoxLayout(self.a_widget)
        a_label = QLabel("Matriz A"); a_label.setFont(font_label); a_label.setStyleSheet("color: #000000;")
        a_layout.addWidget(a_label)
        filas_a_layout = QHBoxLayout()
        filas_a_label = QLabel("Filas"); filas_a_label.setFont(QFont("Segoe UI", 12)); filas_a_label.setFixedWidth(70)
        self.filas_A_input = QLineEdit("3"); self.filas_A_input.setFixedWidth(60); self.filas_A_input.setFont(font_input)
        filas_a_layout.addWidget(filas_a_label)
        filas_a_layout.addWidget(self.filas_A_input)
        a_layout.addLayout(filas_a_layout)
        columnas_a_layout = QHBoxLayout()
        columnas_a_label = QLabel("Columnas"); columnas_a_label.setFont(QFont("Segoe UI", 12)); columnas_a_label.setFixedWidth(70)
        self.columnas_A_input = QLineEdit("3"); self.columnas_A_input.setFixedWidth(60); self.columnas_A_input.setFont(font_input)
        columnas_a_layout.addWidget(columnas_a_label)
        columnas_a_layout.addWidget(self.columnas_A_input)
        a_layout.addLayout(columnas_a_layout)

        # Matriz B
        self.b_widget = QWidget()
        b_layout = QVBoxLayout(self.b_widget)
        b_label = QLabel("Matriz B"); b_label.setFont(font_label); b_label.setStyleSheet("color: #000000;")
        b_layout.addWidget(b_label)
        filas_b_layout = QHBoxLayout()
        filas_b_label = QLabel("Filas"); filas_b_label.setFont(QFont("Segoe UI", 12)); filas_b_label.setFixedWidth(70)
        self.filas_B_input = QLineEdit("3"); self.filas_B_input.setFixedWidth(60); self.filas_B_input.setFont(font_input)
        filas_b_layout.addWidget(filas_b_label)
        filas_b_layout.addWidget(self.filas_B_input)
        b_layout.addLayout(filas_b_layout)
        columnas_b_layout = QHBoxLayout()
        columnas_b_label = QLabel("Columnas"); columnas_b_label.setFont(QFont("Segoe UI", 12)); columnas_b_label.setFixedWidth(70)
        self.columnas_B_input = QLineEdit("3"); self.columnas_B_input.setFixedWidth(60); self.columnas_B_input.setFont(font_input)
        columnas_b_layout.addWidget(columnas_b_label)
        columnas_b_layout.addWidget(self.columnas_B_input)
        b_layout.addLayout(columnas_b_layout)

        input_layout.addWidget(self.a_widget)
        input_layout.addSpacing(40)
        input_layout.addWidget(self.b_widget)
        input_layout.addStretch()

        # --- Matriz A y B ---
        matrices_layout = QHBoxLayout()
        self.tabla_A = QTableWidget(); self.config_tabla(self.tabla_A, "Matriz A")
        self.tabla_B = QTableWidget(); self.config_tabla(self.tabla_B, "Matriz B")
        matrices_layout.addWidget(self.tabla_A)
        matrices_layout.addWidget(self.tabla_B)

        # --- Botones ---
        botones_layout = QHBoxLayout()
        self.operacion_combo = QComboBox()
        self.operacion_combo.addItems(["Suma", "Resta", "Multiplicacion", "Gauss", "Gauss-Jordan"])
        self.operacion_combo.setFont(font_input)
        self.operacion_combo.setFixedWidth(220)
        self.operacion_combo.setStyleSheet("background-color:#1E88E5; color:white; border-radius:15px; padding:8px;")

        self.btn_ejecutar = QPushButton("Ejecutar operación")
        self.btn_ejecutar.setFont(font_btn)
        self.btn_ejecutar.setStyleSheet("background-color:#43A047; color:white; border-radius:15px; padding:8px;")
        self.btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)

        botones_layout.addWidget(self.operacion_combo)
        botones_layout.addWidget(self.btn_ejecutar)

        # --- Procedimiento ---
        self.procedimiento_text = QTextEdit()
        self.procedimiento_text.setFont(QFont("Consolas", 11))
        self.procedimiento_text.setPlaceholderText("Procedimiento")
        self.procedimiento_text.setMinimumHeight(250)
        self.procedimiento_text.setStyleSheet("background-color:white; color: #000000; border:2px solid #B0BEC5; border-radius:12px;")

        # Layout principal
        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addLayout(matrices_layout)
        layout.addLayout(botones_layout)
        layout.addWidget(self.procedimiento_text)
        self.setLayout(layout)

        # Conexiones
        self.btn_ejecutar.clicked.connect(self.ejecutar_operacion)
        self.filas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.filas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.operacion_combo.currentTextChanged.connect(self.toggle_matrizB)

    # =================== CONFIG TABLAS ===================
    def config_tabla(self, tabla, titulo):
        tabla.setStyleSheet("background-color:white; border-radius:12px;")
        tabla.setFont(QFont("Consolas", 12))
        tabla.setRowCount(3); tabla.setColumnCount(3)
        tabla.setHorizontalHeaderLabels([f"C{j+1}" for j in range(3)])
        tabla.setVerticalHeaderLabels([f"F{i+1}" for i in range(3)])
        tabla.setMinimumSize(220, 180)
        tabla.setCornerButtonEnabled(False)
        tabla.setToolTip(titulo)
        
        # <-- Agrega estas líneas para hacer las celdas más grandes:
        tabla.horizontalHeader().setDefaultSectionSize(80)  # Ancho de columnas
        tabla.verticalHeader().setDefaultSectionSize(60)    # Alto de filas
        tabla.setColumnWidth(0, 80)  # Ancho específico para primera columna
        tabla.setColumnWidth(1, 80)  # Ancho específico para segunda columna  
        tabla.setColumnWidth(2, 80)  # Ancho específico para tercera columna

    def actualizar_dimensiones(self):
        try:
            filas_A = int(self.filas_A_input.text())
            cols_A = int(self.columnas_A_input.text())
            filas_B = int(self.filas_B_input.text())
            cols_B = int(self.columnas_B_input.text())
            if filas_A <= 0 or cols_A <= 0 or filas_B <= 0 or cols_B <= 0: return

            # For tabla_A
            self.tabla_A.setRowCount(filas_A)
            self.tabla_A.setColumnCount(cols_A)
            self.tabla_A.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cols_A)])
            self.tabla_A.setVerticalHeaderLabels([f"F{i+1}" for i in range(filas_A)])
            self.tabla_A.horizontalHeader().setDefaultSectionSize(80)
            self.tabla_A.verticalHeader().setDefaultSectionSize(60)
            for j in range(cols_A):
                self.tabla_A.setColumnWidth(j, 80)

            # For tabla_B
            self.tabla_B.setRowCount(filas_B)
            self.tabla_B.setColumnCount(cols_B)
            self.tabla_B.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cols_B)])
            self.tabla_B.setVerticalHeaderLabels([f"F{i+1}" for i in range(filas_B)])
            self.tabla_B.horizontalHeader().setDefaultSectionSize(80)
            self.tabla_B.verticalHeader().setDefaultSectionSize(60)
            for j in range(cols_B):
                self.tabla_B.setColumnWidth(j, 80)
        except:
            return

    def toggle_matrizB(self):
        """Oculta Matriz B si la operación es Gauss/Gauss-Jordan"""
        if self.operacion_combo.currentText() in ["Gauss", "Gauss-Jordan"]:
            self.b_widget.hide()
            self.tabla_B.hide()
        else:
            self.b_widget.show()
            self.tabla_B.show()

    # =================== UTILIDADES ===================
    def leer_tabla(self, tabla):
        filas, cols = tabla.rowCount(), tabla.columnCount()
        matriz = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                item = tabla.item(i, j)
                val = item.text().strip() if item else "0"
                try:
                    fila.append(Fraction(val if val else "0"))
                except:
                    fila.append(Fraction(0))
            matriz.append(fila)
        return matriz

    def mostrar_matriz(self, M):
        texto = ""
        for fila in M:
            texto += "[ " + "  ".join(str(x) for x in fila) + " ]\n"
        return texto

    # =================== GAUSS & GAUSS-JORDAN ===================
    def eliminacion_adelante(self, M):
        pasos = []
        A = copy.deepcopy(M)
        n, m = len(A), len(A[0])
        row = 0
        pivots = []

        for col in range(m-1):  # suponer última columna es RHS si es sistema
            # seleccionar pivote
            sel = None
            for r in range(row, n):
                if A[r][col] != 0:
                    sel = r
                    break
            if sel is None:
                continue
            if sel != row:
                A[row], A[sel] = A[sel], A[row]
                pasos.append(f"Intercambio F{row+1} ↔ F{sel+1}\n{self.mostrar_matriz(A)}")
            # normalizar pivote
            pivot = A[row][col]
            if pivot != 1:
                A[row] = [x / pivot for x in A[row]]
                pasos.append(f"F{row+1} ÷ {pivot}\n{self.mostrar_matriz(A)}")
            # eliminar debajo
            for r in range(row+1, n):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor*A[row][j] for j in range(m)]
                    pasos.append(f"F{r+1} → F{r+1} - ({factor})·F{row+1}\n{self.mostrar_matriz(A)}")
            pivots.append(col)
            row +=1
        return pasos, A, pivots

    def eliminacionPivote(self, M, pivots):
        pasos = []
        A = copy.deepcopy(M)
        n, m = len(A), len(A[0])
        # eliminar arriba de pivotes
        for pr in reversed(range(len(pivots))):
            col = pivots[pr]
            for r in range(pr):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor*A[pr][j] for j in range(m)]
                    pasos.append(f"F{r+1} → F{r+1} - ({factor})·F{pr+1}\n{self.mostrar_matriz(A)}")
        return pasos, A

    def analizar_sistema(self, A, pivots):
        n, m = len(A), len(A[0])
        NV = m-1
        # revisar inconsistencias
        for r in range(n):
            if all(A[r][c]==0 for c in range(NV)) and A[r][-1]!=0:
                return "⚠️ Sistema INCONSISTENTE → No tiene solución."

        # variables libres
        libres = [i for i in range(NV) if i not in pivots]
        if libres:
            # parametrizar
            ecuaciones = []
            for r, c in enumerate(pivots):
                rhs = A[r][-1]
                expr = f"{rhs}"
                for l in libres:
                    coef = A[r][l]
                    if coef != 0:
                        sign = " - " if coef>0 else " + "
                        expr += f"{sign}{abs(coef)}·t{libres.index(l)+1}"
                ecuaciones.append(f"x{c+1} = {expr}")
            for idx,l in enumerate(libres):
                ecuaciones.append(f"x{l+1} = t{idx+1}")
            texto = "✅ Sistema CONSISTENTE → Infinitas soluciones.\nVariables libres: " + ", ".join(f"x{i+1}" for i in libres) + "\nSolución paramétrica:\n" + "\n".join(ecuaciones)
            return texto
        else:
            # solución única
            soluciones = [None]*NV
            for r,c in enumerate(pivots):
                soluciones[c] = A[r][-1]
            texto = "✅ Sistema CONSISTENTE → Solución única:\n" + "\n".join(f"x{i+1} = {soluciones[i]}" for i in range(NV))
            return texto

    def gauss_jordan(self, M):
        pasos_fwd, A, pivots = self.eliminacion_adelante(M)
        pasos_back, A_rref = self.eliminacionPivote(A, pivots)
        pasos = pasos_fwd + pasos_back
        return pasos, A_rref, pivots

    # =================== OPERACIONES ===================
    def ejecutar_operacion(self):
        op = self.operacion_combo.currentText()
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B)

        try:
            if op == "Suma":
                if len(A) != len(B) or len(A[0]) != len(B[0]):
                    self.procedimiento_text.setPlainText("Error: A y B deben tener mismas dimensiones.")
                    return
                C = [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\nMatriz B:\n" + self.mostrar_matriz(B) + "\nPasos de la suma:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += f"Elemento ({i+1},{j+1}): A[{i+1}][{j+1}] + B[{i+1}][{j+1}] = {A[i][j]} + {B[i][j]} = {C[i][j]}\n"
                texto += "\nResultado A + B:\n" + self.mostrar_matriz(C)
                self.procedimiento_text.setPlainText(texto)

            elif op == "Resta":
                if len(A) != len(B) or len(A[0]) != len(B[0]):
                    self.procedimiento_text.setPlainText("Error: A y B deben tener mismas dimensiones.")
                    return
                C = [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\nMatriz B:\n" + self.mostrar_matriz(B) + "\nPasos de la resta:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += f"Elemento ({i+1},{j+1}): A[{i+1}][{j+1}] - B[{i+1}][{j+1}] = {A[i][j]} - {B[i][j]} = {C[i][j]}\n"
                texto += "\nResultado A - B:\n" + self.mostrar_matriz(C)
                self.procedimiento_text.setPlainText(texto)

            elif op == "Multiplicacion":
                if len(A[0]) != len(B):
                    self.procedimiento_text.setPlainText("Error: columnas(A) ≠ filas(B).")
                    return
                C = [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\nMatriz B:\n" + self.mostrar_matriz(B) + "\nPasos de la multiplicación:\n"
                for i in range(len(A)):
                    for j in range(len(B[0])):
                        values = [f"{A[i][k]} * {B[k][j]}" for k in range(len(B))]
                        sum_str = " + ".join(values)
                        result = sum(A[i][k] * B[k][j] for k in range(len(B)))
                        texto += f"Elemento ({i+1},{j+1}): {sum_str} = {result}\n"
                texto += "\nResultado A × B:\n" + self.mostrar_matriz(C)
                self.procedimiento_text.setPlainText(texto)

            elif op == "Gauss":
                pasos, A_escalon, pivots = self.eliminacion_adelante(A)
                texto = "\n\n".join(pasos) + "\n\nMatriz resultante (escalonada):\n" + self.mostrar_matriz(A_escalon)
                texto += "\n\nDiagnóstico:\n" + self.analizar_sistema(A_escalon, pivots)
                self.procedimiento_text.setPlainText(texto)

            elif op == "Gauss-Jordan":
                pasos, A_rref, pivots = self.gauss_jordan(A)
                texto = "\n\n".join(pasos) + "\n\nMatriz resultante (RREF):\n" + self.mostrar_matriz(A_rref)
                texto += "\n\nDiagnóstico:\n" + self.analizar_sistema(A_rref, pivots)
                self.procedimiento_text.setPlainText(texto)

        except Exception as e:
            self.procedimiento_text.setPlainText(f"Error al realizar la operación: {str(e)}")

# =================== EJECUCIÓN ===================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaMatrices()
    ventana.show()
    sys.exit(app.exec())
