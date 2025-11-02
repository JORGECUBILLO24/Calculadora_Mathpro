from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QDialog,
    QPlainTextEdit, QSizePolicy, QHeaderView, QInputDialog
)
import re 

from PyQt6.QtGui import QFont, QTextCursor, QGuiApplication
from PyQt6.QtCore import Qt, QTimer
from fractions import Fraction
import copy


class VentanaMatrices(QWidget):
    """
    Operaciones con matrices:
      - Suma, Resta, Multiplicación (A × B), Traspuesta (A^T)
      - Gauss (forma escalonada con pivotes 1 y eliminación inferior)
      - Gauss-Jordan (RREF) + diagnóstico de sistema (consistente/inconsistente/infinitas)
      - Multiplicación por escalar (k × A)
      - Inversa (Gauss-Jordan sobre [A|I])
    Todas las operaciones muestran pasos claros en el panel de procedimiento.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:#F0F4F8; color:#000000;")
        self.setWindowTitle("Operaciones con Matrices")

        font_label = QFont("Segoe UI", 14, QFont.Weight.Bold)
        font_input = QFont("Segoe UI", 12)
        font_btn   = QFont("Segoe UI", 13, QFont.Weight.Bold)

        # --------- Panel dimensiones ---------
        input_layout = QHBoxLayout(); input_layout.setSpacing(20)
        corner = QHBoxLayout()
        corner.setContentsMargins(0, 0, 0, 0)
        corner.addStretch(1)

        self.btn_eq2mat = QPushButton("Ecuaciones → Matrices")
        self.btn_eq2mat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eq2mat.setFixedHeight(36)
        self.btn_eq2mat.setStyleSheet("background-color:#455A64; color:white; border-radius:12px; padding:6px;")
        self.btn_eq2mat.clicked.connect(self._abrir_convertidor_ecuaciones)

        corner.addWidget(self.btn_eq2mat, 0)
        root = QVBoxLayout(); root.setSpacing(12); root.setContentsMargins(12, 12, 12, 12)
        root.addLayout(corner)

        # Matriz A
        self.a_widget = QWidget()
        a_layout = QVBoxLayout(self.a_widget)
        a_label = QLabel("Matriz A"); a_label.setFont(font_label); a_layout.addWidget(a_label)

        filaA = QHBoxLayout()
        filaA.addWidget(QLabel("Filas")); self.filas_A_input = QLineEdit("3")
        self.filas_A_input.setFixedWidth(60); self.filas_A_input.setFont(font_input)
        filaA.addWidget(self.filas_A_input); a_layout.addLayout(filaA)

        colA = QHBoxLayout()
        colA.addWidget(QLabel("Columnas")); self.columnas_A_input = QLineEdit("3")
        self.columnas_A_input.setFixedWidth(60); self.columnas_A_input.setFont(font_input)
        colA.addWidget(self.columnas_A_input); a_layout.addLayout(colA)

        # Matriz B
        self.b_widget = QWidget()
        b_layout = QVBoxLayout(self.b_widget)
        b_label = QLabel("Matriz B"); b_label.setFont(font_label); b_layout.addWidget(b_label)

        filaB = QHBoxLayout()
        filaB.addWidget(QLabel("Filas")); self.filas_B_input = QLineEdit("3")
        self.filas_B_input.setFixedWidth(60); self.filas_B_input.setFont(font_input)
        filaB.addWidget(self.filas_B_input); b_layout.addLayout(filaB)

        colB = QHBoxLayout()
        colB.addWidget(QLabel("Columnas")); self.columnas_B_input = QLineEdit("3")
        self.columnas_B_input.setFixedWidth(60); self.columnas_B_input.setFont(font_input)
        colB.addWidget(self.columnas_B_input); b_layout.addLayout(colB)

        self.a_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.b_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        input_layout.addWidget(self.a_widget, 1)
        input_layout.addWidget(self.b_widget, 1)

        # --------- Tablas A y B ---------
        matrices_layout = QHBoxLayout(); matrices_layout.setSpacing(12)

        self.tabla_A = QTableWidget(); self._config_tabla(self.tabla_A, "Matriz A")
        self.tabla_B = QTableWidget(); self._config_tabla(self.tabla_B, "Matriz B")

        matrices_layout.addWidget(self.tabla_A, 1)
        matrices_layout.addWidget(self.tabla_B, 1)

        # --------- Barra de acciones ---------
        acciones = QHBoxLayout(); acciones.setContentsMargins(0, 10, 0, 10); acciones.setSpacing(10)

        self.operacion_combo = QComboBox()
        self.operacion_combo.addItems([
            "Suma", "Resta", "Multiplicacion",
            "Traspuesta", "Gauss", "Gauss-Jordan",
            "Inversa"
        ])
        self.operacion_combo.setFont(font_input)
        self.operacion_combo.setFixedWidth(260)
        self.operacion_combo.setStyleSheet("background-color:#1E88E5; color:white; border-radius:12px; padding:6px;")

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

        acciones.addWidget(self.operacion_combo, 0)
        acciones.addStretch(1)
        acciones.addWidget(self.btn_limpiar, 0)
        acciones.addWidget(self.btn_ejecutar, 0)

        # --------- Panel de procedimiento ---------
        self.procedimiento_text = QTextEdit()
        self.procedimiento_text.setFont(QFont("Consolas", 11))
        self.procedimiento_text.setPlaceholderText("Procedimiento")
        self.procedimiento_text.setMinimumHeight(260)
        self.procedimiento_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.procedimiento_text.setStyleSheet("background-color:white; color:#000; border:2px solid #B0BEC5; border-radius:12px;")

        # Layout principal
        root.addLayout(input_layout)
        root.addLayout(matrices_layout)
        root.addLayout(acciones)
        root.addWidget(self.procedimiento_text, 1)
        self.setLayout(root)

        # Conexiones
        self.btn_ejecutar.clicked.connect(self.ejecutar_operacion)
        self.btn_limpiar.clicked.connect(self.limpiar_matrices)
        self.filas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.filas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.operacion_combo.currentTextChanged.connect(self._toggle_matrizB)

        # Estado inicial
        self.actualizar_dimensiones()
        self._toggle_matrizB()

    # ---------------- Configuración de tablas ----------------
    def _config_tabla(self, tabla: QTableWidget, titulo: str):
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
        tabla.verticalHeader().setDefaultSectionSize(56)
        self._rellenar_ceros(tabla)

    def _rellenar_ceros(self, tabla: QTableWidget):
        for i in range(tabla.rowCount()):
            for j in range(tabla.columnCount()):
                if tabla.item(i, j) is None:
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tabla.setItem(i, j, it)

    def actualizar_dimensiones(self):
        try:
            fA = max(1, int(self.filas_A_input.text()))
            cA = max(1, int(self.columnas_A_input.text()))
            fB = max(1, int(self.filas_B_input.text()))
            cB = max(1, int(self.columnas_B_input.text()))
        except Exception:
            return
    

        # Tabla A
        self.tabla_A.setRowCount(fA); self.tabla_A.setColumnCount(cA)
        self.tabla_A.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cA)])
        self.tabla_A.setVerticalHeaderLabels([f"F{i+1}" for i in range(fA)])
        self.tabla_A.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._rellenar_ceros(self.tabla_A)

        # Tabla B
        self.tabla_B.setRowCount(fB); self.tabla_B.setColumnCount(cB)
        self.tabla_B.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cB)])
        self.tabla_B.setVerticalHeaderLabels([f"F{i+1}" for i in range(fB)])
        self.tabla_B.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._rellenar_ceros(self.tabla_B)

    def _toggle_matrizB(self):
        """Oculta Matriz B cuando la operación usa solo A."""
        solo_A = self.operacion_combo.currentText() in {
            "Gauss", "Gauss-Jordan", "Traspuesta", "Inversa"
        }
        self.b_widget.setVisible(not solo_A)
        self.tabla_B.setVisible(not solo_A)

    # ---------------- Utilidades ----------------
    def leer_tabla(self, tabla: QTableWidget):
        filas, cols = tabla.rowCount(), tabla.columnCount()
        M = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                it = tabla.item(i, j)
                s = it.text().strip() if it and it.text() else "0"
                try:
                    fila.append(Fraction(s))
                except Exception:
                    fila.append(Fraction(0))
            M.append(fila)
        return M

    def _fmt(self, x: Fraction) -> str:
        return str(x.numerator) if x.denominator == 1 else str(x)

    def mostrar_matriz(self, M):
        return "\n".join("[ " + "  ".join(self._fmt(x) for x in fila) + " ]" for fila in M)

    def mostrar_procedimiento(self, texto: str):
        self.procedimiento_text.setPlainText(texto)

        def _scroll():
            try:
                cur = self.procedimiento_text.textCursor()
                cur.movePosition(QTextCursor.MoveOperation.End)
                self.procedimiento_text.setTextCursor(cur)
                self.procedimiento_text.ensureCursorVisible()
                sb = self.procedimiento_text.verticalScrollBar()
                sb.setValue(sb.maximum())
            except Exception:
                pass

        QTimer.singleShot(30, _scroll)
        QTimer.singleShot(150, _scroll)

    def limpiar_matrices(self):
        # Restablecer todas las celdas a "0" y limpiar el panel de procedimiento
        for tabla in (self.tabla_A, self.tabla_B):
            for i in range(tabla.rowCount()):
                for j in range(tabla.columnCount()):
                    it = tabla.item(i, j)
                    if it is None:
                        it = QTableWidgetItem("0")
                        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        tabla.setItem(i, j, it)
                    else:
                        it.setText("0")
        self.procedimiento_text.clear()

    def _abrir_convertidor_ecuaciones(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Convertidor: Ecuación → Matriz")
        lay = QVBoxLayout(dlg)

        info = QLabel("Pega una ecuación por línea (variables x1, x2, x3, ...). "
                      "Ejemplos:\n"
                      "  2x1 - 3x2 + x3 = 7\n"
                      "  x1 + x3 = 2\n"
                      "Constantes sin variable también se aceptan (p.ej., +4).")
        info.setWordWrap(True)

        eq_edit = QTextEdit()
        eq_edit.setPlaceholderText("Ejemplo:\n2x1 - 3x2 + x3 = 7\nx1 + x3 = 2")
        eq_edit.setMinimumHeight(120)

        out_box = QPlainTextEdit()
        out_box.setReadOnly(True)
        out_box.setPlaceholderText("Matriz aumentada [A|b] aparecerá aquí...")

        btns = QHBoxLayout()
        btn_convertir = QPushButton("Convertir")
        btn_copiar = QPushButton("Copiar matriz")
        btn_cerrar = QPushButton("Cerrar")
        btns.addWidget(btn_convertir)
        btns.addStretch(1)
        btns.addWidget(btn_copiar)
        btns.addWidget(btn_cerrar)

        lay.addWidget(info)
        lay.addWidget(eq_edit)
        lay.addWidget(out_box)
        lay.addLayout(btns)

        def _convertir():
            try:
                A, b = self._ecuaciones_a_matriz(eq_edit.toPlainText())
                # Formato bonito [A | b]
                filas = ["[ " + "  ".join(self._fmt(c) for c in fila) + " | " + self._fmt(bb) + " ]"
                         for fila, bb in zip(A, b)]
                bonito = "Matriz aumentada [A|b]:\n" + "\n".join(filas)

                # Solo números (útil para pegar por filas)
                solo = "\n".join(" ".join(self._fmt(c) for c in (fila + [bb]))
                                 for fila, bb in zip(A, b))

                out_box.setPlainText(bonito + "\n\nSolo números (A|b):\n" + solo)
            except Exception as e:
                out_box.setPlainText(f"Error: {e}")

        def _copiar():
            QGuiApplication.clipboard().setText(out_box.toPlainText())

        btn_convertir.clicked.connect(_convertir)
        btn_copiar.clicked.connect(_copiar)
        btn_cerrar.clicked.connect(dlg.accept)

        dlg.resize(520, 460)
        dlg.exec()

    def _ecuaciones_a_matriz(self, texto: str):
        lineas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
        if not lineas:
            raise ValueError("No hay ecuaciones.")

        ecuaciones = []
        max_var = 0

        for ln in lineas:
            s = (ln.replace("−", "-")
                   .replace("—", "-")
                   .replace("·", "*")
                   .replace(" ", ""))
            if "=" in s:
                left, right = s.split("=", 1)
            else:
                left, right = s, "0"

            coefL, constL, mL = self._parse_expr_vars_y_const(left)
            coefR, constR, mR = self._parse_expr_vars_y_const(right)
            max_var = max(max_var, mL, mR)

            # Pasar todo a la izquierda: (coefL - coefR)·x = (constR - constL)
            coefs = {}
            for k in set(coefL) | set(coefR):
                coefs[k] = coefL.get(k, Fraction(0)) - coefR.get(k, Fraction(0))
            const = constR - constL
            ecuaciones.append((coefs, const))

        # Construir A y b
        A, b = [], []
        for coefs, const in ecuaciones:
            fila = [Fraction(0) for _ in range(max_var)]
            for k, v in coefs.items():
                if k <= 0:
                    raise ValueError("Las variables deben ser x1, x2, x3, ...")
                if k - 1 >= len(fila):
                    fila.extend([Fraction(0)] * (k - len(fila)))
                fila[k - 1] = v
            A.append(fila)
            b.append(const)

        return A, b

    def _parse_expr_vars_y_const(self, expr: str):
        s = expr
        var_pat = re.compile(r'([+\-]?)(\d+(?:/\d+)?)?\*?x(\d+)')
        coefs = {}
        max_var = 0
        spans = []

        # Capturar términos con variables
        for m in var_pat.finditer(s):
            sign = -1 if m.group(1) == '-' else 1
            coef = m.group(2)
            c = Fraction(coef) if coef else Fraction(1)
            idx = int(m.group(3))
            coefs[idx] = coefs.get(idx, Fraction(0)) + sign * c
            max_var = max(max_var, idx)
            spans.append((m.start(), m.end()))

        # Quitar los segmentos de variables y analizar constantes
        keep = []
        last = 0
        for a, b in spans:
            keep.append(s[last:a])
            last = b
        keep.append(s[last:])
        resto = ''.join(keep)

        const = Fraction(0)
        if resto:
            # constantes sueltas: +5, -3/2, 7, etc.
            for sign, num in re.findall(r'([+\-]?)(\d+(?:/\d+)?)', resto):
                c = Fraction(num)
                const += (-c if sign == '-' else c)

        return coefs, const, max_var

    # ---------------- Núcleo Gauss / Gauss-Jordan ----------------
    def _forward_elimination_make_pivots_one(self, M):
        """
        Elimina por debajo y normaliza cada fila pivote a 1.
        Devuelve (pasos, A_escalonada, lista_pivotes_col).
        """
        pasos = []
        A = copy.deepcopy(M)
        n, m = len(A), len(A[0])
        row = 0
        pivots = []

        for col in range(m):
            # Buscar pivote != 0 en o debajo de 'row'
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

            piv = A[row][col]
            if piv != 1:
                A[row] = [x / piv for x in A[row]]
                pasos.append(f"F{row+1} ÷ ({self._fmt(piv)})\n{self.mostrar_matriz(A)}")

            # Eliminar debajo
            for r in range(row + 1, n):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor * A[row][j] for j in range(m)]
                    pasos.append(f"F{r+1} → F{r+1} - ({self._fmt(factor)})·F{row+1}\n{self.mostrar_matriz(A)}")

            pivots.append(col)
            row += 1
            if row == n:
                break

        return pasos, A, pivots

    def _back_elimination(self, A, pivots):
        """
        Elimina por encima de cada pivote (asume filas pivote ya normalizadas).
        Devuelve (pasos, A_rref).
        """
        pasos = []
        R = copy.deepcopy(A)
        n, m = len(R), len(R[0])

        # Cada pivote en fila r está en columna pivots[r]
        for r in reversed(range(len(pivots))):
            c = pivots[r]
            # proteger rangos
            if r >= n or c >= m:
                continue
            for up in range(r):
                factor = R[up][c]
                if factor != 0:
                    R[up] = [R[up][j] - factor * R[r][j] for j in range(m)]
                    pasos.append(f"F{up+1} → F{up+1} - ({self._fmt(factor)})·F{r+1}\n{self.mostrar_matriz(R)}")
        return pasos, R

    def _diagnostico_sistema(self, A_rref):
        """
        Diagnóstico interpretando la última columna como RHS (Ax = b).
        Devuelve texto con:
          - inconsistente / solución única / infinitas soluciones
          - solución paramétrica cuando aplique
        """
        n, m = len(A_rref), len(A_rref[0])
        if m < 2:
            return "⚠️ Para diagnóstico, la última columna debe ser el término independiente (RHS)."

        NV = m - 1  # número de variables
        # Inconsistencia: fila de ceros en coeficientes y RHS != 0
        for r in range(n):
            if all(A_rref[r][c] == 0 for c in range(NV)) and A_rref[r][-1] != 0:
                return "❌ Sistema INCONSISTENTE (no tiene solución)."

        # Detectar columnas pivote
        pivot_cols = []
        for r in range(n):
            # índice del primer no-cero en la fila r (en las primeras NV columnas)
            first = None
            for c in range(NV):
                if A_rref[r][c] != 0:
                    first = c; break
            if first is not None and first not in pivot_cols:
                pivot_cols.append(first)

        libres = [c for c in range(NV) if c not in pivot_cols]

        if not pivot_cols:
            # todo libre -> infinitas
            if NV == 0:
                return "✅ Sistema CONSISTENTE (trivial)."
            texto = "✅ Infinitas soluciones.\nVariables libres: " + ", ".join(f"x{l+1}" for l in libres)
            texto += "\nParámetros: " + ", ".join(f"t{i+1}" for i in range(len(libres)))
            return texto

        if libres:
            texto = "✅ Infinitas soluciones.\nVariables libres: " + ", ".join(f"x{l+1}" for l in libres) + "\n"
            # Construcción paramétrica básica a partir de RREF
            free_to_t = {l: i + 1 for i, l in enumerate(libres)}
            ecuaciones = []
            # Tomar filas hasta min(len(pivot_cols), n)
            for r in range(min(len(pivot_cols), n)):
                c = pivot_cols[r]
                rhs = A_rref[r][-1]
                expr = f"{self._fmt(rhs)}"
                for l in libres:
                    coef = A_rref[r][l]
                    if coef != 0:
                        t = free_to_t[l]
                        signo = "-" if coef > 0 else "+"
                        expr += f" {signo} {self._fmt(abs(coef))}·t{t}"
                ecuaciones.append(f"x{c+1} = {expr}")
            for l, t in free_to_t.items():
                ecuaciones.append(f"x{l+1} = t{t}")
            texto += "Solución paramétrica:\n" + "\n".join(ecuaciones)
            return texto

        # Solución única
        sol = [Fraction(0)] * NV
        used_rows = 0
        for c in pivot_cols:
            if used_rows < n:
                sol[c] = A_rref[used_rows][-1]
                used_rows += 1
        return "✅ Solución única:\n" + "\n".join(f"x{i+1} = {self._fmt(sol[i])}" for i in range(NV))

    # ---------------- Acciones ----------------
    def ejecutar_operacion(self):
        op = self.operacion_combo.currentText()
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B) if self.tabla_B.isVisible() else None

        try:
            if op == "Suma":
                if B is None:
                    self.mostrar_procedimiento("Error: Matriz B requerida para la suma."); return
                if len(A) != len(B) or len(A[0]) != len(B[0]):
                    self.mostrar_procedimiento("Error: A y B deben tener mismas dimensiones."); return
                C = [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                pasos = "Matriz A:\n" + self.mostrar_matriz(A) + "\n\nMatriz B:\n" + self.mostrar_matriz(B) + "\n\n"
                pasos += "Pasos de la suma:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        pasos += f"({i+1},{j+1}): {self._fmt(A[i][j])} + {self._fmt(B[i][j])} = {self._fmt(C[i][j])}\n"
                pasos += "\nResultado A + B:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(pasos)

            elif op == "Resta":
                if B is None:
                    self.mostrar_procedimiento("Error: Matriz B requerida para la resta."); return
                if len(A) != len(B) or len(A[0]) != len(B[0]):
                    self.mostrar_procedimiento("Error: A y B deben tener mismas dimensiones."); return
                C = [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                pasos = "Matriz A:\n" + self.mostrar_matriz(A) + "\n\nMatriz B:\n" + self.mostrar_matriz(B) + "\n\n"
                pasos += "Pasos de la resta:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        pasos += f"({i+1},{j+1}): {self._fmt(A[i][j])} - {self._fmt(B[i][j])} = {self._fmt(C[i][j])}\n"
                pasos += "\nResultado A - B:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(pasos)

            elif op == "Multiplicacion":
                if B is None:
                    self.mostrar_procedimiento("Error: Matriz B requerida para la multiplicación."); return
                if len(A[0]) != len(B):
                    self.mostrar_procedimiento("Error: columnas(A) ≠ filas(B)."); return
                C = [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
                pasos = "Matriz A:\n" + self.mostrar_matriz(A) + "\n\nMatriz B:\n" + self.mostrar_matriz(B) + "\n\n"
                pasos += "Pasos de la multiplicación:\n"
                for i in range(len(A)):
                    for j in range(len(B[0])):
                        sum_str = " + ".join(f"{self._fmt(A[i][k])}·{self._fmt(B[k][j])}" for k in range(len(B)))
                        pasos += f"({i+1},{j+1}): {sum_str} = {self._fmt(C[i][j])}\n"
                pasos += "\nResultado A × B:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(pasos)

            elif op == "Traspuesta":
                if not A or not A[0]:
                    self.mostrar_procedimiento("Error: Matriz A vacía o inválida para trasponer."); return
                filas, cols = len(A), len(A[0])
                T = [[A[i][j] for i in range(filas)] for j in range(cols)]
                pasos = "Matriz A:\n" + self.mostrar_matriz(A) + "\n\nPasos de la traspuesta:\n"
                for i in range(filas):
                    for j in range(cols):
                        pasos += f"A({i+1},{j+1}) → T({j+1},{i+1}) = {self._fmt(A[i][j])}\n"
                pasos += "\nResultado A^T:\n" + self.mostrar_matriz(T)
                self.mostrar_procedimiento(pasos)

            elif op == "Gauss":
                pasos_fwd, A_escalon, pivots = self._forward_elimination_make_pivots_one(A)
                # Para diagnóstico más claro, llevar a RREF (sin mezclar los pasos de Gauss)
                _, A_rref = self._back_elimination(A_escalon, pivots)
                texto = "Pasos (eliminación hacia adelante):\n" + "\n\n".join(pasos_fwd)
                texto += "\n\nMatriz resultante (escalonada):\n" + self.mostrar_matriz(A_escalon)
                texto += "\n\nDiagnóstico (asumiendo última columna RHS):\n" + self._diagnostico_sistema(A_rref)
                self.mostrar_procedimiento(texto)

            elif op == "Gauss-Jordan":
                pasos_fwd, A_escalon, pivots = self._forward_elimination_make_pivots_one(A)
                pasos_back, A_rref = self._back_elimination(A_escalon, pivots)
                texto = "Pasos (adelante):\n" + "\n\n".join(pasos_fwd)
                texto += "\n\nPasos (hacia atrás):\n" + ("\n\n".join(pasos_back) if pasos_back else "(no hubo pasos)")
                texto += "\n\nMatriz resultante (RREF):\n" + self.mostrar_matriz(A_rref)
                texto += "\n\nDiagnóstico (asumiendo última columna RHS):\n" + self._diagnostico_sistema(A_rref)
                self.mostrar_procedimiento(texto)

            elif op == "Multiplicacion por escalar":
                esc_str, ok = QInputDialog.getText(self, "Escalar", "Ingrese el escalar (ej: 2, 0.5 o 1/3):")
                if not ok or esc_str.strip() == "": return
                try:
                    k = Fraction(esc_str)
                except Exception:
                    self.mostrar_procedimiento("Error: el escalar no es válido (use 2, 0.5 o 1/3).")
                    return
                if not A or not A[0]:
                    self.mostrar_procedimiento("Error: Matriz A vacía o inválida."); return
                C = [[k * A[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                pasos = "Matriz A:\n" + self.mostrar_matriz(A) + f"\n\nEscalar k = {self._fmt(k)}\n\nPasos:\n"
                for i in range(len(A)):
                    for j in range(len(A[0])):
                        pasos += f"({i+1},{j+1}): {self._fmt(k)} × {self._fmt(A[i][j])} = {self._fmt(C[i][j])}\n"
                pasos += "\nResultado k × A:\n" + self.mostrar_matriz(C)
                self.mostrar_procedimiento(pasos)

            elif op == "Inversa":
                if not A or not A[0]:
                    self.mostrar_procedimiento("Error: Matriz A vacía o inválida."); return
                if len(A) != len(A[0]):
                    self.mostrar_procedimiento("Error: la matriz no es cuadrada, no tiene inversa."); return

                n = len(A)
                AI = [row[:] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
                texto = "Matriz aumentada [A | I]:\n" + self.mostrar_matriz(AI) + "\n\n"

                # Gauss-Jordan sobre [A|I]
                for i in range(n):
                    # Pivote: si 0, buscar fila abajo
                    if AI[i][i] == 0:
                        swap = None
                        for k in range(i + 1, n):
                            if AI[k][i] != 0:
                                swap = k; break
                        if swap is None:
                            self.mostrar_procedimiento("La matriz no tiene inversa (determinante = 0)."); return
                        AI[i], AI[swap] = AI[swap], AI[i]
                        texto += f"Intercambio F{i+1} ↔ F{swap+1}\n{self.mostrar_matriz(AI)}\n\n"

                    piv = AI[i][i]
                    if piv != 1:
                        AI[i] = [x / piv for x in AI[i]]
                        texto += f"F{i+1} ÷ ({self._fmt(piv)})\n{self.mostrar_matriz(AI)}\n\n"

                    # Ceros arriba y abajo
                    for j in range(n):
                        if j == i: continue
                        factor = AI[j][i]
                        if factor != 0:
                            AI[j] = [AI[j][k] - factor * AI[i][k] for k in range(2 * n)]
                            texto += f"F{j+1} → F{j+1} - ({self._fmt(factor)})·F{i+1}\n{self.mostrar_matriz(AI)}\n\n"

                inv = [row[n:] for row in AI]
                texto += "Matriz inversa (A⁻¹):\n" + self.mostrar_matriz(inv)
                self.mostrar_procedimiento(texto)

        except Exception as e:
            self.mostrar_procedimiento(f"Error al realizar la operación: {e}")
