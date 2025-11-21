<<<<<<< HEAD
# Determinantes.py - Ventana de cálculo de determinantes con LaTeX

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit,
    QSizePolicy, QHeaderView, QSplitter
)
from PyQt6.QtGui import QFont, QTextCursor, QGuiApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from fractions import Fraction
import html


class VentanaDeterminantes(QWidget):
    """
    Ventana para cálculo de determinantes:
      - Cofactores (expansión)
      - Regla de Sarrus (3x3)
      - Método de Cramer (Ax = b)
    Muestra los procedimientos usando LaTeX real en QWebEngineView + MathJax.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cálculo de determinantes")
        self.setStyleSheet("background-color:#F0F4F8; color:#000000;")

        font_label = QFont("Segoe UI", 14, QFont.Weight.Bold)
        font_input = QFont("Segoe UI", 12)
        font_btn = QFont("Segoe UI", 13, QFont.Weight.Bold)

        # ===============================================================
        #                PANEL DE DIMENSIONES A Y B
        # ===============================================================
        input_layout = QHBoxLayout()
        input_layout.setSpacing(20)

        # ---------- Matriz A ----------
        self.a_widget = QWidget()
        a_layout = QVBoxLayout(self.a_widget)

        labelA = QLabel("Matriz A")
        labelA.setFont(font_label)
        a_layout.addWidget(labelA)

        filaA = QHBoxLayout()
        filaA.addWidget(QLabel("Filas:"))
        self.filas_A_input = QLineEdit("3")
        self.filas_A_input.setFixedWidth(60)
        self.filas_A_input.setFont(font_input)
        filaA.addWidget(self.filas_A_input)
        a_layout.addLayout(filaA)

        colA = QHBoxLayout()
        colA.addWidget(QLabel("Columnas:"))
        self.columnas_A_input = QLineEdit("3")
        self.columnas_A_input.setFixedWidth(60)
        self.columnas_A_input.setFont(font_input)
        colA.addWidget(self.columnas_A_input)
        a_layout.addLayout(colA)

        # ---------- Matriz / Vector B (para Cramer) ----------
        self.b_widget = QWidget()
        b_layout = QVBoxLayout(self.b_widget)

        labelB = QLabel("Vector B (RHS para Cramer)")
        labelB.setFont(font_label)
        b_layout.addWidget(labelB)

        filaB = QHBoxLayout()
        filaB.addWidget(QLabel("Filas:"))
        self.filas_B_input = QLineEdit("3")
        self.filas_B_input.setFixedWidth(60)
        self.filas_B_input.setFont(font_input)
        filaB.addWidget(self.filas_B_input)
        b_layout.addLayout(filaB)

        colB = QHBoxLayout()
        colB.addWidget(QLabel("Columnas:"))
        self.columnas_B_input = QLineEdit("1")
        self.columnas_B_input.setFixedWidth(60)
        self.columnas_B_input.setFont(font_input)
        colB.addWidget(self.columnas_B_input)
        b_layout.addLayout(colB)

        self.a_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.b_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        input_layout.addWidget(self.a_widget, 1)
        input_layout.addWidget(self.b_widget, 1)

        # ===============================================================
        #                     TABLAS A Y B
        # ===============================================================
        matrices_layout = QHBoxLayout()
        matrices_layout.setSpacing(12)

        self.tabla_A = QTableWidget()
        self._config_tabla(self.tabla_A, "Matriz A")

        self.tabla_B = QTableWidget()
        self._config_tabla(self.tabla_B, "Vector B (RHS)")

        matrices_layout.addWidget(self.tabla_A, 1)
        matrices_layout.addWidget(self.tabla_B, 1)

        # ===============================================================
        #                   BARRA DE ACCIONES
        # ===============================================================
        acciones = QHBoxLayout()
        acciones.setContentsMargins(0, 10, 0, 10)
        acciones.setSpacing(10)

        self.metodo_combo = QComboBox()
        self.metodo_combo.addItems([
            "Cofactores (expansión)",
            "Regla de Sarrus (3x3)",
            "Cramer (Ax = b)"
        ])
        self.metodo_combo.setFont(font_input)
        self.metodo_combo.setFixedWidth(300)
        self.metodo_combo.setStyleSheet("""
            QComboBox {
                background-color:#1E88E5;
                color:white;
                border-radius:12px;
                padding:6px;
            }
        """)

        self.btn_limpiar = QPushButton("Limpiar matrices")
        self.btn_limpiar.setFont(font_btn)
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.setMinimumHeight(40)
        self.btn_limpiar.setFixedWidth(180)
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color:#E53935;
                color:white;
                border-radius:12px;
                padding:8px 16px;
            }
            QPushButton:hover {
                background-color:#B71C1C;
            }
        """)

        self.btn_ejecutar = QPushButton("Calcular")
        self.btn_ejecutar.setFont(font_btn)
        self.btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ejecutar.setMinimumHeight(40)
        self.btn_ejecutar.setFixedWidth(160)
        self.btn_ejecutar.setStyleSheet("""
            QPushButton {
                background-color:#43A047;
                color:white;
                border-radius:12px;
                padding:8px 16px;
            }
            QPushButton:hover {
                background-color:#2E7D32;
            }
        """)

        acciones.addWidget(self.metodo_combo, 0)
        acciones.addStretch(1)
        acciones.addWidget(self.btn_limpiar, 0)
        acciones.addWidget(self.btn_ejecutar, 0)

        # ===============================================================
        #                PANEL TEXTO (OCULTO) + WEB (LaTeX)
        # ===============================================================
        self.procedimiento_text = QTextEdit()
        self.procedimiento_text.setFixedHeight(1)
        self.procedimiento_text.setStyleSheet(
            "color:transparent; background:transparent; border:none;"
        )

        self.procedimiento_web = QWebEngineView()

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.procedimiento_text)
        splitter.addWidget(self.procedimiento_web)
        splitter.setSizes([0, 700])

        # Layout principal
        root = QVBoxLayout()
        root.setSpacing(12)
        root.setContentsMargins(12, 12, 12, 12)
        root.addLayout(input_layout)
        root.addLayout(matrices_layout)
        root.addLayout(acciones)
        root.addWidget(splitter, 1)
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
        self._set_html_content(
            "<div class='card'>"
            "Configura la matriz A (y B para Cramer) y selecciona un método."
            "</div>"
        )

    # ===============================================================
    #                 HELPERS DE HTML / LATEX
    # ===============================================================
    def _set_html_content(self, body_html: str):
        """
        Renderiza body_html dentro de una plantilla HTML con estilos
        tipo tarjeta y soporte MathJax para LaTeX.
        """
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <style>
                body {{
                    background-color: #F0F4F8;
                    font-family: 'Segoe UI', sans-serif;
                    padding: 10px;
                }}
                .card {{
                    background: #FFFFFF;
                    border-radius: 12px;
                    padding: 16px 20px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                    margin-bottom: 10px;
                }}
                pre {{
                    font-family: Consolas, 'Courier New', monospace;
                    font-size: 13px;
                    white-space: pre-wrap;
                }}
                h3, h4 {{
                    margin-top: 0;
                }}
            </style>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
            </script>
        </head>
        <body>
            {body_html}
        </body>
        </html>
        """
        self.procedimiento_web.setHtml(full_html)

    def _fmt(self, x: Fraction) -> str:
        return str(x.numerator) if x.denominator == 1 else str(x)

    def _fmt_frac_latex(self, x: Fraction) -> str:
        """
        Convierte un Fraction a LaTeX:
        3/1 -> '3', 3/4 -> '\\frac{3}{4}'.
        """
        if x.denominator == 1:
            return str(x.numerator)
        return f"\\frac{{{x.numerator}}}{{{x.denominator}}}"

    def _latex_matriz(self, M) -> str:
        """
        Convierte una matriz numérica (lista de listas) a entorno bmatrix.
        """
        if not M or not M[0]:
            return "\\begin{bmatrix}\\end{bmatrix}"
        filas_latex = []
        for fila in M:
            celdas = [self._fmt_frac_latex(x) for x in fila]
            filas_latex.append(" & ".join(celdas))
        cuerpo = " \\\\ ".join(filas_latex)
        return f"\\begin{{bmatrix}}{cuerpo}\\end{{bmatrix}}"

    # ===============================================================
    #             CONFIGURACIÓN Y UTILIDADES DE TABLAS
    # ===============================================================
    def _config_tabla(self, tabla: QTableWidget, titulo: str):
        tabla.setStyleSheet("background-color:white; border-radius:12px; color: black;")
        tabla.setFont(QFont("Consolas", 12))
        tabla.setRowCount(3)
        tabla.setColumnCount(3)
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
        self.tabla_A.setRowCount(fA)
        self.tabla_A.setColumnCount(cA)
        self.tabla_A.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cA)])
        self.tabla_A.setVerticalHeaderLabels([f"F{i+1}" for i in range(fA)])
        self.tabla_A.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._rellenar_ceros(self.tabla_A)

        # Tabla B
        self.tabla_B.setRowCount(fB)
        self.tabla_B.setColumnCount(cB)
        self.tabla_B.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cB)])
        self.tabla_B.setVerticalHeaderLabels([f"F{i+1}" for i in range(fB)])
        self.tabla_B.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._rellenar_ceros(self.tabla_B)

    def _toggle_matrizB(self):
        """
        Muestra u oculta la matriz B según el método seleccionado.
        """
        metodo = self.metodo_combo.currentText()
        necesita_B = metodo == "Cramer (Ax = b)"
        self.b_widget.setVisible(necesita_B)
        self.tabla_B.setVisible(necesita_B)

    # ---------------- Lectura y formato de matrices ----------------
    def leer_tabla(self, tabla: QTableWidget):
        filas, cols = tabla.rowCount(), tabla.columnCount()
        M = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                it = tabla.item(i, j)
                s = it.text().strip() if it and it.text() else "0"
                try:
                    fila.append(Fraction(s.replace(",", ".")))
                except Exception:
                    fila.append(Fraction(0))
            M.append(fila)
        return M

    def mostrar_matriz(self, M):
        return "\n".join("[ " + "  ".join(self._fmt(x) for x in fila) + " ]" for fila in M)

    def mostrar_procedimiento(self, texto: str):
        """
        Muestra un mensaje simple (errores, info) en modo texto + tarjeta.
        """
        self.procedimiento_text.setPlainText(texto)

        def _scroll():
            try:
                cur = self.procedimiento_text.textCursor()
                cur.movePosition(QTextCursor.MoveOperation.End)
                self.procedimiento_text.setTextCursor(cur)
                self.procedimiento_text.ensureCursorVisible()
            except Exception:
                pass

        QTimer.singleShot(30, _scroll)
        QTimer.singleShot(150, _scroll)

        texto_escapado = html.escape(texto)
        body = f"<div class='card'><pre>{texto_escapado}</pre></div>"
        self._set_html_content(body)

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
                        it.setForeground(Qt.GlobalColor.black)
                        it.setFont(QFont("Consolas", 12))
        self.procedimiento_text.clear()
        self._set_html_content(
            "<div class='card'>Matrices limpiadas. Vuelve a ingresar datos.</div>"
        )

    
    # ===============================================================
    #          MÉTODO DE COFACTORES 
    # ===============================================================
    def determinante_cofactores_latex(self, M):
        """
        Calcula el determinante por expansión de cofactores (fila 1).
        Devuelve:
            det  : Fraction
            latex: str (procedimiento en LaTeX REAL, sin $$)
        """

        def _det(A, nivel):
            n = len(A)
            indent = "\\quad" * nivel  # sangría visual en LaTeX

            # ---------- CASO 1x1 ----------
            if n == 1:
                a = A[0][0]
                latex_line = (
                    f"{indent}\\text{{Matriz 1x1: }}\\\\[4pt]"
                    f"{indent}\\det([ {self._fmt_frac_latex(a)} ])"
                    f" = {self._fmt_frac_latex(a)}\\\\[10pt]"
                )
                return a, latex_line

            # ---------- CASO 2x2 ----------
            if n == 2:
                a, b = A[0][0], A[0][1]
                c, d = A[1][0], A[1][1]
                det_2 = a * d - b * c
                latex_line = (
                    f"{indent}\\text{{Matriz 2x2: }}\\\\[4pt]"
                    f"{indent}"
                    f"\\det\\left(\\begin{{bmatrix}}"
                    f"{self._fmt_frac_latex(a)} & {self._fmt_frac_latex(b)} \\\\ "
                    f"{self._fmt_frac_latex(c)} & {self._fmt_frac_latex(d)}"
                    f"\\end{{bmatrix}}\\right)\\\\[4pt]"
                    f"{indent}= {self._fmt_frac_latex(a)}\\cdot{self._fmt_frac_latex(d)}"
                    f" - {self._fmt_frac_latex(b)}\\cdot{self._fmt_frac_latex(c)}"
                    f" = {self._fmt_frac_latex(det_2)}\\\\[10pt]"
                )
                return det_2, latex_line

            # ---------- CASO GENERAL n×n ----------
            det_total = Fraction(0)
            pasos = (
                f"{indent}\\textbf{{Expansión por cofactores en la fila 1}}\\\\[8pt]"
            )

            # Recorremos columnas de la fila 1
            for j in range(n):
                a_1j = A[0][j]

                # Si el elemento es 0, la contribución es 0
                if a_1j == 0:
                    pasos += (
                        f"{indent}\\text{{a(1,{j+1}) = 0 → contribución 0}}\\\\[6pt]"
                    )
                    continue

                # Construir submatriz M_{1,j+1} eliminando fila 1 y columna j
                sub = []
                for r in range(1, n):
                    fila_sub = []
                    for c in range(n):
                        if c == j:
                            continue
                        fila_sub.append(A[r][c])
                    sub.append(fila_sub)

                # Determinante recursivo del menor
                det_sub, latex_sub = _det(sub, nivel + 1)

                # Signo (-1)^(1+j) → con j de 0 a n-1 es (-1)^j
                signo = Fraction(-1) ** j
                contrib = signo * a_1j * det_sub

                # Menor en LaTeX (submatriz)
                M_latex = self._latex_matriz(sub)
                pasos += (
                    f"{indent}\\text{{Eliminar fila 1 y columna {j+1}:}}\\\\[4pt]"
                    f"{indent}M_{{1,{j+1}}} = {M_latex} \\\\[6pt]"
                )

                # Cofactor y determinante del menor
                pasos += (
                    f"{indent}C_{{1,{j+1}}} = "
                    f"(-1)^{{1+{j+1}}}"
                    f"{self._fmt_frac_latex(a_1j)}"
                    f"\\det(M_{{1,{j+1}}})\\\\[4pt]"
                )

                # Pasos internos del determinante del menor (más indentado)
                pasos += latex_sub + "\\\\[4pt]"

                # Contribución a la suma total
                pasos += (
                    f"{indent}\\Rightarrow "
                    f"{self._fmt_frac_latex(signo)}"
                    f"\\cdot{self._fmt_frac_latex(a_1j)}"
                    f"\\cdot{self._fmt_frac_latex(det_sub)}"
                    f" = {self._fmt_frac_latex(contrib)}\\\\[10pt]"
                )

                det_total += contrib

            pasos += (
                f"{indent}\\textbf{{Suma de contribuciones: }} "
                f"{self._fmt_frac_latex(det_total)}"
            )

            return det_total, pasos

        det, latex = _det(M, nivel=0)
        return det, latex

    # ===============================================================
    #      REGLA DE SARRUS (3x3) — LaTeX REAL (PARTE 3)
    # ===============================================================
   
        """
        Regla de Sarrus para matrices 3x3.
        Devuelve:
            det  : Fraction
            latex: str (procedimiento en LaTeX REAL, sin $$)
        """
        if len(M) != 3 or len(M[0]) != 3:
            raise ValueError("La regla de Sarrus solo aplica para matrices 3x3.")

        a = M  # alias corto

        # Productos positivos (diagonales principales extendidas)
        p1 = a[0][0] * a[1][1] * a[2][2]
        p2 = a[0][1] * a[1][2] * a[2][0]
        p3 = a[0][2] * a[1][0] * a[2][1]
        sum_pos = p1 + p2 + p3

        # Productos negativos (diagonales secundarias extendidas)
        q1 = a[0][2] * a[1][1] * a[2][0]
        q2 = a[0][0] * a[1][2] * a[2][1]
        q3 = a[0][1] * a[1][0] * a[2][2]
        sum_neg = q1 + q2 + q3

        det = sum_pos - sum_neg

        # Matriz A en LaTeX
        latex_A = self._latex_matriz(M)

        # Representación LaTeX de cada producto positivo
        p1_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )
        p2_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        p3_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )
        positivos_prod = f"{p1_l} + {p2_l} + {p3_l}"

        # Representación LaTeX de cada producto negativo
        q1_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        q2_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )
        q3_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )
        negativos_prod = f"{q1_l} + {q2_l} + {q3_l}"

        # Construir explicación completa en LaTeX
        latex = (
            "\\textbf{Regla de Sarrus (3\\times 3)}\\\\[6pt]"
            "\\text{Matriz }A:\\\\[2pt]"
            f"{latex_A} \\\\[10pt]"
            "\\textbf{Diagonales positivas (verde):}\\\\[4pt]"
            f"\\color{{#2E7D32}}{{{positivos_prod}}}"
            f" = {self._fmt_frac_latex(sum_pos)} \\\\[10pt]"
            "\\textbf{Diagonales negativas (rojo):}\\\\[4pt]"
            f"\\color{{#C62828}}{{{negativos_prod}}}"
            f" = {self._fmt_frac_latex(sum_neg)} \\\\[10pt]"
            "\\textbf{Determinante final:}\\\\[4pt]"
            f"\\det(A) = {self._fmt_frac_latex(sum_pos)}"
            f" - {self._fmt_frac_latex(sum_neg)}"
            f" = {self._fmt_frac_latex(det)}"
        )

        return det, latex
      # ===============================================================
    #      REGLA DE SARRUS (3x3) 
    # ===============================================================
    def determinante_sarrus_latex(self, M):
        """
        Regla de Sarrus para matrices 3x3.
        Devuelve:
            det  : Fraction
            latex: str (procedimiento en LaTeX REAL, sin $$)
        """
        if len(M) != 3 or len(M[0]) != 3:
            raise ValueError("La regla de Sarrus solo aplica para matrices 3x3.")

        a = M  # alias corto

        # Productos positivos (diagonales principales extendidas)
        p1 = a[0][0] * a[1][1] * a[2][2]
        p2 = a[0][1] * a[1][2] * a[2][0]
        p3 = a[0][2] * a[1][0] * a[2][1]
        sum_pos = p1 + p2 + p3

        # Productos negativos (diagonales secundarias extendidas)
        q1 = a[0][2] * a[1][1] * a[2][0]
        q2 = a[0][0] * a[1][2] * a[2][1]
        q3 = a[0][1] * a[1][0] * a[2][2]
        sum_neg = q1 + q2 + q3

        det = sum_pos - sum_neg

        # Matriz A en LaTeX
        latex_A = self._latex_matriz(M)

        # Productos positivos
        p1_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )
        p2_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        p3_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )

        # Productos negativos
        q1_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        q2_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )
        q3_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )

        latex = (
            "\\textbf{Regla de Sarrus (3\\times 3)}\\\\[8pt]"
            "\\text{Matriz }A:\\\\[4pt]"
            f"{latex_A} \\\\[12pt]"
            "\\textbf{Diagonales positivas (verde):}\\\\[6pt]"
            "\\color{#2E7D32}{"
            f"{p1_l} + {p2_l} + {p3_l}"
            "}\\\\[4pt]"
            f"= {self._fmt_frac_latex(sum_pos)} \\\\[12pt]"
            "\\textbf{Diagonales negativas (rojo):}\\\\[6pt]"
            "\\color{#C62828}{"
            f"{q1_l} + {q2_l} + {q3_l}"
            "}\\\\[4pt]"
            f"= {self._fmt_frac_latex(sum_neg)} \\\\[12pt]"
            "\\textbf{Determinante final:}\\\\[6pt]"
            f"\\det(A) = {self._fmt_frac_latex(sum_pos)}"
            f" - {self._fmt_frac_latex(sum_neg)}"
            f" = {self._fmt_frac_latex(det)}"
        )

        return det, latex
    # ===============================================================
    #   MÉTODO DE CRAMER (Ax = b) 
    # ===============================================================
    def cramer_latex(self, A, B):
        """
        Método de Cramer para Ax = B.
        A: matriz cuadrada (n x n)
        B: vector columna (n x 1)
        Devuelve:
            soluciones : lista[Fraction]
            latex      : str (procedimiento completo en LaTeX, sin $$)
        Usa determinante_cofactores_latex para det(A) y det(A_i).
        """
        n = len(A)
        if n == 0 or len(A[0]) != n:
            raise ValueError("A debe ser una matriz cuadrada n×n.")

        if B is None or len(B) != n:
            raise ValueError("B debe tener la misma cantidad de filas que A.")
        for fila in B:
            if len(fila) != 1:
                raise ValueError("B debe ser un vector columna (una sola columna).")

        # =======================
        # 1) Determinante de A
        # =======================
        detA, latex_detA_pasos = self.determinante_cofactores_latex(A)
        if detA == 0:
            raise ValueError("det(A) = 0 → el sistema no tiene solución única (Cramer no aplica).")

        latex_A = self._latex_matriz(A)
        latex_B = self._latex_matriz(B)
        latex_detA = self._fmt_frac_latex(detA)

        latex_global = (
            "\\textbf{Método de Cramer para } Ax = b\\\\[6pt]"
            "\\text{Matriz de coeficientes } A:\\\\[4pt]"
            f"{latex_A} \\\\[10pt]"
            "\\text{Vector de términos independientes } b:\\\\[4pt]"
            f"{latex_B} \\\\[10pt]"
            "\\textbf{1) Cálculo de } \\det(A) \\\\[4pt]"
            f"{latex_detA_pasos} \\\\[4pt]"
            "\\Rightarrow \\det(A) = " + latex_detA + " \\\\[12pt]"
        )

        # =======================
        # 2) Construir A_i y det(A_i)
        # =======================
        soluciones = []
        det_mods = []

        latex_global += "\\textbf{2) Cálculo de cada } \\det(A_i) \\text{ y de } x_i\\\\[6pt]"

        for i in range(n):
            # Construir A_i sustituyendo la columna i por B
            A_mod = []
            for r in range(n):
                fila_mod = []
                for c in range(n):
                    if c == i:
                        fila_mod.append(B[r][0])
                    else:
                        fila_mod.append(A[r][c])
                A_mod.append(fila_mod)

            # Determinante de A_i por cofactores (con LaTeX)
            detAi, latex_detAi_pasos = self.determinante_cofactores_latex(A_mod)
            det_mods.append(detAi)

            latex_Ai = self._latex_matriz(A_mod)
            latex_detAi = self._fmt_frac_latex(detAi)

            # x_i = det(A_i) / det(A)
            xi = detAi / detA
            soluciones.append(xi)
            latex_xi = self._fmt_frac_latex(xi)

            latex_global += (
                "\\textbf{Columna " + str(i+1) + ":}\\\\[4pt]"
                "\\text{Matriz } A_{" + str(i+1) +
                "} \\text{ (sustituyendo columna " + str(i+1) + " por } b \\text{):}\\\\[4pt]"
                f"{latex_Ai} \\\\[4pt]"
                "\\text{Determinante de } A_{" + str(i+1) + "}:\\\\[4pt]"
                f"{latex_detAi_pasos} \\\\[4pt]"
                "\\Rightarrow \\det(A_{" + str(i+1) + "}) = " + latex_detAi + " \\\\[6pt]"
                "\\text{Aplicando Cramer: }\\\\[2pt]"
                "x_{" + str(i+1) + "} = \\dfrac{\\det(A_{" + str(i+1) + "})}{\\det(A)}"
                " = \\dfrac{" + latex_detAi + "}{" + latex_detA + "}"
                " = " + latex_xi + " \\\\[12pt]"
            )

        # =======================
        # 3) Resumen final
        # =======================
        latex_global += "\\textbf{3) Solución del sistema:}\\\\[4pt]"
        latex_global += "\\begin{aligned}"
        for i, xi in enumerate(soluciones):
            latex_global += (
                f"x_{{{i+1}}} &= {self._fmt_frac_latex(xi)} \\\\"
            )
        latex_global += "\\end{aligned}"

        return soluciones, latex_global
    # ===============================================================
    #   ACCIÓN PRINCIPAL: CALCULAR
    # ===============================================================
    def ejecutar_calculo(self):
        metodo = self.metodo_combo.currentText()
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B) if self.tabla_B.isVisible() else None

        try:
            # ---------- Validaciones básicas ----------
            if not A or not A[0]:
                self._set_html_content(
                    "<div class='card'><b>Error:</b> la matriz A está vacía.</div>"
                )
                return

            filas = len(A)
            cols = len(A[0])
            if filas != cols:
                self._set_html_content(
                    "<div class='card'><b>Error:</b> la matriz A debe ser cuadrada.</div>"
                )
                return

            latex_A = self._latex_matriz(A)

            # --------------------------------------------------------
            #   1) MÉTODO: COFACTORES (EXPANSIÓN)
            # --------------------------------------------------------
            if metodo == "Cofactores (expansión)":
                det, latex_pasos = self.determinante_cofactores_latex(A)
                latex_det = self._fmt_frac_latex(det)

                # Guardamos LaTeX crudo en el QTextEdit oculto
                latex_crudo = (
                    "\\textbf{Método de cofactores (expansión)}\n"
                    f"A = {latex_A}\n"
                    f"{latex_pasos}\n"
                    f"\\det(A) = {latex_det}"
                )
                self.procedimiento_text.setPlainText(latex_crudo)

                # Tarjeta HTML con MathJax (ahora en vertical con aligned)
                body = "<div class='card'>"
                body += "<h3>Método de cofactores (expansión)</h3>"
                body += f"$$ A = {latex_A} $$"
                body += "<h4>Procedimiento paso a paso:</h4>"
                body += f"$$ \\begin{{aligned}} {latex_pasos} \\end{{aligned}} $$"
                body += "<h4>Resultado:</h4>"
                body += f"$$ \\det(A) = {latex_det} $$"
                body += "</div>"

                self._set_html_content(body)
                return

            # --------------------------------------------------------
            #   2) MÉTODO: REGLA DE SARRUS (3x3)
            # --------------------------------------------------------
            elif metodo == "Regla de Sarrus (3x3)":
                if filas != 3 or cols != 3:
                    self._set_html_content(
                        "<div class='card'><b>Error:</b> la regla de Sarrus solo aplica a matrices 3×3.</div>"
                    )
                    return

                det, latex_sarrus = self.determinante_sarrus_latex(A)
                latex_det = self._fmt_frac_latex(det)

                # LaTeX crudo para copiar
                latex_crudo = (
                    "\\textbf{Regla de Sarrus (3\\times 3)}\n"
                    f"A = {latex_A}\n"
                    f"{latex_sarrus}\n"
                    f"\\det(A) = {latex_det}"
                )
                self.procedimiento_text.setPlainText(latex_crudo)

                body = "<div class='card'>"
                body += "<h3>Regla de Sarrus (3×3)</h3>"
                body += f"$$ A = {latex_A} $$"
                body += "<h4>Procedimiento:</h4>"
                body += f"$$ \\begin{{aligned}} {latex_sarrus} \\end{{aligned}} $$"
                body += "<h4>Resultado:</h4>"
                body += f"$$ \\det(A) = {latex_det} $$"
                body += "</div>"

                self._set_html_content(body)
                return

            # --------------------------------------------------------
            #   3) MÉTODO: CRAMER (Ax = b)
            # --------------------------------------------------------
            elif metodo == "Cramer (Ax = b)":
                if B is None:
                    self._set_html_content(
                        "<div class='card'><b>Error:</b> se requiere el vector B para aplicar Cramer.</div>"
                    )
                    return

                # B debe ser vector columna (una sola columna)
                if any(len(fila) != 1 for fila in B):
                    self._set_html_content(
                        "<div class='card'><b>Error:</b> B debe ser un vector columna (1 sola columna).</div>"
                    )
                    return

                soluciones, latex_cramer = self.cramer_latex(A, B)

                # Guardamos el LaTeX crudo
                self.procedimiento_text.setPlainText(latex_cramer)

                body = "<div class='card'>"
                body += "<h3>Método de Cramer (Ax = b)</h3>"
                body += f"$$ \\begin{{aligned}} {latex_cramer} \\end{{aligned}} $$"
                body += "</div>"

                self._set_html_content(body)
                return

        except Exception as e:
            self._set_html_content(
                f"<div class='card'><b>Error al calcular:</b> {html.escape(str(e))}</div>"
            )
=======
# Determinantes.py - Ventana de cálculo de determinantes con LaTeX

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit,
    QSizePolicy, QHeaderView, QSplitter
)
from PyQt6.QtGui import QFont, QTextCursor, QGuiApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from fractions import Fraction
import html


class VentanaDeterminantes(QWidget):
    """
    Ventana para cálculo de determinantes:
      - Cofactores (expansión)
      - Regla de Sarrus (3x3)
      - Método de Cramer (Ax = b)
    Muestra los procedimientos usando LaTeX real en QWebEngineView + MathJax.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cálculo de determinantes")
        self.setStyleSheet("background-color:#F0F4F8; color:#000000;")

        font_label = QFont("Segoe UI", 14, QFont.Weight.Bold)
        font_input = QFont("Segoe UI", 12)
        font_btn = QFont("Segoe UI", 13, QFont.Weight.Bold)

        # ===============================================================
        #                PANEL DE DIMENSIONES A Y B
        # ===============================================================
        input_layout = QHBoxLayout()
        input_layout.setSpacing(20)

        # ---------- Matriz A ----------
        self.a_widget = QWidget()
        a_layout = QVBoxLayout(self.a_widget)

        labelA = QLabel("Matriz A")
        labelA.setFont(font_label)
        a_layout.addWidget(labelA)

        filaA = QHBoxLayout()
        filaA.addWidget(QLabel("Filas:"))
        self.filas_A_input = QLineEdit("3")
        self.filas_A_input.setFixedWidth(60)
        self.filas_A_input.setFont(font_input)
        filaA.addWidget(self.filas_A_input)
        a_layout.addLayout(filaA)

        colA = QHBoxLayout()
        colA.addWidget(QLabel("Columnas:"))
        self.columnas_A_input = QLineEdit("3")
        self.columnas_A_input.setFixedWidth(60)
        self.columnas_A_input.setFont(font_input)
        colA.addWidget(self.columnas_A_input)
        a_layout.addLayout(colA)

        # ---------- Matriz / Vector B (para Cramer) ----------
        self.b_widget = QWidget()
        b_layout = QVBoxLayout(self.b_widget)

        labelB = QLabel("Vector B (RHS para Cramer)")
        labelB.setFont(font_label)
        b_layout.addWidget(labelB)

        filaB = QHBoxLayout()
        filaB.addWidget(QLabel("Filas:"))
        self.filas_B_input = QLineEdit("3")
        self.filas_B_input.setFixedWidth(60)
        self.filas_B_input.setFont(font_input)
        filaB.addWidget(self.filas_B_input)
        b_layout.addLayout(filaB)

        colB = QHBoxLayout()
        colB.addWidget(QLabel("Columnas:"))
        self.columnas_B_input = QLineEdit("1")
        self.columnas_B_input.setFixedWidth(60)
        self.columnas_B_input.setFont(font_input)
        colB.addWidget(self.columnas_B_input)
        b_layout.addLayout(colB)

        self.a_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.b_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        input_layout.addWidget(self.a_widget, 1)
        input_layout.addWidget(self.b_widget, 1)

        # ===============================================================
        #                     TABLAS A Y B
        # ===============================================================
        matrices_layout = QHBoxLayout()
        matrices_layout.setSpacing(12)

        self.tabla_A = QTableWidget()
        self._config_tabla(self.tabla_A, "Matriz A")

        self.tabla_B = QTableWidget()
        self._config_tabla(self.tabla_B, "Vector B (RHS)")

        matrices_layout.addWidget(self.tabla_A, 1)
        matrices_layout.addWidget(self.tabla_B, 1)

        # ===============================================================
        #                   BARRA DE ACCIONES
        # ===============================================================
        acciones = QHBoxLayout()
        acciones.setContentsMargins(0, 10, 0, 10)
        acciones.setSpacing(10)

        self.metodo_combo = QComboBox()
        self.metodo_combo.addItems([
            "Cofactores (expansión)",
            "Regla de Sarrus (3x3)",
            "Cramer (Ax = b)"
        ])
        self.metodo_combo.setFont(font_input)
        self.metodo_combo.setFixedWidth(300)
        self.metodo_combo.setStyleSheet("""
            QComboBox {
                background-color:#1E88E5;
                color:white;
                border-radius:12px;
                padding:6px;
            }
        """)

        self.btn_limpiar = QPushButton("Limpiar matrices")
        self.btn_limpiar.setFont(font_btn)
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.setMinimumHeight(40)
        self.btn_limpiar.setFixedWidth(180)
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color:#E53935;
                color:white;
                border-radius:12px;
                padding:8px 16px;
            }
            QPushButton:hover {
                background-color:#B71C1C;
            }
        """)

        self.btn_ejecutar = QPushButton("Calcular")
        self.btn_ejecutar.setFont(font_btn)
        self.btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ejecutar.setMinimumHeight(40)
        self.btn_ejecutar.setFixedWidth(160)
        self.btn_ejecutar.setStyleSheet("""
            QPushButton {
                background-color:#43A047;
                color:white;
                border-radius:12px;
                padding:8px 16px;
            }
            QPushButton:hover {
                background-color:#2E7D32;
            }
        """)

        acciones.addWidget(self.metodo_combo, 0)
        acciones.addStretch(1)
        acciones.addWidget(self.btn_limpiar, 0)
        acciones.addWidget(self.btn_ejecutar, 0)

        # ===============================================================
        #                PANEL TEXTO (OCULTO) + WEB (LaTeX)
        # ===============================================================
        self.procedimiento_text = QTextEdit()
        self.procedimiento_text.setFixedHeight(1)
        self.procedimiento_text.setStyleSheet(
            "color:transparent; background:transparent; border:none;"
        )

        self.procedimiento_web = QWebEngineView()

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.procedimiento_text)
        splitter.addWidget(self.procedimiento_web)
        splitter.setSizes([0, 700])

        # Layout principal
        root = QVBoxLayout()
        root.setSpacing(12)
        root.setContentsMargins(12, 12, 12, 12)
        root.addLayout(input_layout)
        root.addLayout(matrices_layout)
        root.addLayout(acciones)
        root.addWidget(splitter, 1)
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
        self._set_html_content(
            "<div class='card'>"
            "Configura la matriz A (y B para Cramer) y selecciona un método."
            "</div>"
        )

    # ===============================================================
    #                 HELPERS DE HTML / LATEX
    # ===============================================================
    def _set_html_content(self, body_html: str):
        """
        Renderiza body_html dentro de una plantilla HTML con estilos
        tipo tarjeta y soporte MathJax para LaTeX.
        """
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <style>
                body {{
                    background-color: #F0F4F8;
                    font-family: 'Segoe UI', sans-serif;
                    padding: 10px;
                }}
                .card {{
                    background: #FFFFFF;
                    border-radius: 12px;
                    padding: 16px 20px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                    margin-bottom: 10px;
                }}
                pre {{
                    font-family: Consolas, 'Courier New', monospace;
                    font-size: 13px;
                    white-space: pre-wrap;
                }}
                h3, h4 {{
                    margin-top: 0;
                }}
            </style>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
            </script>
        </head>
        <body>
            {body_html}
        </body>
        </html>
        """
        self.procedimiento_web.setHtml(full_html)

    def _fmt(self, x: Fraction) -> str:
        return str(x.numerator) if x.denominator == 1 else str(x)

    def _fmt_frac_latex(self, x: Fraction) -> str:
        """
        Convierte un Fraction a LaTeX:
        3/1 -> '3', 3/4 -> '\\frac{3}{4}'.
        """
        if x.denominator == 1:
            return str(x.numerator)
        return f"\\frac{{{x.numerator}}}{{{x.denominator}}}"

    def _latex_matriz(self, M) -> str:
        """
        Convierte una matriz numérica (lista de listas) a entorno bmatrix.
        """
        if not M or not M[0]:
            return "\\begin{bmatrix}\\end{bmatrix}"
        filas_latex = []
        for fila in M:
            celdas = [self._fmt_frac_latex(x) for x in fila]
            filas_latex.append(" & ".join(celdas))
        cuerpo = " \\\\ ".join(filas_latex)
        return f"\\begin{{bmatrix}}{cuerpo}\\end{{bmatrix}}"

    # ===============================================================
    #             CONFIGURACIÓN Y UTILIDADES DE TABLAS
    # ===============================================================
    def _config_tabla(self, tabla: QTableWidget, titulo: str):
        tabla.setStyleSheet("background-color:white; border-radius:12px; color: black;")
        tabla.setFont(QFont("Consolas", 12))
        tabla.setRowCount(3)
        tabla.setColumnCount(3)
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
        self.tabla_A.setRowCount(fA)
        self.tabla_A.setColumnCount(cA)
        self.tabla_A.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cA)])
        self.tabla_A.setVerticalHeaderLabels([f"F{i+1}" for i in range(fA)])
        self.tabla_A.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._rellenar_ceros(self.tabla_A)

        # Tabla B
        self.tabla_B.setRowCount(fB)
        self.tabla_B.setColumnCount(cB)
        self.tabla_B.setHorizontalHeaderLabels([f"C{j+1}" for j in range(cB)])
        self.tabla_B.setVerticalHeaderLabels([f"F{i+1}" for i in range(fB)])
        self.tabla_B.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._rellenar_ceros(self.tabla_B)

    def _toggle_matrizB(self):
        """
        Muestra u oculta la matriz B según el método seleccionado.
        """
        metodo = self.metodo_combo.currentText()
        necesita_B = metodo == "Cramer (Ax = b)"
        self.b_widget.setVisible(necesita_B)
        self.tabla_B.setVisible(necesita_B)

    # ---------------- Lectura y formato de matrices ----------------
    def leer_tabla(self, tabla: QTableWidget):
        filas, cols = tabla.rowCount(), tabla.columnCount()
        M = []
        for i in range(filas):
            fila = []
            for j in range(cols):
                it = tabla.item(i, j)
                s = it.text().strip() if it and it.text() else "0"
                try:
                    fila.append(Fraction(s.replace(",", ".")))
                except Exception:
                    fila.append(Fraction(0))
            M.append(fila)
        return M

    def mostrar_matriz(self, M):
        return "\n".join("[ " + "  ".join(self._fmt(x) for x in fila) + " ]" for fila in M)

    def mostrar_procedimiento(self, texto: str):
        """
        Muestra un mensaje simple (errores, info) en modo texto + tarjeta.
        """
        self.procedimiento_text.setPlainText(texto)

        def _scroll():
            try:
                cur = self.procedimiento_text.textCursor()
                cur.movePosition(QTextCursor.MoveOperation.End)
                self.procedimiento_text.setTextCursor(cur)
                self.procedimiento_text.ensureCursorVisible()
            except Exception:
                pass

        QTimer.singleShot(30, _scroll)
        QTimer.singleShot(150, _scroll)

        texto_escapado = html.escape(texto)
        body = f"<div class='card'><pre>{texto_escapado}</pre></div>"
        self._set_html_content(body)

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
                        it.setForeground(Qt.GlobalColor.black)
                        it.setFont(QFont("Consolas", 12))
        self.procedimiento_text.clear()
        self._set_html_content(
            "<div class='card'>Matrices limpiadas. Vuelve a ingresar datos.</div>"
        )

    
    # ===============================================================
    #          MÉTODO DE COFACTORES 
    # ===============================================================
    def determinante_cofactores_latex(self, M):
        """
        Calcula el determinante por expansión de cofactores (fila 1).
        Devuelve:
            det  : Fraction
            latex: str (procedimiento en LaTeX REAL, sin $$)
        """

        def _det(A, nivel):
            n = len(A)
            indent = "\\quad" * nivel  # sangría visual en LaTeX

            # ---------- CASO 1x1 ----------
            if n == 1:
                a = A[0][0]
                latex_line = (
                    f"{indent}\\text{{Matriz 1x1: }}\\\\[4pt]"
                    f"{indent}\\det([ {self._fmt_frac_latex(a)} ])"
                    f" = {self._fmt_frac_latex(a)}\\\\[10pt]"
                )
                return a, latex_line

            # ---------- CASO 2x2 ----------
            if n == 2:
                a, b = A[0][0], A[0][1]
                c, d = A[1][0], A[1][1]
                det_2 = a * d - b * c
                latex_line = (
                    f"{indent}\\text{{Matriz 2x2: }}\\\\[4pt]"
                    f"{indent}"
                    f"\\det\\left(\\begin{{bmatrix}}"
                    f"{self._fmt_frac_latex(a)} & {self._fmt_frac_latex(b)} \\\\ "
                    f"{self._fmt_frac_latex(c)} & {self._fmt_frac_latex(d)}"
                    f"\\end{{bmatrix}}\\right)\\\\[4pt]"
                    f"{indent}= {self._fmt_frac_latex(a)}\\cdot{self._fmt_frac_latex(d)}"
                    f" - {self._fmt_frac_latex(b)}\\cdot{self._fmt_frac_latex(c)}"
                    f" = {self._fmt_frac_latex(det_2)}\\\\[10pt]"
                )
                return det_2, latex_line

            # ---------- CASO GENERAL n×n ----------
            det_total = Fraction(0)
            pasos = (
                f"{indent}\\textbf{{Expansión por cofactores en la fila 1}}\\\\[8pt]"
            )

            # Recorremos columnas de la fila 1
            for j in range(n):
                a_1j = A[0][j]

                # Si el elemento es 0, la contribución es 0
                if a_1j == 0:
                    pasos += (
                        f"{indent}\\text{{a(1,{j+1}) = 0 → contribución 0}}\\\\[6pt]"
                    )
                    continue

                # Construir submatriz M_{1,j+1} eliminando fila 1 y columna j
                sub = []
                for r in range(1, n):
                    fila_sub = []
                    for c in range(n):
                        if c == j:
                            continue
                        fila_sub.append(A[r][c])
                    sub.append(fila_sub)

                # Determinante recursivo del menor
                det_sub, latex_sub = _det(sub, nivel + 1)

                # Signo (-1)^(1+j) → con j de 0 a n-1 es (-1)^j
                signo = Fraction(-1) ** j
                contrib = signo * a_1j * det_sub

                # Menor en LaTeX (submatriz)
                M_latex = self._latex_matriz(sub)
                pasos += (
                    f"{indent}\\text{{Eliminar fila 1 y columna {j+1}:}}\\\\[4pt]"
                    f"{indent}M_{{1,{j+1}}} = {M_latex} \\\\[6pt]"
                )

                # Cofactor y determinante del menor
                pasos += (
                    f"{indent}C_{{1,{j+1}}} = "
                    f"(-1)^{{1+{j+1}}}"
                    f"{self._fmt_frac_latex(a_1j)}"
                    f"\\det(M_{{1,{j+1}}})\\\\[4pt]"
                )

                # Pasos internos del determinante del menor (más indentado)
                pasos += latex_sub + "\\\\[4pt]"

                # Contribución a la suma total
                pasos += (
                    f"{indent}\\Rightarrow "
                    f"{self._fmt_frac_latex(signo)}"
                    f"\\cdot{self._fmt_frac_latex(a_1j)}"
                    f"\\cdot{self._fmt_frac_latex(det_sub)}"
                    f" = {self._fmt_frac_latex(contrib)}\\\\[10pt]"
                )

                det_total += contrib

            pasos += (
                f"{indent}\\textbf{{Suma de contribuciones: }} "
                f"{self._fmt_frac_latex(det_total)}"
            )

            return det_total, pasos

        det, latex = _det(M, nivel=0)
        return det, latex

    # ===============================================================
    #      REGLA DE SARRUS (3x3) — LaTeX REAL (PARTE 3)
    # ===============================================================
   
        """
        Regla de Sarrus para matrices 3x3.
        Devuelve:
            det  : Fraction
            latex: str (procedimiento en LaTeX REAL, sin $$)
        """
        if len(M) != 3 or len(M[0]) != 3:
            raise ValueError("La regla de Sarrus solo aplica para matrices 3x3.")

        a = M  # alias corto

        # Productos positivos (diagonales principales extendidas)
        p1 = a[0][0] * a[1][1] * a[2][2]
        p2 = a[0][1] * a[1][2] * a[2][0]
        p3 = a[0][2] * a[1][0] * a[2][1]
        sum_pos = p1 + p2 + p3

        # Productos negativos (diagonales secundarias extendidas)
        q1 = a[0][2] * a[1][1] * a[2][0]
        q2 = a[0][0] * a[1][2] * a[2][1]
        q3 = a[0][1] * a[1][0] * a[2][2]
        sum_neg = q1 + q2 + q3

        det = sum_pos - sum_neg

        # Matriz A en LaTeX
        latex_A = self._latex_matriz(M)

        # Representación LaTeX de cada producto positivo
        p1_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )
        p2_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        p3_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )
        positivos_prod = f"{p1_l} + {p2_l} + {p3_l}"

        # Representación LaTeX de cada producto negativo
        q1_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        q2_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )
        q3_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )
        negativos_prod = f"{q1_l} + {q2_l} + {q3_l}"

        # Construir explicación completa en LaTeX
        latex = (
            "\\textbf{Regla de Sarrus (3\\times 3)}\\\\[6pt]"
            "\\text{Matriz }A:\\\\[2pt]"
            f"{latex_A} \\\\[10pt]"
            "\\textbf{Diagonales positivas (verde):}\\\\[4pt]"
            f"\\color{{#2E7D32}}{{{positivos_prod}}}"
            f" = {self._fmt_frac_latex(sum_pos)} \\\\[10pt]"
            "\\textbf{Diagonales negativas (rojo):}\\\\[4pt]"
            f"\\color{{#C62828}}{{{negativos_prod}}}"
            f" = {self._fmt_frac_latex(sum_neg)} \\\\[10pt]"
            "\\textbf{Determinante final:}\\\\[4pt]"
            f"\\det(A) = {self._fmt_frac_latex(sum_pos)}"
            f" - {self._fmt_frac_latex(sum_neg)}"
            f" = {self._fmt_frac_latex(det)}"
        )

        return det, latex
      # ===============================================================
    #      REGLA DE SARRUS (3x3) 
    # ===============================================================
    def determinante_sarrus_latex(self, M):
        """
        Regla de Sarrus para matrices 3x3.
        Devuelve:
            det  : Fraction
            latex: str (procedimiento en LaTeX REAL, sin $$)
        """
        if len(M) != 3 or len(M[0]) != 3:
            raise ValueError("La regla de Sarrus solo aplica para matrices 3x3.")

        a = M  # alias corto

        # Productos positivos (diagonales principales extendidas)
        p1 = a[0][0] * a[1][1] * a[2][2]
        p2 = a[0][1] * a[1][2] * a[2][0]
        p3 = a[0][2] * a[1][0] * a[2][1]
        sum_pos = p1 + p2 + p3

        # Productos negativos (diagonales secundarias extendidas)
        q1 = a[0][2] * a[1][1] * a[2][0]
        q2 = a[0][0] * a[1][2] * a[2][1]
        q3 = a[0][1] * a[1][0] * a[2][2]
        sum_neg = q1 + q2 + q3

        det = sum_pos - sum_neg

        # Matriz A en LaTeX
        latex_A = self._latex_matriz(M)

        # Productos positivos
        p1_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )
        p2_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        p3_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )

        # Productos negativos
        q1_l = (
            f"{self._fmt_frac_latex(a[0][2])}\\cdot"
            f"{self._fmt_frac_latex(a[1][1])}\\cdot"
            f"{self._fmt_frac_latex(a[2][0])}"
        )
        q2_l = (
            f"{self._fmt_frac_latex(a[0][0])}\\cdot"
            f"{self._fmt_frac_latex(a[1][2])}\\cdot"
            f"{self._fmt_frac_latex(a[2][1])}"
        )
        q3_l = (
            f"{self._fmt_frac_latex(a[0][1])}\\cdot"
            f"{self._fmt_frac_latex(a[1][0])}\\cdot"
            f"{self._fmt_frac_latex(a[2][2])}"
        )

        latex = (
            "\\textbf{Regla de Sarrus (3\\times 3)}\\\\[8pt]"
            "\\text{Matriz }A:\\\\[4pt]"
            f"{latex_A} \\\\[12pt]"
            "\\textbf{Diagonales positivas (verde):}\\\\[6pt]"
            "\\color{#2E7D32}{"
            f"{p1_l} + {p2_l} + {p3_l}"
            "}\\\\[4pt]"
            f"= {self._fmt_frac_latex(sum_pos)} \\\\[12pt]"
            "\\textbf{Diagonales negativas (rojo):}\\\\[6pt]"
            "\\color{#C62828}{"
            f"{q1_l} + {q2_l} + {q3_l}"
            "}\\\\[4pt]"
            f"= {self._fmt_frac_latex(sum_neg)} \\\\[12pt]"
            "\\textbf{Determinante final:}\\\\[6pt]"
            f"\\det(A) = {self._fmt_frac_latex(sum_pos)}"
            f" - {self._fmt_frac_latex(sum_neg)}"
            f" = {self._fmt_frac_latex(det)}"
        )

        return det, latex
    # ===============================================================
    #   MÉTODO DE CRAMER (Ax = b) 
    # ===============================================================
    def cramer_latex(self, A, B):
        """
        Método de Cramer para Ax = B.
        A: matriz cuadrada (n x n)
        B: vector columna (n x 1)
        Devuelve:
            soluciones : lista[Fraction]
            latex      : str (procedimiento completo en LaTeX, sin $$)
        Usa determinante_cofactores_latex para det(A) y det(A_i).
        """
        n = len(A)
        if n == 0 or len(A[0]) != n:
            raise ValueError("A debe ser una matriz cuadrada n×n.")

        if B is None or len(B) != n:
            raise ValueError("B debe tener la misma cantidad de filas que A.")
        for fila in B:
            if len(fila) != 1:
                raise ValueError("B debe ser un vector columna (una sola columna).")

        # =======================
        # 1) Determinante de A
        # =======================
        detA, latex_detA_pasos = self.determinante_cofactores_latex(A)
        if detA == 0:
            raise ValueError("det(A) = 0 → el sistema no tiene solución única (Cramer no aplica).")

        latex_A = self._latex_matriz(A)
        latex_B = self._latex_matriz(B)
        latex_detA = self._fmt_frac_latex(detA)

        latex_global = (
            "\\textbf{Método de Cramer para } Ax = b\\\\[6pt]"
            "\\text{Matriz de coeficientes } A:\\\\[4pt]"
            f"{latex_A} \\\\[10pt]"
            "\\text{Vector de términos independientes } b:\\\\[4pt]"
            f"{latex_B} \\\\[10pt]"
            "\\textbf{1) Cálculo de } \\det(A) \\\\[4pt]"
            f"{latex_detA_pasos} \\\\[4pt]"
            "\\Rightarrow \\det(A) = " + latex_detA + " \\\\[12pt]"
        )

        # =======================
        # 2) Construir A_i y det(A_i)
        # =======================
        soluciones = []
        det_mods = []

        latex_global += "\\textbf{2) Cálculo de cada } \\det(A_i) \\text{ y de } x_i\\\\[6pt]"

        for i in range(n):
            # Construir A_i sustituyendo la columna i por B
            A_mod = []
            for r in range(n):
                fila_mod = []
                for c in range(n):
                    if c == i:
                        fila_mod.append(B[r][0])
                    else:
                        fila_mod.append(A[r][c])
                A_mod.append(fila_mod)

            # Determinante de A_i por cofactores (con LaTeX)
            detAi, latex_detAi_pasos = self.determinante_cofactores_latex(A_mod)
            det_mods.append(detAi)

            latex_Ai = self._latex_matriz(A_mod)
            latex_detAi = self._fmt_frac_latex(detAi)

            # x_i = det(A_i) / det(A)
            xi = detAi / detA
            soluciones.append(xi)
            latex_xi = self._fmt_frac_latex(xi)

            latex_global += (
                "\\textbf{Columna " + str(i+1) + ":}\\\\[4pt]"
                "\\text{Matriz } A_{" + str(i+1) +
                "} \\text{ (sustituyendo columna " + str(i+1) + " por } b \\text{):}\\\\[4pt]"
                f"{latex_Ai} \\\\[4pt]"
                "\\text{Determinante de } A_{" + str(i+1) + "}:\\\\[4pt]"
                f"{latex_detAi_pasos} \\\\[4pt]"
                "\\Rightarrow \\det(A_{" + str(i+1) + "}) = " + latex_detAi + " \\\\[6pt]"
                "\\text{Aplicando Cramer: }\\\\[2pt]"
                "x_{" + str(i+1) + "} = \\dfrac{\\det(A_{" + str(i+1) + "})}{\\det(A)}"
                " = \\dfrac{" + latex_detAi + "}{" + latex_detA + "}"
                " = " + latex_xi + " \\\\[12pt]"
            )

        # =======================
        # 3) Resumen final
        # =======================
        latex_global += "\\textbf{3) Solución del sistema:}\\\\[4pt]"
        latex_global += "\\begin{aligned}"
        for i, xi in enumerate(soluciones):
            latex_global += (
                f"x_{{{i+1}}} &= {self._fmt_frac_latex(xi)} \\\\"
            )
        latex_global += "\\end{aligned}"

        return soluciones, latex_global
    # ===============================================================
    #   ACCIÓN PRINCIPAL: CALCULAR
    # ===============================================================
    def ejecutar_calculo(self):
        metodo = self.metodo_combo.currentText()
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B) if self.tabla_B.isVisible() else None

        try:
            # ---------- Validaciones básicas ----------
            if not A or not A[0]:
                self._set_html_content(
                    "<div class='card'><b>Error:</b> la matriz A está vacía.</div>"
                )
                return

            filas = len(A)
            cols = len(A[0])
            if filas != cols:
                self._set_html_content(
                    "<div class='card'><b>Error:</b> la matriz A debe ser cuadrada.</div>"
                )
                return

            latex_A = self._latex_matriz(A)

            # --------------------------------------------------------
            #   1) MÉTODO: COFACTORES (EXPANSIÓN)
            # --------------------------------------------------------
            if metodo == "Cofactores (expansión)":
                det, latex_pasos = self.determinante_cofactores_latex(A)
                latex_det = self._fmt_frac_latex(det)

                # Guardamos LaTeX crudo en el QTextEdit oculto
                latex_crudo = (
                    "\\textbf{Método de cofactores (expansión)}\n"
                    f"A = {latex_A}\n"
                    f"{latex_pasos}\n"
                    f"\\det(A) = {latex_det}"
                )
                self.procedimiento_text.setPlainText(latex_crudo)

                # Tarjeta HTML con MathJax (ahora en vertical con aligned)
                body = "<div class='card'>"
                body += "<h3>Método de cofactores (expansión)</h3>"
                body += f"$$ A = {latex_A} $$"
                body += "<h4>Procedimiento paso a paso:</h4>"
                body += f"$$ \\begin{{aligned}} {latex_pasos} \\end{{aligned}} $$"
                body += "<h4>Resultado:</h4>"
                body += f"$$ \\det(A) = {latex_det} $$"
                body += "</div>"

                self._set_html_content(body)
                return

            # --------------------------------------------------------
            #   2) MÉTODO: REGLA DE SARRUS (3x3)
            # --------------------------------------------------------
            elif metodo == "Regla de Sarrus (3x3)":
                if filas != 3 or cols != 3:
                    self._set_html_content(
                        "<div class='card'><b>Error:</b> la regla de Sarrus solo aplica a matrices 3×3.</div>"
                    )
                    return

                det, latex_sarrus = self.determinante_sarrus_latex(A)
                latex_det = self._fmt_frac_latex(det)

                # LaTeX crudo para copiar
                latex_crudo = (
                    "\\textbf{Regla de Sarrus (3\\times 3)}\n"
                    f"A = {latex_A}\n"
                    f"{latex_sarrus}\n"
                    f"\\det(A) = {latex_det}"
                )
                self.procedimiento_text.setPlainText(latex_crudo)

                body = "<div class='card'>"
                body += "<h3>Regla de Sarrus (3×3)</h3>"
                body += f"$$ A = {latex_A} $$"
                body += "<h4>Procedimiento:</h4>"
                body += f"$$ \\begin{{aligned}} {latex_sarrus} \\end{{aligned}} $$"
                body += "<h4>Resultado:</h4>"
                body += f"$$ \\det(A) = {latex_det} $$"
                body += "</div>"

                self._set_html_content(body)
                return

            # --------------------------------------------------------
            #   3) MÉTODO: CRAMER (Ax = b)
            # --------------------------------------------------------
            elif metodo == "Cramer (Ax = b)":
                if B is None:
                    self._set_html_content(
                        "<div class='card'><b>Error:</b> se requiere el vector B para aplicar Cramer.</div>"
                    )
                    return

                # B debe ser vector columna (una sola columna)
                if any(len(fila) != 1 for fila in B):
                    self._set_html_content(
                        "<div class='card'><b>Error:</b> B debe ser un vector columna (1 sola columna).</div>"
                    )
                    return

                soluciones, latex_cramer = self.cramer_latex(A, B)

                # Guardamos el LaTeX crudo
                self.procedimiento_text.setPlainText(latex_cramer)

                body = "<div class='card'>"
                body += "<h3>Método de Cramer (Ax = b)</h3>"
                body += f"$$ \\begin{{aligned}} {latex_cramer} \\end{{aligned}} $$"
                body += "</div>"

                self._set_html_content(body)
                return

        except Exception as e:
            self._set_html_content(
                f"<div class='card'><b>Error al calcular:</b> {html.escape(str(e))}</div>"
            )
>>>>>>> ef984993824d81b7fabae7af610d92334376c7ab
