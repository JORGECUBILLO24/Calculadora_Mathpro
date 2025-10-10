from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QApplication,
    QSizePolicy, QHeaderView
)
from PyQt6.QtGui import QFont, QTextCursor
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
        # Añadir con stretch para que ambas tablas ocupen el mismo espacio disponible
        matrices_layout.addWidget(self.tabla_A, 1)
        matrices_layout.addWidget(self.tabla_B, 1)

        # --- Botones ---
        botones_layout = QHBoxLayout()
        botones_layout.setContentsMargins(0, 10, 0, 10)
        botones_layout.setSpacing(10)
        self.operacion_combo = QComboBox()
        self.operacion_combo.addItems(["Suma", "Resta", "Multiplicacion", "Traspuesta", "Gauss", "Gauss-Jordan"])
        self.operacion_combo.setFont(font_input)
        self.operacion_combo.setFixedWidth(240)
        self.operacion_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.operacion_combo.setStyleSheet("background-color:#1E88E5; color:white; border-radius:12px; padding:6px;")

        self.btn_ejecutar = QPushButton("Ejecutar operación")
        self.btn_ejecutar.setFont(font_btn)
        self.btn_ejecutar.setStyleSheet("background-color:#43A047; color:white; border-radius:12px; padding:8px;")
        self.btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ejecutar.setMinimumHeight(40)
        self.btn_ejecutar.setFixedWidth(220)
        # Botón para limpiar matrices y procedimiento
        self.btn_limpiar = QPushButton("Limpiar matrices")
        self.btn_limpiar.setFont(font_btn)
        self.btn_limpiar.setStyleSheet("background-color:#E53935; color:white; border-radius:12px; padding:8px;")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.setMinimumHeight(40)
        self.btn_limpiar.setFixedWidth(180)

        # Distribuir: combo al inicio y boton al final con espacio flexible
        botones_layout.addWidget(self.operacion_combo, 0)
        botones_layout.addStretch(1)
        botones_layout.addWidget(self.btn_limpiar, 0)
        botones_layout.addWidget(self.btn_ejecutar, 0)

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
        layout.addLayout(botones_layout)
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

        # Inicializar tablas con las dimensiones por defecto y estado de B
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
        # Preferir que las columnas se estiren para usar el espacio disponible
        tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.verticalHeader().setDefaultSectionSize(60)    # Alto de filas

        # Rellenar con items "0" centrados
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
            if filas_A <= 0 or cols_A <= 0 or filas_B <= 0 or cols_B <= 0: return

            # For tabla_A
            self.tabla_A.setRowCount(filas_A)
            self.tabla_A.setColumnCount(cols_A)
            self.tabla_A.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cols_A)])
            self.tabla_A.setVerticalHeaderLabels([f"F{i+1}" for i in range(filas_A)])
            # Hacer que las columnas se estiren automáticamente
            self.tabla_A.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.tabla_A.verticalHeader().setDefaultSectionSize(60)
            self._rellenar_celdas_con_ceros(self.tabla_A)

            # For tabla_B
            self.tabla_B.setRowCount(filas_B)
            self.tabla_B.setColumnCount(cols_B)
            self.tabla_B.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cols_B)])
            self.tabla_B.setVerticalHeaderLabels([f"F{i+1}" for i in range(filas_B)])
            # Hacer que las columnas se estiren automáticamente
            self.tabla_B.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.tabla_B.verticalHeader().setDefaultSectionSize(60)
            self._rellenar_celdas_con_ceros(self.tabla_B)

        except Exception:
            return

    def toggle_matrizB(self):
        """Oculta Matriz B si la operación es Gauss/Gauss-Jordan"""
        # Ocultar Matriz B para operaciones que solo requieren una matriz
        if self.operacion_combo.currentText() in ["Gauss", "Gauss-Jordan", "Traspuesta"]:
            self.b_widget.hide()
            self.tabla_B.hide()
        else:
            self.b_widget.show()
            self.tabla_B.show()

    def mostrar_procedimiento(self, texto: str):
        """Setea el texto del procedimiento y fuerza el scroll al final de forma confiable.

        Usa un pequeño retraso (QTimer.singleShot) para ejecutar el desplazamiento después
        de que Qt haya hecho el repaint y calculado los tamaños del widget.
        """
        # Actualizar el texto inmediatamente
        self.procedimiento_text.setPlainText(texto)

        # Callback que mueve el cursor al final y fuerza a que la barra esté al máximo
        def _scroll_to_end():
            try:
                cursor = self.procedimiento_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.procedimiento_text.setTextCursor(cursor)
                self.procedimiento_text.ensureCursorVisible()
                # Fallback adicional: forzar el scrollbar vertical al máximo
                sb = self.procedimiento_text.verticalScrollBar()
                sb.setValue(sb.maximum())
            except Exception:
                pass

        # Usar pequeños delays para dar tiempo al layout; intentos a 50ms y 200ms
        QTimer.singleShot(50, _scroll_to_end)
        QTimer.singleShot(200, _scroll_to_end)

    # =================== UTILIDADES ===================
    def leer_tabla(self, tabla):
        filas, cols = tabla.rowCount(), tabla.columnCount()
        matriz = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                item = tabla.item(i, j)
                val = item.text().strip() if item and item.text() else "0"
                try:
                    # Acepta formas: "3", "1/2", "2.5"
                    fila.append(Fraction(val))
                except Exception:
                    # Si no se puede convertir, poner 0
                    fila.append(Fraction(0))
            matriz.append(fila)
        return matriz

    def mostrar_matriz(self, M):
        def fmt(x: Fraction):
            if x.denominator == 1:
                return str(x.numerator)
            return str(x)  # muestra como 'a/b'
        texto = ""
        for fila in M:
            texto += "[ " + "  ".join(fmt(x) for x in fila) + " ]\n"
        return texto

    def limpiar_matrices(self):
        """Pone todas las celdas de las tablas en '0' y limpia el área de procedimiento."""
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

        # Limpiar procedimiento
        try:
            self.procedimiento_text.clear()
        except Exception:
            pass

    # =================== GAUSS & GAUSS-JORDAN ===================
    def eliminacion_adelante(self, M):
        pasos = []
        A = copy.deepcopy(M)
        n, m = len(A), len(A[0])
        row = 0
        pivots = []

        # iterar columnas (si se supone último col es RHS, iterar hasta m-1)
        for col in range(m - 1):  # si no es sistema con RHS, ajustar externamente
            # seleccionar pivote (primer fila no nula en o debajo de 'row')
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
            # normalizar pivote a 1 (si se desea). Conservamos la normalización para RREF
            pivot = A[row][col]
            if pivot != 1:
                # dividir toda la fila por pivot (si pivot=0 ya filtrado)
                A[row] = [x / pivot for x in A[row]]
                pasos.append(f"F{row+1} ÷ ({pivot})\n{self.mostrar_matriz(A)}")
            # eliminar debajo
            for r in range(row+1, n):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor*A[row][j] for j in range(m)]
                    pasos.append(f"F{r+1} → F{r+1} - ({factor})·F{row+1}\n{self.mostrar_matriz(A)}")
            pivots.append(col)
            row += 1
            if row == n:
                break
        return pasos, A, pivots

    def eliminacionPivote(self, M, pivots):
        """
        Elimina hacia arriba para obtener RREF. pivots es la lista de índices de columna
        donde se encontraron pivotes; el orden de pivots corresponde a las filas
        0..len(pivots)-1 después de la eliminación hacia adelante.
        """
        pasos = []
        A = copy.deepcopy(M)
        n, m = len(A), len(A[0])

        # Recorrer pivotes desde el último pivot-row hacia el primero
        for pr in reversed(range(len(pivots))):
            col = pivots[pr]  # columna del pivot correspondiente a la fila 'pr'
            # eliminar términos por encima de la fila pr
            for r in range(pr):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor*A[pr][j] for j in range(m)]
                    pasos.append(f"F{r+1} → F{r+1} - ({factor})·F{pr+1}\n{self.mostrar_matriz(A)}")
        return pasos, A

    def analizar_sistema(self, A, pivots):
        n, m = len(A), len(A[0])

        # Se asume que la última columna es el término independiente (RHS)
        if m < 2:
            return "⚠️ Matriz inválida para análisis (no hay columna RHS)."
        NV = m - 1

        # revisar inconsistencia: fila con todos coeficientes 0 y RHS distinto de 0
        for r in range(n):
            if all(A[r][c] == 0 for c in range(NV)) and A[r][-1] != 0:
                return "⚠️ Sistema INCONSISTENTE → No tiene solución."

        # Recalcular pivotes a partir de la matriz A (útil si A ya es RREF)
        pivots_from_A = []
        for r in range(n):
            for c in range(NV):
                if A[r][c] != 0:
                    if c not in pivots_from_A:
                        pivots_from_A.append(c)
                    break

        # Usar pivotes detectados en A si hay, si no usar la lista pasada
        pivots_used = pivots_from_A if pivots_from_A else pivots

        # variables libres: índices de columnas que no son pivote
        libres = [i for i in range(NV) if i not in pivots_used]

        # Construir un mapeo columna_pivot -> fila donde aparece (si es RREF debería ser exacto)
        pivot_col_to_row = {}
        for r in range(n):
            for c in range(NV):
                if A[r][c] != 0:
                    # tomamos la primera entrada no nula como pivot para esa fila
                    if c not in pivot_col_to_row:
                        pivot_col_to_row[c] = r
                    break

        # Caso: no hay pivotes -> todas las variables son libres
        if len(pivots_used) == 0:
            if NV == 0:
                return "✅ Sistema CONSISTENTE → Sin variables (trivial)."
            texto = "✅ Sistema CONSISTENTE → Infinitas soluciones.\n"
            texto += "Tipo: Sistema  DEPENDIENTE\n"
            texto += "Variables libres: " + ", ".join(f"x{i+1}" for i in libres) + "\n"
            texto += "Solución paramétrica:\n"
            for i in range(NV):
                texto += f"x{i+1} = Libre\n"
            return texto

        # Caso: si hay variables libres, construir solución paramétrica mostrando 'Libre' para ellas
        if libres:
            # mapear cada variable (por orden) a una expresión o a 'Libre'
            lines = []
            # crear índices para parámetros t1, t2, ... (aunque no los mostramos como x = t, los usamos en expresiones)
            free_to_t = {l: idx+1 for idx, l in enumerate(libres)}

            for i in range(NV):
                if i in libres:
                    lines.append(f"x{i+1} = Libre")
                else:
                    # variable pivote: encontrar fila correspondiente
                    row = pivot_col_to_row.get(i)
                    if row is None:
                        # como fallback si no encontramos la fila, marcar como indefinida
                        lines.append(f"x{i+1} = ?")
                        continue
                    # rhs y construir expresión: x_pivot = rhs - sum(coef * t_k)
                    rhs = A[row][-1]
                    # formatear rhs (Fraction -> int si posible)
                    def fmt_val(v: Fraction):
                        return str(v.numerator) if v.denominator == 1 else str(v)

                    expr = fmt_val(rhs)
                    for l in libres:
                        coef = A[row][l]
                        if coef != 0:
                            t_idx = free_to_t[l]
                            # signo: x_pivot = rhs - coef*t  => si coef>0 mostramos ' - coef·t', si coef<0 mostramos ' + abs(coef)·t'
                            coef_abs = abs(coef)
                            coef_str = fmt_val(coef_abs)
                            if coef > 0:
                                expr += f" - {coef_str}·t{t_idx}"
                            else:
                                expr += f" + {coef_str}·t{t_idx}"
                    lines.append(f"x{i+1} = {expr}")

            texto = "✅ Sistema CONSISTENTE → Infinitas soluciones.\n"
            texto += "Tipo: Sistema  DEPENDIENTE\n"
            texto += "Variables libres: " + ", ".join(f"x{i+1}" for i in libres) + "\n"
            texto += "Solución paramétrica:\n" + "\n".join(lines)
            return texto

        # Caso: sin variables libres -> solución única (tomar RHS de filas correspondientes a pivotes)
        soluciones = [None] * NV
        for c in pivots_used:
            r = pivot_col_to_row.get(c)
            if r is not None:
                soluciones[c] = A[r][-1]
        # formatear soluciones
        def fmt_val(v: Fraction):
            return str(v.numerator) if v.denominator == 1 else str(v)

        texto = "✅ Sistema CONSISTENTE → Solución única.\n"
        texto += "Tipo: Sistema  INDEPENDIENTE\n"
        texto += "Solución:\n"
        for i in range(NV):
            val = soluciones[i]
            val_str = fmt_val(val) if val is not None else "0"
            texto += f"x{i+1} = {val_str}\n"
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
        # Si tabla_B está oculta, no la leemos (usualmente en Gauss/Gauss-Jordan)
        B = self.leer_tabla(self.tabla_B) if self.tabla_B.isVisible() else None

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
                        texto += f"Elemento ({i+1},{j+1}): A[{i+1}][{j+1}] + B[{i+1}][{j+1}] = {A[i][j]} + {B[i][j]} = {C[i][j]}\n"
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
                        texto += f"Elemento ({i+1},{j+1}): A[{i+1}][{j+1}] - B[{i+1}][{j+1}] = {A[i][j]} - {B[i][j]} = {C[i][j]}\n"
                texto += "\nResultado A - B:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(texto)

            elif op == "Multiplicacion":
                if B is None:
                    self.mostrar_procedimiento("Error: Matriz B requerida para la multiplicación.")
                    return
                if len(A[0]) != len(B):
                    self.mostrar_procedimiento("Error: columnas(A) ≠ filas(B).")
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
                self.mostrar_procedimiento(texto)

            elif op == "Traspuesta":
                # Trasponer la matriz A (no se usa B)
                if not A or not A[0]:
                    self.mostrar_procedimiento("Error: Matriz A vacía o inválida para trasponer.")
                    return
                filas = len(A)
                cols = len(A[0])
                # Construir traspuesta
                T = [[A[i][j] for i in range(filas)] for j in range(cols)]
                texto = "Matriz A:\n" + self.mostrar_matriz(A)
                texto += "\nPasos de la traspuesta:\n"
                for i in range(filas):
                    for j in range(cols):
                        texto += f"Elemento A({i+1},{j+1}) -> T({j+1},{i+1}) = {A[i][j]}\n"
                texto += "\nResultado A^T:\n" + self.mostrar_matriz(T)
                self.mostrar_procedimiento(texto)

            elif op == "Gauss":
                # Se asume que A corresponde a una matriz aumentada si hay RHS.
                pasos, A_escalon, pivots = self.eliminacion_adelante(A)
                # obtener RREF para diagnóstico más preciso (no añadimos estos pasos al log)
                _, A_rref = self.eliminacionPivote(A_escalon, pivots)
                texto = "\n\n".join(pasos) + "\n\nMatriz resultante (escalonada):\n" + self.mostrar_matriz(A_escalon)
                texto += "\n\nDiagnóstico:\n" + self.analizar_sistema(A_rref, pivots)
                self.mostrar_procedimiento(texto)

            elif op == "Gauss-Jordan":
                pasos, A_rref, pivots = self.gauss_jordan(A)
                texto = "\n\n".join(pasos) + "\n\nMatriz resultante (RREF):\n" + self.mostrar_matriz(A_rref)
                texto += "\n\nDiagnóstico:\n" + self.analizar_sistema(A_rref, pivots)
                self.mostrar_procedimiento(texto)

        except Exception as e:
            self.mostrar_procedimiento(f"Error al realizar la operación: {str(e)}")

