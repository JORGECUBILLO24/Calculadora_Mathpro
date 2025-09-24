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

        # --- Fila y columna ---
        input_layout = QHBoxLayout()
        filas_label = QLabel("Filas"); filas_label.setFont(font_label); filas_label.setStyleSheet("color: #000000;")
        self.filas_input = QLineEdit("3"); self.filas_input.setFixedWidth(60); self.filas_input.setFont(font_input)
        columnas_label = QLabel("Columnas"); columnas_label.setFont(font_label); columnas_label.setStyleSheet("color: #000000;")
        self.columnas_input = QLineEdit("3"); self.columnas_input.setFixedWidth(60); self.columnas_input.setFont(font_input)

        input_layout.addWidget(filas_label)
        input_layout.addWidget(self.filas_input)
        input_layout.addSpacing(20)
        input_layout.addWidget(columnas_label)
        input_layout.addWidget(self.columnas_input)
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
        self.filas_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_input.editingFinished.connect(self.actualizar_dimensiones)
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
            filas = int(self.filas_input.text())
            cols = int(self.columnas_input.text())
            if filas <= 0 or cols <= 0: return
            for tabla in (self.tabla_A, self.tabla_B):
                tabla.setRowCount(filas)
                tabla.setColumnCount(cols)
                tabla.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cols)])
                tabla.setVerticalHeaderLabels([f"F{i+1}" for i in range(filas)])
                
                # <-- Agrega estas líneas para hacer las celdas más grandes:
            tabla.horizontalHeader().setDefaultSectionSize(80)
            tabla.verticalHeader().setDefaultSectionSize(60)
            for j in range(cols):
                tabla.setColumnWidth(j, 80)
        except:
            return

    def toggle_matrizB(self):
        """Oculta Matriz B si la operación es Gauss/Gauss-Jordan"""
        if self.operacion_combo.currentText() in ["Gauss", "Gauss-Jordan"]:
            self.tabla_B.hide()
        else:
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
    def forward_elim(self, M):
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

    def back_elim(self, M, pivots):
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
        pasos_fwd, A, pivots = self.forward_elim(M)
        pasos_back, A_rref = self.back_elim(A, pivots)
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
                self.procedimiento_text.setPlainText("A + B =\n" + self.mostrar_matriz(C))

            elif op == "Resta":
                if len(A) != len(B) or len(A[0]) != len(B[0]):
                    self.procedimiento_text.setPlainText("Error: A y B deben tener mismas dimensiones.")
                    return
                C = [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                self.procedimiento_text.setPlainText("A - B =\n" + self.mostrar_matriz(C))

            elif op == "Multiplicacion":
                if len(A[0]) != len(B):
                    self.procedimiento_text.setPlainText("Error: columnas(A) ≠ filas(B).")
                    return
                C = [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
                self.procedimiento_text.setPlainText("A × B =\n" + self.mostrar_matriz(C))

            elif op == "Gauss":
                pasos, A_escalon, pivots = self.forward_elim(A)
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
