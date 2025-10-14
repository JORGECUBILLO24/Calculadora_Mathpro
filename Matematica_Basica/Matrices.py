from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QApplication,
    QSizePolicy, QHeaderView
)
from PyQt6.QtGui import QFont, QTextCursor
    # QCheckBox eliminado
from PyQt6.QtCore import Qt, QTimer
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
        input_layout.setSpacing(20)

        # Matriz A
        self.a_widget = QWidget()
        a_layout = QVBoxLayout(self.a_widget)
        a_label = QLabel("Matriz A")
        a_label.setFont(font_label)
        a_label.setStyleSheet("color: #000000;")
        a_layout.addWidget(a_label)
        filas_a_layout = QHBoxLayout()
        filas_a_label = QLabel("Filas")
        filas_a_label.setFont(QFont("Segoe UI", 12))
        filas_a_label.setFixedWidth(70)
        self.filas_A_input = QLineEdit("3")
        self.filas_A_input.setFixedWidth(60)
        self.filas_A_input.setFont(font_input)
        filas_a_layout.addWidget(filas_a_label)
        filas_a_layout.addWidget(self.filas_A_input)
        a_layout.addLayout(filas_a_layout)
        columnas_a_layout = QHBoxLayout()
        columnas_a_label = QLabel("Columnas")
        columnas_a_label.setFont(QFont("Segoe UI", 12))
        columnas_a_label.setFixedWidth(70)
        self.columnas_A_input = QLineEdit("3")
        self.columnas_A_input.setFixedWidth(60)
        self.columnas_A_input.setFont(font_input)
        columnas_a_layout.addWidget(columnas_a_label)
        columnas_a_layout.addWidget(self.columnas_A_input)
        a_layout.addLayout(columnas_a_layout)

        # Matriz B
        self.b_widget = QWidget()
        b_layout = QVBoxLayout(self.b_widget)
        b_label = QLabel("Matriz B")
        b_label.setFont(font_label)
        b_label.setStyleSheet("color: #000000;")
        b_layout.addWidget(b_label)
        filas_b_layout = QHBoxLayout()
        filas_b_label = QLabel("Filas")
        filas_b_label.setFont(QFont("Segoe UI", 12))
        filas_b_label.setFixedWidth(70)
        self.filas_B_input = QLineEdit("3")
        self.filas_B_input.setFixedWidth(60)
        self.filas_B_input.setFont(font_input)
        filas_b_layout.addWidget(filas_b_label)
        filas_b_layout.addWidget(self.filas_B_input)
        b_layout.addLayout(filas_b_layout)
        columnas_b_layout = QHBoxLayout()
        columnas_b_label = QLabel("Columnas")
        columnas_b_label.setFont(QFont("Segoe UI", 12))
        columnas_b_label.setFixedWidth(70)
        self.columnas_B_input = QLineEdit("3")
        self.columnas_B_input.setFixedWidth(60)
        self.columnas_B_input.setFont(font_input)
        columnas_b_layout.addWidget(columnas_b_label)
        columnas_b_layout.addWidget(self.columnas_B_input)
        b_layout.addLayout(columnas_b_layout)

        # Añadir con stretch para que A y B se distribuyan proporcionalmente
        self.a_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.b_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        input_layout.addWidget(self.a_widget, 1)
        input_layout.addWidget(self.b_widget, 1)

        # --- Matriz A y B ---
        matrices_layout = QHBoxLayout()
        matrices_layout.setSpacing(12)
        self.tabla_A = QTableWidget()
        self.config_tabla(self.tabla_A, "Matriz A")
        self.tabla_B = QTableWidget()
        self.config_tabla(self.tabla_B, "Matriz B")
        matrices_layout.addWidget(self.tabla_A, 1)
        matrices_layout.addWidget(self.tabla_B, 1)

        # --- Botones / Operaciones ---
        controles_top = QHBoxLayout()
        controles_top.setContentsMargins(0, 10, 0, 0)
        controles_top.setSpacing(12)

        self.operacion_combo = QComboBox()
        self.operacion_combo.addItems(["Suma", "Resta", "Multiplicacion", "Traspuesta", "Gauss", "Gauss-Jordan"])
        self.operacion_combo.setFont(font_input)
        self.operacion_combo.setFixedWidth(240)
        self.operacion_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.operacion_combo.setStyleSheet("background-color:#1E88E5; color:white; border-radius:12px; padding:6px;")

        # (Checkbox eliminado: todo será automático)

        # Botones ejecutar / limpiar
        self.btn_limpiar = QPushButton("Limpiar matrices")
        self.btn_limpiar.setFont(font_btn)
        self.btn_limpiar.setStyleSheet("background-color:#E53935; color:white; border-radius:12px; padding:8px;")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.setMinimumHeight(40)
        self.btn_limpiar.setFixedWidth(180)

        self.btn_ejecutar = QPushButton("Ejecutar operación")
        self.btn_ejecutar.setFont(font_btn)
        self.btn_ejecutar.setStyleSheet("background-color:#43A047; color:white; border-radius:12px; padding:8px;")
        self.btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ejecutar.setMinimumHeight(40)
        self.btn_ejecutar.setFixedWidth(220)

        # Distribución superior
        controles_top.addWidget(self.operacion_combo, 0)
        controles_top.addStretch(1)
        controles_top.addWidget(self.btn_limpiar, 0)
        controles_top.addWidget(self.btn_ejecutar, 0)

        # --- Procedimiento ---
        self.procedimiento_text = QTextEdit()
        self.procedimiento_text.setFont(QFont("Consolas", 11))
        self.procedimiento_text.setPlaceholderText("Procedimiento")
        self.procedimiento_text.setMinimumHeight(250)
        self.procedimiento_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.procedimiento_text.setStyleSheet("background-color:white; color: #000000; border:2px solid #B0BEC5; border-radius:12px;")

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addLayout(input_layout)
        layout.addLayout(matrices_layout)
        layout.addLayout(controles_top)
        layout.addWidget(self.procedimiento_text, 1)
        self.setLayout(layout)

        # Conexiones
        self.btn_ejecutar.clicked.connect(self.ejecutar_operacion)
        self.btn_limpiar.clicked.connect(self.limpiar_matrices)
        self.filas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.filas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.operacion_combo.currentTextChanged.connect(self.toggle_matrizB)

        # Inicialización
        self.actualizar_dimensiones()
        self.toggle_matrizB()

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
        tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.verticalHeader().setDefaultSectionSize(60)
        self._rellenar_celdas_con_ceros(tabla)

    def _rellenar_celdas_con_ceros(self, tabla):
        filas, cols = tabla.rowCount(), tabla.columnCount()
        for i in range(filas):
            for j in range(cols):
                item = tabla.item(i, j)
                if item is None:
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tabla.setItem(i, j, item)

    def actualizar_dimensiones(self):
        try:
            filas_A = int(self.filas_A_input.text())
            cols_A = int(self.columnas_A_input.text())
            filas_B = int(self.filas_B_input.text())
            cols_B = int(self.columnas_B_input.text())
            if filas_A <= 0 or cols_A <= 0 or filas_B <= 0 or cols_B <= 0: 
                return

            # tabla_A
            self.tabla_A.setRowCount(filas_A)
            self.tabla_A.setColumnCount(cols_A)
            self.tabla_A.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cols_A)])
            self.tabla_A.setVerticalHeaderLabels([f"F{i+1}" for i in range(filas_A)])
            self.tabla_A.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.tabla_A.verticalHeader().setDefaultSectionSize(60)
            self._rellenar_celdas_con_ceros(self.tabla_A)

            # tabla_B
            self.tabla_B.setRowCount(filas_B)
            self.tabla_B.setColumnCount(cols_B)
            self.tabla_B.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cols_B)])
            self.tabla_B.setVerticalHeaderLabels([f"F{i+1}" for i in range(filas_B)])
            self.tabla_B.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.tabla_B.verticalHeader().setDefaultSectionSize(60)
            self._rellenar_celdas_con_ceros(self.tabla_B)
        finally:
            self.toggle_matrizB()

    def toggle_matrizB(self):
        """Oculta Matriz B si la operación es Gauss/Gauss-Jordan o Traspuesta."""
        if self.operacion_combo.currentText() in ["Gauss", "Gauss-Jordan", "Traspuesta"]:
            self.b_widget.hide()
            self.tabla_B.hide()
        else:
            self.b_widget.show()
            self.tabla_B.show()

    def mostrar_procedimiento(self, texto: str):
        self.procedimiento_text.setPlainText(texto)
        def _scroll_to_end():
            try:
                cursor = self.procedimiento_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.procedimiento_text.setTextCursor(cursor)
                self.procedimiento_text.ensureCursorVisible()
                sb = self.procedimiento_text.verticalScrollBar()
                sb.setValue(sb.maximum())
            except Exception:
                pass
        QTimer.singleShot(50, _scroll_to_end)
        QTimer.singleShot(200, _scroll_to_end)

    # =================== UTILIDADES ===================
    def leer_tabla(self, tabla):
        """Devuelve matriz de Fractions. Acepta '3', '1/2', '2.5' y '2,5'."""
        filas, cols = tabla.rowCount(), tabla.columnCount()
        matriz = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                item = tabla.item(i, j)
                val = item.text().strip() if item and item.text() else "0"
                try:
                    val_norm = val.replace(",", ".")
                    fila.append(Fraction(val_norm))
                except Exception:
                    fila.append(Fraction(0))
            matriz.append(fila)
        return matriz

    def mostrar_matriz(self, M):
        def fmt(x: Fraction):
            return str(x.numerator) if x.denominator == 1 else str(x)
        texto = ""
        for fila in M:
            texto += "[ " + "  ".join(fmt(x) for x in fila) + " ]\n"
        return texto

    def limpiar_matrices(self):
        try:
            for tabla in (self.tabla_A, self.tabla_B):
                filas, cols = tabla.rowCount(), tabla.columnCount()
                for i in range(filas):
                    for j in range(cols):
                        item = tabla.item(i, j)
                        if item is None:
                            item = QTableWidgetItem("0")
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            tabla.setItem(i, j, item)
                        else:
                            item.setText("0")
        except Exception:
            pass
        try:
            self.procedimiento_text.clear()
        except Exception:
            pass

    # =================== GAUSS & GAUSS-JORDAN ===================
    def eliminacion_adelante(self, M, has_rhs=True):
        """
        Eliminación hacia adelante. Si has_rhs=True, no pivotea la última columna (b).
        Si has_rhs=False, pivotea todas las columnas.
        """
        pasos = []
        A = copy.deepcopy(M)
        n, m = len(A), len(A[0])
        row = 0
        pivots = []

        last_col = m - 1 if has_rhs else m

        for col in range(last_col):
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

            pivot = A[row][col]
            if pivot != 1:
                A[row] = [x / pivot for x in A[row]]
                pasos.append(f"F{row+1} ÷ ({pivot})\n{self.mostrar_matriz(A)}")

            for r in range(row + 1, n):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor * A[row][j] for j in range(m)]
                    pasos.append(f"F{r+1} → F{r+1} - ({factor})·F{row+1}\n{self.mostrar_matriz(A)}")

            pivots.append(col)
            row += 1
            if row == n:
                break

        return pasos, A, pivots

    def eliminacionPivote(self, M, pivots):
        pasos = []
        A = copy.deepcopy(M)
        n, m = len(A), len(A[0])

        for pr in reversed(range(len(pivots))):
            col = pivots[pr]
            piv = A[pr][col]
            if piv != 0 and piv != 1:
                A[pr] = [x / piv for x in A[pr]]
                pasos.append(f"F{pr+1} ÷ ({piv})\n{self.mostrar_matriz(A)}")

            for r in range(pr):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor * A[pr][j] for j in range(m)]
                    pasos.append(f"F{r+1} → F{r+1} - ({factor})·F{pr+1}\n{self.mostrar_matriz(A)}")

        return pasos, A

    def analizar_sistema(self, A, pivots, has_rhs=True):
        """
        - has_rhs=True  -> Ax=b (usa última columna como b)
        - has_rhs=False -> sin término independiente (Ax=0 / análisis de columnas)
        """
        n, m = len(A), len(A[0])

        # ---- Caso sin término independiente ----
        if not has_rhs:
            NV = m
            pivots_from_A = []
            for r in range(n):
                for c in range(NV):
                    if A[r][c] != 0:
                        if c not in pivots_from_A:
                            pivots_from_A.append(c)
                        break
            libres = [i for i in range(NV) if i not in pivots_from_A]

            texto = "RREF sin término independiente (Ax=0 / análisis de columnas).\n"
            texto += f"Rango(A) = {len(pivots_from_A)}\n"
            texto += "Columnas pivote: " + (", ".join(f"C{c+1}" for c in pivots_from_A) if pivots_from_A else "Ninguna") + "\n"
            texto += "Columnas libres: " + (", ".join(f"C{l+1}" for l in libres) if libres else "Ninguna") + "\n"
            texto += "Conclusión: " + ("Las columnas son INDEPENDIENTES.\n" if len(pivots_from_A) == NV else "Las columnas son DEPENDIENTES.\n")
            return texto

        # ---- Con término independiente: Ax=b ----
        if m < 2:
            return "⚠️ Matriz inválida para análisis (no hay columna RHS)."
        NV = m - 1

        # Inconsistente: [0 ... 0 | b≠0]
        for r in range(n):
            if all(A[r][c] == 0 for c in range(NV)) and A[r][-1] != 0:
                return "⚠️ Sistema INCONSISTENTE → No tiene solución."

        # Pivotes detectados de la RREF (por si difieren de la lista recibida)
        pivots_from_A = []
        for r in range(n):
            for c in range(NV):
                if A[r][c] != 0:
                    if c not in pivots_from_A:
                        pivots_from_A.append(c)
                    break
        pivots_used = pivots_from_A if pivots_from_A else pivots

        libres = [i for i in range(NV) if i not in pivots_used]

        # Mapeo col pivote -> fila
        pivot_col_to_row = {}
        for r in range(n):
            for c in range(NV):
                if A[r][c] != 0:
                    if c not in pivot_col_to_row:
                        pivot_col_to_row[c] = r
                    break

        # Sin pivotes
        if len(pivots_used) == 0:
            if NV == 0:
                return "✅ Sistema CONSISTENTE → Sin variables (trivial)."
            texto = "✅ Sistema CONSISTENTE → Infinitas soluciones.\n"
            texto += "Tipo: Sistema COMPATIBLE DEPENDIENTE\n"
            texto += "Variables libres: " + ", ".join(f"x{i+1}" for i in libres) + "\n"
            texto += "Solución paramétrica:\n"
            for i in range(NV):
                texto += f"x{i+1} = variable libre\n"
            return texto

        # Helper
        def fmt_val(v: Fraction):
            return str(v.numerator) if v.denominator == 1 else str(v)

        # Con variables libres: imprime "xk = variable libre" y usa t1, t2,… en pivotes
        if libres:
            lines = []
            free_to_t = {l: idx + 1 for idx, l in enumerate(libres)}

            for i in range(NV):
                if i in libres:
                    # tal como pediste:
                    lines.append(f"x{i+1} = variable libre")
                else:
                    row = pivot_col_to_row.get(i)
                    if row is None:
                        lines.append(f"x{i+1} = ?")
                        continue
                    rhs = A[row][-1]
                    expr = fmt_val(rhs)
                    for l in libres:
                        coef = A[row][l]
                        if coef != 0:
                            t_idx = free_to_t[l]
                            coef_abs = abs(coef)
                            coef_str = fmt_val(coef_abs)
                            # x_pivote = rhs - sum(coef*tl)
                            expr += f" {'-' if coef > 0 else '+'} {coef_str}·t{t_idx}"
                    lines.append(f"x{i+1} = {expr}")

            texto = "✅ Sistema CONSISTENTE → Infinitas soluciones.\n"
            texto += "Tipo: Sistema COMPATIBLE DEPENDIENTE\n"
            texto += "Variables libres: " + ", ".join(f"x{i+1}" for i in libres) + "\n"
            texto += "Solución paramétrica:\n" + "\n".join(lines)
            return texto

        # Sin variables libres: solución única
        soluciones = [None] * NV
        for c in pivots_used:
            r = pivot_col_to_row.get(c)
            if r is not None:
                soluciones[c] = A[r][-1]

        texto = "✅ Sistema CONSISTENTE → Solución única.\n"
        texto += "Tipo: Sistema COMPATIBLE INDEPENDIENTE\n"
        texto += "Solución:\n"
        for i in range(NV):
            val = soluciones[i]
            texto += f"x{i+1} = {fmt_val(val) if val is not None else '0'}\n"
        return texto

    def gauss_jordan(self, M, has_rhs=True):
        pasos_fwd, A_mid, pivots = self.eliminacion_adelante(M, has_rhs=has_rhs)
        pasos_back, A_rref = self.eliminacionPivote(A_mid, pivots)
        pasos = pasos_fwd + pasos_back
        return pasos, A_rref, pivots

    # =================== OPERACIONES ===================
    def ejecutar_operacion(self):
        op = self.operacion_combo.currentText()
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B) if self.tabla_B.isVisible() else None

        # Detección AUTOMÁTICA de Ax=b: solo en Gauss/Gauss-Jordan y si hay ≥2 columnas
        has_rhs = (op in ["Gauss", "Gauss-Jordan"]) and (len(A[0]) >= 2)

        try:
            if op == "Suma":
                if B is None:
                    self.mostrar_procedimiento("Error: Matriz B requerida para la suma.")
                    return
                if len(A) != len(B) or len(A[0]) != len(B[0]):
                    self.mostrar_procedimiento("Error: A y B deben tener mismas dimensiones.")
                    return
                C = [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\nMatriz B:\n" + self.mostrar_matriz(B) + "\nPasos de la suma:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += f"Elemento ({i+1},{j+1}): {A[i][j]} + {B[i][j]} = {C[i][j]}\n"
                texto += "\nResultado A + B:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(texto)

            elif op == "Resta":
                if B is None:
                    self.mostrar_procedimiento("Error: Matriz B requerida para la resta.")
                    return
                if len(A) != len(B) or len(A[0]) != len(B[0]):
                    self.mostrar_procedimiento("Error: A y B deben tener mismas dimensiones.")
                    return
                C = [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\nMatriz B:\n" + self.mostrar_matriz(B) + "\nPasos de la resta:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        texto += f"Elemento ({i+1},{j+1}): {A[i][j]} - {B[i][j]} = {C[i][j]}\n"
                texto += "\nResultado A - B:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(texto)

            elif op == "Multiplicacion":
                if B is None:
                    self.mostrar_procedimiento("Error: Matriz B requerida para la multiplicación.")
                    return
                if len(A[0]) != len(B):
                    self.mostrar_procedimiento("Error: columnas(A) ≠ filas(B).")
                    return
                C = [[sum(A[i][k]*B[k][j] for k in range(len(A[0]))) for j in range(len(B[0]))] for i in range(len(A))]
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\nMatriz B:\n" + self.mostrar_matriz(B) + "\nPasos de la multiplicación:\n"
                for i in range(len(A)):
                    for j in range(len(B[0])):
                        values = [f"{A[i][k]}*{B[k][j]}" for k in range(len(B))]
                        sum_str = " + ".join(values)
                        result = sum(A[i][k] * B[k][j] for k in range(len(B)))
                        texto += f"Elemento ({i+1},{j+1}): {sum_str} = {result}\n"
                texto += "\nResultado A × B:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(texto)

            elif op == "Traspuesta":
                if not A or not A[0]:
                    self.mostrar_procedimiento("Error: Matriz A vacía o inválida para trasponer.")
                    return
                filas = len(A)
                cols = len(A[0])
                T = [[A[i][j] for i in range(filas)] for j in range(cols)]
                texto = "Matriz A:\n" + self.mostrar_matriz(A)
                texto += "\nPasos de la traspuesta:\n"
                for i in range(filas):
                    for j in range(cols):
                        texto += f"A({i+1},{j+1}) → T({j+1},{i+1}) = {A[i][j]}\n"
                texto += "\nResultado A^T:\n" + self.mostrar_matriz(T)
                self.mostrar_procedimiento(texto)

            elif op == "Gauss":
                pasos, A_escalon, pivots = self.eliminacion_adelante(A, has_rhs=has_rhs)
                _, A_rref = self.eliminacionPivote(A_escalon, pivots)
                texto = "\n\n".join(pasos) + "\n\nMatriz resultante (escalonada):\n" + self.mostrar_matriz(A_escalon)
                texto += "\n\nDiagnóstico:\n" + self.analizar_sistema(A_rref, pivots, has_rhs=has_rhs)
                self.mostrar_procedimiento(texto)

            elif op == "Gauss-Jordan":
                pasos, A_rref, pivots = self.gauss_jordan(A, has_rhs=has_rhs)
                texto = "\n\n".join(pasos) + "\n\nMatriz resultante (RREF):\n" + self.mostrar_matriz(A_rref)
                texto += "\n\nDiagnóstico:\n" + self.analizar_sistema(A_rref, pivots, has_rhs=has_rhs)
                self.mostrar_procedimiento(texto)

        except Exception as e:
            self.mostrar_procedimiento(f"Error al realizar la operación: {str(e)}")


