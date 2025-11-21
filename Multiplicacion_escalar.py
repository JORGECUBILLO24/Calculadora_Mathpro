from fractions import Fraction
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit
)
from PyQt6.QtWidgets import QSizePolicy, QSplitter
from PyQt6.QtWebEngineWidgets import QWebEngineView

def multiplicar_matriz_por_escalar(M, k):
    """
    Multiplica la matriz M por el escalar k.
    Devuelve la matriz resultante, los pasos y un texto descriptivo.
    """
    if not M or not M[0]:
        return [], [], "Matriz vacía."

    filas = len(M)
    cols = len(M[0])
    C = [[Fraction(0) for _ in range(cols)] for _ in range(filas)]
    pasos = []
    texto = f"Multiplicando la matriz por el escalar {k}:\n"

    for i in range(filas):
        for j in range(cols):
            C[i][j] = M[i][j] * k
            texto += f"Elemento ({i+1},{j+1}): {M[i][j]} * {k} = {C[i][j]}\n"
            pasos.append((i, j, M[i][j], k, C[i][j]))

    return C, pasos, texto


class VentanaMultiplicacionEscalar(QWidget):
    """
    Ventana para multiplicar matrices A y B por escalares
    y mostrar TODOS los pasos en LaTeX (MathJax + QWebEngineView).

    - Matriz B se activa/desactiva SOLO con el botón "Ocultar/Mostrar matriz B".
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multiplicación por escalar")
        self.usar_B = True  # estado lógico de la matriz B

        # ----------------- Estilos generales -----------------
        self.setStyleSheet("""
            QWidget {
                background-color:#F0F4F8;
                color:#000000;
            }
            QLineEdit {
                background:white;
                border:1px solid #B0BEC5;
                border-radius:6px;
                padding:4px 6px;
            }
            QTableWidget {
                background:white;
                border-radius:10px;
                gridline-color:#CFD8DC;
            }
            QHeaderView::section {
                background:#ECEFF1;
                padding:4px;
                border:0px;
            }
            QComboBox {
                background:white;
                border:1px solid #B0BEC5;
                border-radius:6px;
                padding:4px 6px;
            }
        """)

        font_label = QFont("Segoe UI", 12, QFont.Weight.Bold)
        font_input = QFont("Segoe UI", 11)
        font_btn   = QFont("Segoe UI", 11, QFont.Weight.Bold)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ==================================================
        #   FILAS / COLUMNAS A y B
        # ==================================================
        dims_layout = QHBoxLayout()
        dims_layout.setSpacing(30)

        # ----- A -----
        box_A = QVBoxLayout()
        box_A.setSpacing(6)

        filaA = QHBoxLayout()
        lbl_fA = QLabel("Filas A:")
        lbl_fA.setFont(font_label)
        filaA.addWidget(lbl_fA)
        self.filas_input_a = QLineEdit("3")
        self.filas_input_a.setFixedWidth(60)
        self.filas_input_a.setFont(font_input)
        filaA.addWidget(self.filas_input_a)
        box_A.addLayout(filaA)

        colA = QHBoxLayout()
        lbl_cA = QLabel("Columnas A:")
        lbl_cA.setFont(font_label)
        colA.addWidget(lbl_cA)
        self.cols_input_a = QLineEdit("3")
        self.cols_input_a.setFixedWidth(60)
        self.cols_input_a.setFont(font_input)
        colA.addWidget(self.cols_input_a)
        box_A.addLayout(colA)

        self.btn_actualizar_a = QPushButton("Actualizar A")
        self.btn_actualizar_a.setFont(font_btn)
        self.btn_actualizar_a.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_actualizar_a.setStyleSheet("""
            QPushButton {
                background-color:#1E88E5;
                color:white;
                border-radius:10px;
                padding:6px 14px;
            }
            QPushButton:hover { background-color:#1565C0; }
        """)
        box_A.addWidget(self.btn_actualizar_a, alignment=Qt.AlignmentFlag.AlignLeft)

        dims_layout.addLayout(box_A, 1)

        # ----- separador -----
        dims_layout.addStretch(1)

        # ----- B -----
        box_B = QVBoxLayout()
        box_B.setSpacing(6)

        # *** Eliminado: self.chk_usar_B = QCheckBox("Usar matriz B") ***
        # box_B.addWidget(self.chk_usar_B) # También eliminado

        filaB = QHBoxLayout()
        self.lbl_fB = QLabel("Filas B:")
        self.lbl_fB.setFont(font_label)
        filaB.addWidget(self.lbl_fB)
        self.filas_input_b = QLineEdit("3")
        self.filas_input_b.setFixedWidth(60)
        self.filas_input_b.setFont(font_input)
        filaB.addWidget(self.filas_input_b)
        box_B.addLayout(filaB)

        colB = QHBoxLayout()
        self.lbl_cB = QLabel("Columnas B:")
        self.lbl_cB.setFont(font_label)
        colB.addWidget(self.lbl_cB)
        self.cols_input_b = QLineEdit("3")
        self.cols_input_b.setFixedWidth(60)
        self.cols_input_b.setFont(font_input)
        colB.addWidget(self.cols_input_b)
        box_B.addLayout(colB)

        self.btn_actualizar_b = QPushButton("Actualizar B")
        self.btn_actualizar_b.setFont(font_btn)
        self.btn_actualizar_b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_actualizar_b.setStyleSheet("""
            QPushButton {
                background-color:#1E88E5;
                color:white;
                border-radius:10px;
                padding:6px 14px;
            }
            QPushButton:hover { background-color:#1565C0; }
        """)
        box_B.addWidget(self.btn_actualizar_b, alignment=Qt.AlignmentFlag.AlignLeft)

        dims_layout.addLayout(box_B, 1)
        root.addLayout(dims_layout)

        # ==================================================
        #   TABLAS A y B
        # ==================================================
        tablas_layout = QHBoxLayout()
        tablas_layout.setSpacing(18)

        # --- Matriz A ---
        col_A = QVBoxLayout()
        col_A.setSpacing(6)
        lbl_A = QLabel("Matriz A:")
        lbl_A.setFont(font_label)
        col_A.addWidget(lbl_A)

        self.tabla_A = QTableWidget(3, 3)
        self.tabla_A.setFont(QFont("Consolas", 12))
        self.tabla_A.setSizePolicy(QSizePolicy.Policy.Expanding,
                                   QSizePolicy.Policy.Expanding)
        self._rellenar_celdas_con_ceros(self.tabla_A)
        tablas_layout.addLayout(col_A)
        col_A.addWidget(self.tabla_A)

        # --- Matriz B ---
        self.col_B = QVBoxLayout()
        self.col_B.setSpacing(6)
        self.lbl_B = QLabel("Matriz B:")
        self.lbl_B.setFont(font_label)
        self.col_B.addWidget(self.lbl_B)

        self.tabla_B = QTableWidget(3, 3)
        self.tabla_B.setFont(QFont("Consolas", 12))
        self.tabla_B.setSizePolicy(QSizePolicy.Policy.Expanding,
                                   QSizePolicy.Policy.Expanding)
        self._rellenar_celdas_con_ceros(self.tabla_B)
        self.col_B.addWidget(self.tabla_B)

        tablas_layout.addLayout(self.col_B)
        root.addLayout(tablas_layout)

        # ==================================================
        #   ESCALARES + OPERACIÓN + BOTONES
        # ==================================================
        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)

        lbl_eA = QLabel("Escalar A:")
        lbl_eA.setFont(font_label)
        ctrl.addWidget(lbl_eA)

        self.escalar_input_a = QLineEdit("2")
        self.escalar_input_a.setFixedWidth(120)
        self.escalar_input_a.setFont(font_input)
        ctrl.addWidget(self.escalar_input_a)

        self.lbl_eB = QLabel("Escalar B:")
        self.lbl_eB.setFont(font_label)
        ctrl.addWidget(self.lbl_eB)

        self.escalar_input_b = QLineEdit("3")
        self.escalar_input_b.setFixedWidth(120)
        self.escalar_input_b.setFont(font_input)
        ctrl.addWidget(self.escalar_input_b)

        self.op_combo = QComboBox()
        self.op_combo.setFont(font_input)
        self.op_combo.addItems([
            "No operar",
            "Sumar resultados",
            "Restar resultados (A - B)"
        ])
        self.op_combo.setFixedWidth(220)
        ctrl.addWidget(self.op_combo)

        ctrl.addStretch(1)

        # botón para ocultar/mostrar B
        self.btn_toggle_B = QPushButton("Ocultar matriz B")
        self.btn_toggle_B.setFont(font_btn)
        self.btn_toggle_B.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_B.setMinimumWidth(170)
        self.btn_toggle_B.setStyleSheet("""
            QPushButton {
                background-color:#00897B;
                color:white;
                border-radius:10px;
                padding:8px 18px;
            }
            QPushButton:hover { background-color:#00695C; }
        """)
        ctrl.addWidget(self.btn_toggle_B)

        # botón calcular
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.setFont(font_btn)
        self.btn_calcular.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calcular.setMinimumWidth(130)
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color:#43A047;
                color:white;
                border-radius:10px;
                padding:8px 18px;
            }
            QPushButton:hover { background-color:#2E7D32; }
        """)
        ctrl.addWidget(self.btn_calcular)

        root.addLayout(ctrl)

        # ==================================================
        #   PANEL TEXTO (OCULTO) + WEB (MATHJAX)
        # ==================================================
        self.procedimiento_text = QTextEdit()
        self.procedimiento_text.setFixedHeight(1)
        self.procedimiento_text.setStyleSheet(
            "color:transparent; background:transparent; border:none;"
        )

        self.procedimiento_web = QWebEngineView()

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.procedimiento_text)
        splitter.addWidget(self.procedimiento_web)
        splitter.setSizes([0, 600])
        root.addWidget(splitter, 1)

        # ----------------- Conexiones -----------------
        self.btn_actualizar_a.clicked.connect(self.actualizar_dimensiones_a)
        self.btn_actualizar_b.clicked.connect(self.actualizar_dimensiones_b)
        self.btn_calcular.clicked.connect(self.calcular)
        self.btn_toggle_B.clicked.connect(self.toggle_matriz_b)
        # *** Eliminado: self.chk_usar_B.stateChanged.connect(self._sincronizar_check_con_boton) ***

        # Mensaje inicial
        self._set_html_content(
            "<div class='card'>Ingresa matrices y escalares, luego pulsa "
            "<b>Calcular</b>.</div>"
        )

        # aplicar visibilidad inicial
        self._aplicar_visibilidad_matriz_b()

    # =====================================================
    #   HTML + MathJax
    # =====================================================
    def _set_html_content(self, body_html: str) -> None:
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <style>
                body {{
                    background-color:#F0F4F8;
                    font-family:'Segoe UI',sans-serif;
                    padding:10px;
                }}
                .card {{
                    background:#FFFFFF;
                    border-radius:12px;
                    padding:16px 20px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.15);
                    margin-bottom:10px;
                }}
                pre {{
                    font-family:Consolas,'Courier New',monospace;
                    font-size:13px;
                    white-space:pre-wrap;
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

    # =====================================================
    #   Helpers tablas
    # =====================================================
    def _rellenar_celdas_con_ceros(self, tabla: QTableWidget) -> None:
        filas = tabla.rowCount()
        cols = tabla.columnCount()
        for i in range(filas):
            for j in range(cols):
                it = tabla.item(i, j)
                if it is None:
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    it.setForeground(Qt.GlobalColor.black)
                    it.setFont(QFont("Consolas", 12))
                    tabla.setItem(i, j, it)

    def actualizar_dimensiones_a(self) -> None:
        try:
            f = int(self.filas_input_a.text())
            c = int(self.cols_input_a.text())
            if f <= 0 or c <= 0:
                return
            self.tabla_A.setRowCount(f)
            self.tabla_A.setColumnCount(c)
            self._rellenar_celdas_con_ceros(self.tabla_A)
        except Exception:
            return

    def actualizar_dimensiones_b(self) -> None:
        if not self.usar_B:
            return
        try:
            f = int(self.filas_input_b.text())
            c = int(self.cols_input_b.text())
            if f <= 0 or c <= 0:
                return
            self.tabla_B.setRowCount(f)
            self.tabla_B.setColumnCount(c)
            self._rellenar_celdas_con_ceros(self.tabla_B)
        except Exception:
            return

    def leer_tabla(self, tabla: QTableWidget):
        filas = tabla.rowCount()
        cols = tabla.columnCount()
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

    # =====================================================
    #   Helpers LaTeX
    # =====================================================
    def _fmt_frac_latex(self, x: Fraction) -> str:
        if x.denominator == 1:
            return str(x.numerator)
        return f"\\frac{{{x.numerator}}}{{{x.denominator}}}"

    def _latex_matriz(self, M) -> str:
        if not M or not M[0]:
            return "\\begin{bmatrix}\\end{bmatrix}"
        filas_latex = []
        for fila in M:
            celdas = [self._fmt_frac_latex(x) for x in fila]
            filas_latex.append(" & ".join(celdas))
        cuerpo = " \\\\ ".join(filas_latex)
        return f"\\begin{{bmatrix}}{cuerpo}\\end{{bmatrix}}"

    def _operar_matrices_resultado(self, A, B, oper: str):
        filas = len(A)
        cols = len(A[0]) if filas > 0 else 0
        if filas != len(B) or cols != len(B[0]):
            return None, [], "Las dimensiones no coinciden; no se puede operar."

        R = [[Fraction(0) for _ in range(cols)] for _ in range(filas)]
        pasos = []
        texto = f"Pasos de la operación ({'suma' if oper=='sum' else 'resta'}):\n"

        for i in range(filas):
            for j in range(cols):
                if oper == "sum":
                    R[i][j] = A[i][j] + B[i][j]
                    texto += f"({i+1},{j+1}): {A[i][j]} + {B[i][j]} = {R[i][j]}\n"
                else:
                    R[i][j] = A[i][j] - B[i][j]
                    texto += f"({i+1},{j+1}): {A[i][j]} - {B[i][j]} = {R[i][j]}\n"
                pasos.append((i, j, A[i][j], B[i][j], R[i][j]))

        return R, pasos, texto

    # =====================================================
    #   Mostrar / ocultar matriz B
    # =====================================================
    def _aplicar_visibilidad_matriz_b(self) -> None:
        visible = self.usar_B

        # controles superiores
        self.lbl_fB.setVisible(visible)
        self.filas_input_b.setVisible(visible)
        self.lbl_cB.setVisible(visible)
        self.cols_input_b.setVisible(visible)
        self.btn_actualizar_b.setVisible(visible)

        # tablas
        self.lbl_B.setVisible(visible)
        self.tabla_B.setVisible(visible)

        # controles inferiores
        self.lbl_eB.setVisible(visible)
        self.escalar_input_b.setVisible(visible)
        self.op_combo.setVisible(visible)
        self.op_combo.setEnabled(visible)

        if visible:
            self.btn_toggle_B.setText("Ocultar matriz B")
        else:
            self.btn_toggle_B.setText("Mostrar matriz B")
            self.op_combo.setCurrentIndex(0)

    def toggle_matriz_b(self) -> None:
        self.usar_B = not self.usar_B
        self._aplicar_visibilidad_matriz_b()
    
    # *** Eliminado el método _sincronizar_check_con_boton ***

    # =====================================================
    #   Calcular
    # =====================================================
    def calcular(self) -> None:
        # ----- Matriz A -----
        A = self.leer_tabla(self.tabla_A)
        try:
            esc_a = Fraction(self.escalar_input_a.text().strip().replace(",", "."))
        except Exception:
            self._set_html_content(
                "<div class='card'><b>Error:</b> Escalar A inválido.</div>"
            )
            return

        C_a, pasos_a, texto_a = multiplicar_matriz_por_escalar(A, esc_a)

        # ----- Matriz B (opcional) -----
        B = None
        C_b = None
        pasos_b = []
        texto_b = ""
        R = None
        pasos_R = []
        texto_op = ""
        op_text = self.op_combo.currentText()

        if self.usar_B:
            B = self.leer_tabla(self.tabla_B)
            try:
                esc_b = Fraction(self.escalar_input_b.text().strip().replace(",", "."))
            except Exception:
                self._set_html_content(
                    "<div class='card'><b>Error:</b> Escalar B inválido.</div>"
                )
                return

            C_b, pasos_b, texto_b = multiplicar_matriz_por_escalar(B, esc_b)

            if op_text != "No operar":
                oper = "sum" if op_text.startswith("Sumar") else "sub"
                R, pasos_R, texto_op = self._operar_matrices_resultado(C_a, C_b, oper)

        # texto crudo
        texto = "--- Resultado para Matriz A ---\n" + texto_a
        if self.usar_B:
            texto += "\n\n--- Resultado para Matriz B ---\n" + texto_b
            if texto_op:
                texto += "\n\n--- Operación entre resultados ---\n" + texto_op
        self.procedimiento_text.setPlainText(texto)

        # ========== LaTeX ==========
        latex_A  = self._latex_matriz(A)
        latex_Ca = self._latex_matriz(C_a)
        latex_ka = self._fmt_frac_latex(esc_a)

        pasos_a_latex = "\\begin{aligned}"
        for (i, j, a_ij, k, c_ij) in pasos_a:
            pasos_a_latex += (
                f"c_{{{i+1}{j+1}}} &= {self._fmt_frac_latex(a_ij)}"
                f"\\cdot {self._fmt_frac_latex(k)}"
                f" = {self._fmt_frac_latex(c_ij)}\\\\"
            )
        pasos_a_latex += "\\end{aligned}"

        body_html = "<div class='card'>"
        body_html += "<h3>Matriz A</h3>"
        body_html += f"$$ A = {latex_A} $$"
        body_html += f"$$ k_A = {latex_ka} $$"
        body_html += "<h4>Pasos:</h4>"
        body_html += f"$$ {pasos_a_latex} $$"
        body_html += "<h4>Resultado:</h4>"
        body_html += f"$$ k_A \\cdot A = {latex_Ca} $$"
        body_html += "</div>"

        if self.usar_B and B is not None:
            latex_B  = self._latex_matriz(B)
            latex_Cb = self._latex_matriz(C_b)
            latex_kb = self._fmt_frac_latex(esc_b)

            pasos_b_latex = "\\begin{aligned}"
            for (i, j, a_ij, k, c_ij) in pasos_b:
                pasos_b_latex += (
                    f"d_{{{i+1}{j+1}}} &= {self._fmt_frac_latex(a_ij)}"
                    f"\\cdot {self._fmt_frac_latex(k)}"
                    f" = {self._fmt_frac_latex(c_ij)}\\\\"
                )
            pasos_b_latex += "\\end{aligned}"

            body_html += "<div class='card'>"
            body_html += "<h3>Matriz B</h3>"
            body_html += f"$$ B = {latex_B} $$"
            body_html += f"$$ k_B = {latex_kb} $$"
            body_html += "<h4>Pasos:</h4>"
            body_html += f"$$ {pasos_b_latex} $$"
            body_html += "<h4>Resultado:</h4>"
            body_html += f"$$ k_B \\cdot B = {latex_Cb} $$"
            body_html += "</div>"

        if self.usar_B and R is not None:
            latex_R = self._latex_matriz(R)
            pasos_R_latex = "\\begin{aligned}"
            for (i, j, ca_ij, cb_ij, r_ij) in pasos_R:
                if op_text.startswith("Sumar"):
                    pasos_R_latex += (
                        f"r_{{{i+1}{j+1}}} &= {self._fmt_frac_latex(ca_ij)}"
                        f" + {self._fmt_frac_latex(cb_ij)}"
                        f" = {self._fmt_frac_latex(r_ij)}\\\\"
                    )
                else:
                    pasos_R_latex += (
                        f"r_{{{i+1}{j+1}}} &= {self._fmt_frac_latex(ca_ij)}"
                        f" - {self._fmt_frac_latex(cb_ij)}"
                        f" = {self._fmt_frac_latex(r_ij)}\\\\"
                    )
            pasos_R_latex += "\\end{aligned}"

            body_html += "<div class='card'>"
            body_html += "<h3>Operación entre resultados</h3>"
            body_html += "<h4>Pasos:</h4>"
            body_html += f"$$ {pasos_R_latex} $$"
            body_html += "<h4>Resultado final:</h4>"
            if op_text.startswith("Sumar"):
                body_html += "$$ (k_A A) + (k_B B) = " + latex_R + " $$"
            else:
                body_html += "$$ (k_A A) - (k_B B) = " + latex_R + " $$"
            body_html += "</div>"

        self._set_html_content(body_html)