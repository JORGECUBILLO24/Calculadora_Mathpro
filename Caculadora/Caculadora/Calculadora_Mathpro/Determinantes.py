# determinantes.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit,
    QSizePolicy, QHeaderView
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt, QTimer
from fractions import Fraction
import copy


class VentanaDeterminantes(QWidget):
    """
    Ventana para cálculo de determinantes:
      - Cofactores (expansión recursiva) — muestra pasos con indentación
      - Regla de Sarrus (3x3)
      - Método de Cramer (Ax = b) — requiere Matriz B como vector columna (1 columna)
    Interfaz diseñada para coincidir con el estilo de VentanaMatrices.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:#F0F4F8; color:#000000;")
        self.setWindowTitle("Cálculo de Determinantes")

        font_label = QFont("Segoe UI", 14, QFont.Weight.Bold)
        font_input = QFont("Segoe UI", 12)
        font_btn   = QFont("Segoe UI", 13, QFont.Weight.Bold)

        # --------- Panel dimensiones ---------
        input_layout = QHBoxLayout(); input_layout.setSpacing(20)

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

        # Matriz B (usada solo para Cramer)
        self.b_widget = QWidget()
        b_layout = QVBoxLayout(self.b_widget)
        b_label = QLabel("Vector B (RHS para Cramer)"); b_label.setFont(font_label); b_layout.addWidget(b_label)

        filaB = QHBoxLayout()
        filaB.addWidget(QLabel("Filas")); self.filas_B_input = QLineEdit("3")
        self.filas_B_input.setFixedWidth(60); self.filas_B_input.setFont(font_input)
        filaB.addWidget(self.filas_B_input); b_layout.addLayout(filaB)

        colB = QHBoxLayout()
        colB.addWidget(QLabel("Columnas")); self.columnas_B_input = QLineEdit("1")
        self.columnas_B_input.setFixedWidth(60); self.columnas_B_input.setFont(font_input)
        colB.addWidget(self.columnas_B_input); b_layout.addLayout(colB)

        self.a_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.b_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        input_layout.addWidget(self.a_widget, 1)
        input_layout.addWidget(self.b_widget, 1)

        # --------- Tablas A y B ---------
        matrices_layout = QHBoxLayout(); matrices_layout.setSpacing(12)

        self.tabla_A = QTableWidget(); self._config_tabla(self.tabla_A, "Matriz A")
        self.tabla_B = QTableWidget(); self._config_tabla(self.tabla_B, "Vector B (RHS)")

        matrices_layout.addWidget(self.tabla_A, 1)
        matrices_layout.addWidget(self.tabla_B, 1)

        # --------- Barra de acciones ---------
        acciones = QHBoxLayout(); acciones.setContentsMargins(0, 10, 0, 10); acciones.setSpacing(10)

        self.metodo_combo = QComboBox()
        self.metodo_combo.addItems([
            "Cofactores (expansión)",
            "Regla de Sarrus (3x3)",
            "Cramer (Ax = b)"
        ])
        self.metodo_combo.setFont(font_input)
        self.metodo_combo.setFixedWidth(300)
        self.metodo_combo.setStyleSheet("background-color:#1E88E5; color:white; border-radius:12px; padding:6px;")

        self.btn_limpiar = QPushButton("Limpiar matrices")
        self.btn_limpiar.setFont(font_btn)
        self.btn_limpiar.setStyleSheet("background-color:#E53935; color:white; border-radius:12px; padding:8px;")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.setMinimumHeight(40)
        self.btn_limpiar.setFixedWidth(180)

        self.btn_ejecutar = QPushButton("Calcular")
        self.btn_ejecutar.setFont(font_btn)
        self.btn_ejecutar.setStyleSheet("background-color:#43A047; color:white; border-radius:12px; padding:8px;")
        self.btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ejecutar.setMinimumHeight(40)
        self.btn_ejecutar.setFixedWidth(160)

        acciones.addWidget(self.metodo_combo, 0)
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
        root = QVBoxLayout(); root.setSpacing(12); root.setContentsMargins(12, 12, 12, 12)
        root.addLayout(input_layout)
        root.addLayout(matrices_layout)
        root.addLayout(acciones)
        root.addWidget(self.procedimiento_text, 1)
        self.setLayout(root)

        # Conexiones
        self.btn_ejecutar.clicked.connect(self.ejecutar_calculo)
        self.btn_limpiar.clicked.connect(self.limpiar_matrices)
        self.filas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_A_input.editingFinished.connect(self.actualizar_dimensiones)
        self.filas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.columnas_B_input.editingFinished.connect(self.actualizar_dimensiones)
        self.metodo_combo.currentTextChanged.connect(self._toggle_matrizB)

        # Estado inicial
        self.actualizar_dimensiones()
        self._toggle_matrizB()

    # ---------------- Configuración de tablas ----------------
    def _config_tabla(self, tabla: QTableWidget, titulo: str):
        tabla.setStyleSheet("background-color:white; border-radius:12px; color: black;")
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
                    # asegurar que el texto de la celda sea visible en negro
                    it.setForeground(Qt.GlobalColor.black)
                    it.setFont(QFont("Consolas", 12))
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
        """Oculta Matriz B cuando el método no la requiere."""
        metodo = self.metodo_combo.currentText()
        necesita_B = metodo == "Cramer (Ax = b)"
        # Para mantener estilo similar, ocultamos/mostramos widget y tabla B
        self.b_widget.setVisible(necesita_B)
        self.tabla_B.setVisible(necesita_B)

    # ---------------- Utilidades (misma lógica que matrices.py) ----------------
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
        for tabla in (self.tabla_A, self.tabla_B):
            for i in range(tabla.rowCount()):
                for j in range(tabla.columnCount()):
                    it = tabla.item(i, j)
                    if it is None:
                        it = QTableWidgetItem("0")
                        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        it.setForeground(Qt.GlobalColor.black)
                        it.setFont(QFont("Consolas", 12))
                        tabla.setItem(i, j, it)
                    else:
                        it.setText("0")
                        # al limpiar, forzar color y fuente para mayor contraste
                        it.setForeground(Qt.GlobalColor.black)
                        it.setFont(QFont("Consolas", 12))
        self.procedimiento_text.clear()

    # ---------------- Métodos numéricos: determinantes ----------------
    def determinante_cofactores_with_steps(self, M):
        """
        Entrada: M - lista de listas de Fraction (cuadrada)
        Salida: (determinante: Fraction, pasos: str)
        Genera pasos con indentación según la recursión.
        """
        def _det_rec(A, level=0):
            n = len(A)
            indent = "  " * level
            if n == 1:
                return A[0][0], f"{indent}det([ {self._fmt(A[0][0])} ]) = {self._fmt(A[0][0])}\n"
            if n == 2:
                det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
                s = (f"{indent}det( [[{self._fmt(A[0][0])},{self._fmt(A[0][1])}],"
                     f" [{self._fmt(A[1][0])},{self._fmt(A[1][1])}]] ) = "
                     f"{self._fmt(A[0][0])}·{self._fmt(A[1][1])} - {self._fmt(A[0][1])}·{self._fmt(A[1][0])} = {self._fmt(det)}\n")
                return det, s
            total = Fraction(0)
            pasos = f"{indent}Expansión por cofactores (fila 1):\n"
            for c in range(n):
                a = A[0][c]
                if a == 0:
                    pasos += f"{indent}  Cofactor en (1,{c+1}) = {self._fmt(a)} → contribución 0\n"
                    continue
                # construir submatriz
                sub = []
                for r in range(1, n):
                    row = []
                    for j in range(n):
                        if j == c:
                            continue
                        row.append(A[r][j])
                    sub.append(row)
                det_sub, pasos_sub = _det_rec(sub, level + 1)
                signo = Fraction(-1) ** c
                contrib = signo * a * det_sub
                pasos += f"{indent}  a(1,{c+1}) = {self._fmt(a)}, signo = {('-1' if signo < 0 else '1')}, det(sub) = {self._fmt(det_sub)}\n"
                pasos += pasos_sub
                pasos += f"{indent}  → contribución: {self._fmt(signo)}·{self._fmt(a)}·{self._fmt(det_sub)} = {self._fmt(contrib)}\n"
                total += contrib
            pasos += f"{indent}Suma contribuciones = {self._fmt(total)}\n"
            return total, pasos

        det, pasos = _det_rec(M, level=0)
        return det, pasos

    def determinante_sarrus(self, M):
        """
        Regla de Sarrus (solo para 3x3), M es lista de listas Fraction.
        Devuelve (det, pasos).
        """
        if len(M) != 3 or len(M[0]) != 3:
            raise ValueError("La regla de Sarrus solo aplica para matrices 3x3.")
        a = M
        # calcular productos
        p1 = a[0][0]*a[1][1]*a[2][2]
        p2 = a[0][1]*a[1][2]*a[2][0]
        p3 = a[0][2]*a[1][0]*a[2][1]
        q1 = a[0][2]*a[1][1]*a[2][0]
        q2 = a[0][0]*a[1][2]*a[2][1]
        q3 = a[0][1]*a[1][0]*a[2][2]
        det = p1 + p2 + p3 - q1 - q2 - q3
        pasos = "Aplicando regla de Sarrus (3x3):\n"
        pasos += f"Positivos: {self._fmt(p1)} + {self._fmt(p2)} + {self._fmt(p3)} = {self._fmt(p1 + p2 + p3)}\n"
        pasos += f"Negativos: {self._fmt(q1)} + {self._fmt(q2)} + {self._fmt(q3)} = {self._fmt(q1 + q2 + q3)}\n"
        pasos += f"Determinante = [{self._fmt(p1 + p2 + p3)}] - [{self._fmt(q1 + q2 + q3)}] = {self._fmt(det)}\n"
        return det, pasos

    def determinante_cramer(self, A, B):
        """
        A: lista de listas (n x n) Fraction
        B: lista de listas o lista (n x 1) Fraction
        Devuelve (soluciones_list, pasos_str) donde soluciones_list son Fracciones o raise ValueError.
        """
        n = len(A)
        # validar B y convertir a vector si es necesario
        if not B or len(B) != n:
            raise ValueError("Vector B debe tener la misma cantidad de filas que A.")
        # Si B viene como n x m (m>1) rechazamos
        for row in B:
            if len(row) != 1:
                raise ValueError("Para Cramer, B debe ser un vector columna (una sola columna).")

        # construir determinante A
        detA, pasosA = self.determinante_cofactores_with_steps(A)
        pasos = "Determinante de A:\n" + pasosA + "\n"
        if detA == 0:
            raise ValueError("El determinante de A es 0 → sistema no tiene solución única (Cramer no aplica).")

        soluciones = []
        pasos += f"det(A) = {self._fmt(detA)}\n\n"
        # Para cada columna i, sustituir por B y calcular det(A_i)
        for i in range(n):
            A_mod = []
            for r in range(n):
                row = []
                for c in range(n):
                    if c == i:
                        row.append(B[r][0])
                    else:
                        row.append(A[r][c])
                A_mod.append(row)
            det_mod, pasos_mod = self.determinante_cofactores_with_steps(A_mod)
            pasos += f"det(A_{{{i+1}}}) (sustituyendo columna {i+1} por B):\n"
            pasos += pasos_mod
            pasos += f"det(A_{{{i+1}}}) = {self._fmt(det_mod)}\n"
            sol = det_mod / detA
            soluciones.append(sol)
            pasos += f"x{i+1} = det(A_{{{i+1}}}) / det(A) = {self._fmt(det_mod)} / {self._fmt(detA)} = {self._fmt(sol)}\n\n"

        return soluciones, pasos

    # ---------------- Acciones ----------------
    def ejecutar_calculo(self):
        metodo = self.metodo_combo.currentText()
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B) if self.tabla_B.isVisible() else None

        try:
            # Validaciones básicas
            if not A or not A[0]:
                self.mostrar_procedimiento("Error: la matriz A es inválida o está vacía.")
                return
            filas = len(A); cols = len(A[0])
            if filas != cols:
                self.mostrar_procedimiento("Error: la matriz debe ser cuadrada para calcular su determinante.")
                return

            if metodo == "Cofactores (expansión)":
                det, pasos = self.determinante_cofactores_with_steps(A)
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\n\n"
                texto += f"Determinante por cofactores:\n{pasos}\n|A| = {self._fmt(det)}"
                self.mostrar_procedimiento(texto)

            elif metodo == "Regla de Sarrus (3x3)":
                det, pasos = self.determinante_sarrus(A)
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\n\n"
                texto += pasos + f"\n|A| = {self._fmt(det)}"
                self.mostrar_procedimiento(texto)

            elif metodo == "Cramer (Ax = b)":
                # validar A cuadrada
                if B is None:
                    self.mostrar_procedimiento("Error: se requiere el vector B (RHS) para aplicar Cramer.")
                    return
                # B debe tener una sola columna
                if any(len(row) != 1 for row in B):
                    self.mostrar_procedimiento("Error: B debe ser un vector columna (1 sola columna).")
                    return
                soluciones, pasos = self.determinante_cramer(A, B)
                texto = "Matriz A:\n" + self.mostrar_matriz(A) + "\n\n"
                texto += "Vector B:\n" + self.mostrar_matriz(B) + "\n\n"
                # en los pasos ya se incluye det(A) y det(A_i); aseguramos formato claro
                # reemplazar posible línea 'det(A) = ...' por '|A| = ...' para consistencia
                pasos = pasos.replace("det(A) =", "|A| =")
                texto += pasos
                texto += "Solución (Cramer):\n" + "\n".join(f"x{i+1} = {self._fmt(sol)}" for i, sol in enumerate(soluciones))
                self.mostrar_procedimiento(texto)

        except Exception as e:
            self.mostrar_procedimiento(f"Error al calcular: {e}")
