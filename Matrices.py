
#Jorge Cubillo - Calculadora Mathpro - Módulo Matrices (Material Design)
#jorge la bestia 
import re
import copy
from fractions import Fraction

from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QDialog,
    QPlainTextEdit, QHeaderView, QSplitter, QSizePolicy 
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


# ===============================================================
#                  MATHJAX TEMPLATE (Material Design)
# ===============================================================

HTML_MATHJAX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

<style>
body {{
    font-family: 'Segoe UI', sans-serif;
    background: #FAFAFA;
    margin: 12px;
}}

.card {{
    padding: 16px;
    background: white;
    border-radius: 12px;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.15);
    margin-top: 14px;
}}

.step {{
    padding: 10px;
    margin-top: 14px;
    background: #F0F7FF;
    border-left: 5px solid #1E88E5;
    border-radius: 6px;
}}

h2 {{
    margin-top: 6px;
    color: #1565C0;
}}
</style>

</head>
<body>
{content}
</body>
</html>
"""


# ===============================================================
#                  CLASE PRINCIPAL
# ===============================================================

class VentanaMatrices(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Matrices – Material Design")
        self.setStyleSheet("background-color:#ECEFF1; color:#000;")
        self._build_ui()
    # ===============================================================
    #                     CONSTRUCCIÓN DE UI (Material)
    # ===============================================================
    def _build_ui(self):

        font_label = QFont("Segoe UI", 14, QFont.Weight.Bold)
        font_btn   = QFont("Segoe UI", 12, QFont.Weight.Medium)

        # ---------------- Botón Convertidor ----------------
        self.btn_eq2mat = QPushButton("Ecuaciones → Matriz A")
        self.btn_eq2mat.setFont(font_btn)
        self.btn_eq2mat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eq2mat.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border-radius: 10px;
                padding: 8px 14px;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        self.btn_eq2mat.clicked.connect(self._abrir_convertidor_ecuaciones)

        # ===============================================================
        #                         MATRIZ A
        # ===============================================================

        self.a_widget = QWidget()
        layoutA = QVBoxLayout(self.a_widget)

        labelA = QLabel("Matriz A")
        labelA.setFont(font_label)
        layoutA.addWidget(labelA)

        # Dimensiones
        filaA = QHBoxLayout()
        filaA.addWidget(QLabel("Filas:"))
        self.filas_A_input = QLineEdit("3")
        self.filas_A_input.setFixedWidth(60)
        filaA.addWidget(self.filas_A_input)

        colA = QHBoxLayout()
        colA.addWidget(QLabel("Columnas:"))
        self.columnas_A_input = QLineEdit("3")
        self.columnas_A_input.setFixedWidth(60)
        colA.addWidget(self.columnas_A_input)

        layoutA.addLayout(filaA)
        layoutA.addLayout(colA)

        # Tabla A
        self.tabla_A = QTableWidget(3, 3)
        self._config_tabla(self.tabla_A)
        layoutA.addWidget(self.tabla_A)

        # ===============================================================
        #                         MATRIZ B
        # ===============================================================

        self.b_widget = QWidget()
        layoutB = QVBoxLayout(self.b_widget)

        labelB = QLabel("Matriz B")
        labelB.setFont(font_label)
        layoutB.addWidget(labelB)

        filaB = QHBoxLayout()
        filaB.addWidget(QLabel("Filas:"))
        self.filas_B_input = QLineEdit("3")
        self.filas_B_input.setFixedWidth(60)
        filaB.addWidget(self.filas_B_input)

        colB = QHBoxLayout()
        colB.addWidget(QLabel("Columnas:"))
        self.columnas_B_input = QLineEdit("3")
        self.columnas_B_input.setFixedWidth(60)
        colB.addWidget(self.columnas_B_input)

        layoutB.addLayout(filaB)
        layoutB.addLayout(colB)

        # Tabla B
        self.tabla_B = QTableWidget(3, 3)
        self._config_tabla(self.tabla_B)
        layoutB.addWidget(self.tabla_B)

        # Ambas matrices lado a lado
        matrices_layout = QHBoxLayout()
        matrices_layout.addWidget(self.a_widget)
        matrices_layout.addWidget(self.b_widget)


        # ===============================================================
        #         COMBOBOX + BOTONES DE ACCIONES (Material)
        # ===============================================================

        self.operacion_combo = QComboBox()
        self.operacion_combo.addItems([
            "Suma", "Resta", "Multiplicacion",
            "Traspuesta", "Gauss", "Gauss-Jordan", "Inversa"
        ])
        self.operacion_combo.setFont(font_btn)
        self.operacion_combo.setStyleSheet("""
            QComboBox {
                background:#1E88E5;
                color:white;
                border-radius:10px;
                padding:6px;
            }
        """)

        # Botón limpiar
        self.btn_limpiar = QPushButton("Limpiar matrices")
        self.btn_limpiar.setFont(font_btn)
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background:#E53935;
                color:white;
                border-radius:10px;
                padding:8px 14px;
            }
            QPushButton:hover { background:#B71C1C; }
        """)
        self.btn_limpiar.clicked.connect(self.limpiar_matrices)

        # Ejecutar
        self.btn_ejecutar = QPushButton("Ejecutar operación")
        self.btn_ejecutar.setFont(font_btn)
        self.btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ejecutar.setStyleSheet("""
            QPushButton {
                background:#43A047;
                color:white;
                border-radius:10px;
                padding:8px 14px;
            }
            QPushButton:hover { background:#2E7D32; }
        """)
        self.btn_ejecutar.clicked.connect(self.ejecutar_operacion)

        acciones = QHBoxLayout()
        acciones.addWidget(self.operacion_combo)
        acciones.addStretch()
        acciones.addWidget(self.btn_limpiar)
        acciones.addWidget(self.btn_ejecutar)


        # ===============================================================
        #          PANEL SUPERIOR DESACTIVADO + PANEL LATEX
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
        splitter.setSizes([0, 800])


        # ===============================================================
        #                    LAYOUT PRINCIPAL
        # ===============================================================

        root = QVBoxLayout()
        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(self.btn_eq2mat)

        root.addLayout(top)
        root.addLayout(matrices_layout)
        root.addLayout(acciones)
        root.addWidget(splitter)

        self.setLayout(root)

        # Carga inicial
        self._set_html_content("<p>Introduce una matriz o convierte ecuaciones.</p>")

        # Señales
        for w in [
            self.filas_A_input, self.columnas_A_input,
            self.filas_B_input, self.columnas_B_input
        ]:
            w.editingFinished.connect(self.actualizar_dimensiones)

        self.operacion_combo.currentTextChanged.connect(self._toggle_matrizB)


    # ===============================================================
    #               TABLAS ESTILO MATERIAL DESIGN
    # ===============================================================
    def _config_tabla(self, tabla: QTableWidget):
        tabla.setShowGrid(True)
        tabla.setAlternatingRowColors(True)

        tabla.setMinimumWidth(100)
        tabla.setMinimumHeight(150)
        tabla.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        tabla.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        tabla.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        tabla.setStyleSheet("""
            QTableWidget {
                background:white;
                border:2px solid #CFD8DC;
                border-radius:10px;
                gridline-color:#B0BEC5;
                font-size:16px;
            }
            QHeaderView::section {
                background:#ECEFF1;
                font-weight:bold;
                padding:6px;
                border:none;
                border-right:1px solid #CFD8DC;
            }
        """)

    # 👇 IMPORTANTE: nada de Stretch
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        tabla.verticalHeader().setDefaultSectionSize(50)

        filas = tabla.rowCount()
        columnas = tabla.columnCount()

        tabla.setHorizontalHeaderLabels([str(j + 1) for j in range(columnas)])
        tabla.setVerticalHeaderLabels([str(i + 1) for i in range(filas)])

        for i in range(filas):
            for j in range(columnas):
                item = tabla.item(i, j)
                if item is None:
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tabla.setItem(i, j, item)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if not item.text().strip():
                        item.setText("0")



    # ===============================================================
    #                     FUNCIONES UTILITARIAS
    # ===============================================================

    def _fmt(self, x: Fraction):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

    def _fmt_latex(self, x):
        """
        Devuelve x en LaTeX, soportando Fraction.
        Se usa para los factores en los pasos: F2 -> F2 - (factor)·F1
        """
        if isinstance(x, Fraction):
            if x.denominator == 1:
                return str(x.numerator)
            else:
                return r"\frac{" + str(x.numerator) + "}{" + str(x.denominator) + "}"
        else:
            return str(x)


    def _matriz_a_latex(self, M):
        """
        Convierte matriz a LaTeX (bmatrix), soportando Fraction.
        """
        if not M:
            return r"\begin{bmatrix}\end{bmatrix}"

        filas = []
        for fila in M:
            elems = []
            for x in fila:
                if isinstance(x, Fraction):
                    if x.denominator == 1:
                        elems.append(str(x.numerator))
                    else:
                        elems.append(
                            r"\frac{" + str(x.numerator) + "}{" + str(x.denominator) + "}"
                        )
                else:
                    elems.append(str(x))
            filas.append(" & ".join(elems))

        cuerpo = r" \\ ".join(filas)
        return r"\begin{bmatrix}" + cuerpo + r"\end{bmatrix}"

   
   
   # ===============================================================
   
   #procedimientos tuanis 
   
    def _procedimiento_suma(self, A, B, C):
        """
        Devuelve un string HTML con LaTeX mostrando el procedimiento de la suma C = A + B.
        """
        m = len(A)
        n = len(A[0]) if m > 0 else 0

        partes = []
        partes.append("<h3>Procedimiento: Suma de matrices</h3>")

        # Mostrar A, B y C
        partes.append(
            f"<p>\\[ A = {self._matriz_a_latex(A)}, \\quad B = {self._matriz_a_latex(B)} \\]</p>"
        )
        partes.append(
            f"<p>\\[ C = A + B = {self._matriz_a_latex(C)} \\]</p>"
        )

        partes.append("<p>Elementos de \\(C\\):</p>")

        pasos = []
        for i in range(m):
            for j in range(n):
                a = A[i][j]
                b = B[i][j]
                c = C[i][j]
                pasos.append(
                    f"\\(c_{{{i+1},{j+1}}} = {self._fmt_latex(a)} + {self._fmt_latex(b)} = {self._fmt_latex(c)}\\)"
                )

        partes.append("<p>" + "<br>".join(pasos) + "</p>")

        return "\n".join(partes)
    def _procedimiento_resta(self, A, B, C):
        """
        Devuelve un string HTML con LaTeX mostrando el procedimiento de la resta C = A - B.
        """
        m = len(A)
        n = len(A[0]) if m > 0 else 0

        partes = []
        partes.append("<h3>Procedimiento: Resta de matrices</h3>")

        # Mostrar A, B y C
        partes.append(
            f"<p>\\[ A = {self._matriz_a_latex(A)}, \\quad B = {self._matriz_a_latex(B)} \\]</p>"
        )
        partes.append(
            f"<p>\\[ C = A - B = {self._matriz_a_latex(C)} \\]</p>"
        )

        partes.append("<p>Elementos de \\(C\\):</p>")

        pasos = []
        for i in range(m):
            for j in range(n):
                a = A[i][j]
                b = B[i][j]
                c = C[i][j]
                pasos.append(
                    f"\\(c_{{{i+1},{j+1}}} = {self._fmt_latex(a)} - {self._fmt_latex(b)} = {self._fmt_latex(c)}\\)"
                )

        partes.append("<p>" + "<br>".join(pasos) + "</p>")

        return "\n".join(partes)
    def _procedimiento_multiplicacion(self, A, B, C):
        """
        Devuelve un string HTML con LaTeX mostrando el procedimiento de la multiplicación C = A * B.
        """
        m = len(A)
        p = len(B[0]) if B else 0
        n = len(B)

        partes = []
        partes.append("<h3>Procedimiento: Multiplicación de matrices</h3>")

        # Mostrar A, B y C
        partes.append(
            f"<p>\\[ A = {self._matriz_a_latex(A)}, \\quad B = {self._matriz_a_latex(B)} \\]</p>"
        )
        partes.append(
            f"<p>\\[ C = A \\times B = {self._matriz_a_latex(C)} \\]</p>"
        )

        partes.append("<p>Elementos de \\(C\\):</p>")

        pasos = []
        for i in range(m):
            for j in range(p):
                sumandos = []
                for k in range(n):
                    a = A[i][k]
                    b = B[k][j]
                    sumandos.append(f"{self._fmt_latex(a)} \\times {self._fmt_latex(b)}")
                suma_str = " + ".join(sumandos)
                c = C[i][j]
                pasos.append(
                    f"\\(c_{{{i+1},{j+1}}} = {suma_str} = {self._fmt_latex(c)}\\)"
                )

        partes.append("<p>" + "<br>".join(pasos) + "</p>")

        return "\n".join(partes)
    def _procedimiento_traspuesta(self, A, AT):
        """
        Devuelve un string HTML con LaTeX mostrando el procedimiento de la traspuesta AT = A^T.
        """
        m = len(A)
        n = len(A[0]) if m > 0 else 0

        partes = []
        partes.append("<h3>Procedimiento: Traspuesta de una matriz</h3>")

        # Mostrar A y AT
        partes.append(
            f"<p>\\[ A = {self._matriz_a_latex(A)} \\]</p>"
        )
        partes.append(
            f"<p>\\[ A^T = {self._matriz_a_latex(AT)} \\]</p>"
        )

        partes.append("<p>Elementos de \\(A^T\\):</p>")

        pasos = []
        for i in range(m):
            for j in range(n):
                a = A[i][j]
                pasos.append(
                    f"\\(a^T_{{{j+1},{i+1}}} = a_{{{i+1},{j+1}}} = {self._fmt_latex(a)}\\)"
                )

        partes.append("<p>" + "<br>".join(pasos) + "</p>")

        return "\n".join(partes)
    def _procedimiento_inversa(self, A, A_inv):
        """
        Devuelve un string HTML con LaTeX mostrando el procedimiento de la inversa A_inv = A^(-1).
        """
        partes = []
        partes.append("<h3>Procedimiento: Inversa de una matriz</h3>")

        # Mostrar A y A_inv
        partes.append(
            f"<p>\\[ A = {self._matriz_a_latex(A)} \\]</p>"
        )
        partes.append(
            f"<p>\\[ A^{{-1}} = {self._matriz_a_latex(A_inv)} \\]</p>"
        )

        partes.append("<p>El procedimiento detallado de cálculo de la inversa se omite en esta versión.</p>")

        return "\n".join(partes)
    
    # ===============================================================
        

    def _set_html_content(self, html):
        self.procedimiento_web.setHtml(HTML_MATHJAX_TEMPLATE.format(content=html))

    def mostrar_procedimiento(self, _ignored=None, latex=None):
        if latex is None:
            latex = "<p>Sin contenido.</p>"
        self._set_html_content(latex)

    def leer_tabla(self, t):
        M = []
        for i in range(t.rowCount()):
            fila = []
            for j in range(t.columnCount()):
                try:
                    fila.append(Fraction(t.item(i, j).text()))
                except:
                    fila.append(Fraction(0))
            M.append(fila)
        return M
    # ===============================================================
    #             ACTUALIZAR DIMENSIONES DE LAS TABLAS
    # ===============================================================
    def actualizar_dimensiones(self):
        try:
            fA = int(self.filas_A_input.text())
            cA = int(self.columnas_A_input.text())
            fB = int(self.filas_B_input.text())
            cB = int(self.columnas_B_input.text())
        except:
            return
        # Actualizar tabla A
        self.tabla_A.setRowCount(fA)
        self.tabla_A.setColumnCount(cA)
        self._config_tabla(self.tabla_A)
        #Actualizar tabla B
        self.tabla_B.setRowCount(fB)
        self.tabla_B.setColumnCount(cB)
        self._config_tabla(self.tabla_B)
        
        ancho_columna_B = 250   # prueba 250–300
        for j in range(cB):
              self.tabla_B.setColumnWidth(j, ancho_columna_B)

         # 👇 Forzar columnas anchas para que haya scroll
        ancho_columna_A = 250   # prueba 250–300
        for j in range(cA):
          self.tabla_A.setColumnWidth(j, ancho_columna_A)



    # ===============================================================
    #             MOSTRAR / OCULTAR MATRIZ B AUTOMÁTICO
    # ===============================================================
    def _toggle_matrizB(self):
        solo_A = self.operacion_combo.currentText() in {
            "Traspuesta", "Gauss", "Gauss-Jordan", "Inversa"
        }
        self.b_widget.setVisible(not solo_A)


    # ===============================================================
    #                     LIMPIAR AMBAS MATRICES
    # ===============================================================
    def limpiar_matrices(self):
        for tabla in (self.tabla_A, self.tabla_B):
            for i in range(tabla.rowCount()):
                for j in range(tabla.columnCount()):
                    it = QTableWidgetItem("0")
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tabla.setItem(i, j, it)

        self.mostrar_procedimiento("", "<p class='card'>Matrices reiniciadas.</p>")


    # ===============================================================
    #            CONVERTIDOR ECUACIONES → MATRIZ A (Material)
    # ===============================================================
    # ===============================================================
    #            CONVERTIDOR ECUACIONES → MATRICES (Material)
    # ===============================================================
    def _abrir_convertidor_ecuaciones(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Convertidor de ecuaciones → Matrices")

        layout = QVBoxLayout(dlg)

        # --- Texto explicativo ---
        info = QLabel(
            "Introduce ecuaciones (acepta x, y, z, a1, b2...).\n"
            "Ejemplo:\n"
            "x + 2y - z = 8\n"
            "2x + y = 5\n"
            "3x + y + 4z = 12"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # --- Entrada de ecuaciones ---
        eq_edit = QTextEdit()
        eq_edit.setMinimumHeight(120)
        eq_edit.setStyleSheet("""
            QTextEdit {
                background:white;
                border:2px solid #CFD8DC;
                border-radius:8px;
                padding:8px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
            }
        """)
        layout.addWidget(eq_edit)

        # --- Salida / previsualización ---
        out = QPlainTextEdit()
        out.setReadOnly(True)
        out.setMinimumHeight(120)
        out.setStyleSheet("""
            QPlainTextEdit {
                background:white;
                border:2px solid #CFD8DC;
                border-radius:8px;
                padding:8px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
            }
        """)
        layout.addWidget(out)

        # --- Botones ---
        btns = QHBoxLayout()
        b_convert = QPushButton("Convertir")
        b_send_A = QPushButton("Enviar a Matriz A")
        b_send_B = QPushButton("Enviar a Matriz B")
        b_close = QPushButton("Cerrar")

        for b in (b_convert, b_send_A, b_send_B, b_close):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background:#1E88E5;
                    color:white;
                    padding:8px 14px;
                    border-radius:10px;
                }
                QPushButton:hover { background:#1565C0; }
            """)

        btns.addWidget(b_convert)
        btns.addWidget(b_send_A)
        btns.addWidget(b_send_B)
        btns.addWidget(b_close)
        layout.addLayout(btns)

        # ------------ Lógica convertir --------------
        def convertir():
            try:
                A, b_vec = self._ecuaciones_a_matriz(eq_edit.toPlainText())
                filas = [
                    f"[ {'  '.join(self._fmt(x) for x in fila)} | {self._fmt(b_vec[i])} ]"
                    for i, fila in enumerate(A)
                ]
                out.setPlainText("\n".join(filas))
            except Exception as e:
                out.setPlainText(f"Error: {e}")

        # ------------ Enviar a matriz A (matriz aumentada [A|b]) --------------
        def enviar_A():
            try:
                A, b_vec = self._ecuaciones_a_matriz(eq_edit.toPlainText())
                f = len(A)
                c = len(A[0]) + 1  # última columna = términos independientes

                self.filas_A_input.setText(str(f))
                self.columnas_A_input.setText(str(c))
                self.actualizar_dimensiones()

                for i in range(f):
                    for j in range(c - 1):
                        self.tabla_A.setItem(
                            i, j, QTableWidgetItem(self._fmt(A[i][j]))
                        )
                    self.tabla_A.setItem(
                        i, c - 1, QTableWidgetItem(self._fmt(b_vec[i]))
                    )

                # LaTeX de la matriz aumentada
                aumentada = [fila + [b_vec[i]] for i, fila in enumerate(A)]
                latex = (
                    "<h2>Matriz aumentada [A|b]</h2>"
                    "<div class='card'>"
                    f"$${self._matriz_a_latex(aumentada)}$$"
                    "</div>"
                )

                self.mostrar_procedimiento("", latex)
                dlg.accept()
            except Exception as e:
                out.setPlainText(f"Error: {e}")

        # ------------ Enviar a matrices A y B (A y vector columna b) --------------
        def enviar_B():
            try:
                A, b_vec = self._ecuaciones_a_matriz(eq_edit.toPlainText())
                f = len(A)
                cA = len(A[0])

                # Dimensiones: A = f x cA, B = f x 1
                self.filas_A_input.setText(str(f))
                self.columnas_A_input.setText(str(cA))
                self.filas_B_input.setText(str(f))
                self.columnas_B_input.setText("1")
                self.actualizar_dimensiones()

                # Rellenar A
                for i in range(f):
                    for j in range(cA):
                        self.tabla_A.setItem(
                            i, j, QTableWidgetItem(self._fmt(A[i][j]))
                        )

                # Rellenar B (vector columna)
                for i in range(f):
                    self.tabla_B.setItem(
                        i, 0, QTableWidgetItem(self._fmt(b_vec[i]))
                    )

                # LaTeX bonito: A y b lado a lado
                latexA = self._matriz_a_latex(A)
                latexB = self._matriz_a_latex([[bi] for bi in b_vec])
                latex = (
                    "<h2>Matriz de coeficientes A y vector b</h2>"
                    "<div class='card'>"
                    f"$${latexA} \\qquad {latexB}$$"
                    "</div>"
                )

                self.mostrar_procedimiento("", latex)
                dlg.accept()
            except Exception as e:
                out.setPlainText(f"Error: {e}")

        # Conexiones
        b_convert.clicked.connect(convertir)
        b_send_A.clicked.connect(enviar_A)
        b_send_B.clicked.connect(enviar_B)
        b_close.clicked.connect(dlg.accept)

        dlg.resize(520, 500)
        dlg.exec()


        # ======================================================
        #        Funciones internas del diálogo
        # ======================================================

        def convertir():
            """Solo muestra la matriz [A | b] en texto plano."""
            try:
                A, b = self._ecuaciones_a_matriz(eq_edit.toPlainText())
                filas = []
                for i, fila in enumerate(A):
                    coef_str = "  ".join(self._fmt(x) for x in fila)
                    filas.append(f"[ {coef_str} | {self._fmt(b[i])} ]")
                out.setPlainText("\n".join(filas))
            except Exception as e:
                out.setPlainText(f"Error: {e}")

        def enviar_a_matriz_A():
            """
            Envía SOLO los coeficientes a Matriz A.
            Matriz A queda de tamaño (n x m) donde m = #variables.
            """
            try:
                A, b = self._ecuaciones_a_matriz(eq_edit.toPlainText())
                f = len(A)
                c = len(A[0])

                # Actualizar dimensiones de A
                self.filas_A_input.setText(str(f))
                self.columnas_A_input.setText(str(c))
                self.actualizar_dimensiones()

                # Rellenar tabla A con coeficientes
                for i in range(f):
                    for j in range(c):
                        self.tabla_A.setItem(
                            i, j,
                            QTableWidgetItem(self._fmt(A[i][j]))
                        )

                dlg.accept()
            except Exception as e:
                out.setPlainText(f"Error al enviar a Matriz A: {e}")

        def enviar_a_matriz_B():
            """
            Envía SOLO el vector de términos independientes a Matriz B
            como un vector columna (n x 1).
            """
            try:
                A, b = self._ecuaciones_a_matriz(eq_edit.toPlainText())
                f = len(b)

                # Actualizar dimensiones de B (f x 1)
                self.filas_B_input.setText(str(f))
                self.columnas_B_input.setText("1")
                self.actualizar_dimensiones()

                # Rellenar tabla B con b
                for i in range(f):
                    self.tabla_B.setItem(
                        i, 0,
                        QTableWidgetItem(self._fmt(b[i]))
                    )

                dlg.accept()
            except Exception as e:
                out.setPlainText(f"Error al enviar a Matriz B: {e}")

        # Conexión de señales
        b_convert.clicked.connect(convertir)
        b_send_A.clicked.connect(enviar_a_matriz_A)
        b_send_B.clicked.connect(enviar_a_matriz_B)
        b_close.clicked.connect(dlg.accept)
        

        dlg.resize(520, 500)
        dlg.exec()



        # ===============================================================
        #        PARSEAR ECUACIONES A MATRIZ (acepta x, y, z, a1...)
        # ===============================================================
        def _ecuaciones_a_matriz(self, texto):
            lineas = [l.strip() for l in texto.splitlines() if l.strip()]
            if not lineas:
                raise ValueError("No hay ecuaciones.")

            todas_variables = []
            ecuaciones = []

            for ln in lineas:
                if "=" in ln:
                    left, right = ln.split("=")
                else:
                    left, right = ln, "0"

                L, constL, varsL = self._parse_expr_vars_y_const(left)
                R, constR, varsR = self._parse_expr_vars_y_const(right)

                for v in varsL + varsR:
                    if v not in todas_variables:
                        todas_variables.append(v)

                coefs = {v: L.get(v, 0) - R.get(v, 0) for v in set(L) | set(R)}
                ecuaciones.append((coefs, constR - constL))

            A, b = [], []
            for coef, cte in ecuaciones:
                fila = [coef.get(v, Fraction(0)) for v in todas_variables]
                A.append(fila)
                b.append(cte)

            return A, b


        def _parse_expr_vars_y_const(self, expr):
            # Variables tipo: x, y, z, a1, b2...
            pat = re.compile(r'([+\-]?)(\d+(?:/\d+)?)?\*?([A-Za-z]\w*)')

            coefs = {}
            vars_ = []
            spans = []

            for m in pat.finditer(expr):
                sign = -1 if m.group(1) == '-' else 1
                coef = Fraction(m.group(2)) if m.group(2) else Fraction(1)
                var  = m.group(3)

                coefs[var] = coefs.get(var, 0) + sign * coef
                vars_.append(var)
                spans.append((m.start(), m.end()))

            resto = re.sub(pat, "", expr)
            const = Fraction(0)

            for sign, num in re.findall(r'([+\-]?)(\d+(?:/\d+)?)', resto):
                val = Fraction(num)
                const += (-val if sign == '-' else val)

            return coefs, const, vars_
    # ===============================================================
    #        PARSEAR ECUACIONES A MATRIZ (acepta x, y, z, a1, b2...)
    # ===============================================================
    def _ecuaciones_a_matriz(self, texto: str):
        """
        Recibe un bloque de texto con ecuaciones lineales y devuelve:
          A: matriz de coeficientes  (lista de listas de Fraction)
          b: vector de términos independientes (lista de Fraction)

        Ejemplo de entrada:
            x + 2y - z = 8
            2x + y = 5
            3x + y + 4z = 12
        """
        # Limpiar líneas vacías
        lineas = [l.strip() for l in texto.splitlines() if l.strip()]
        if not lineas:
            raise ValueError("No hay ecuaciones.")

        todas_variables = []   # orden de variables (x, y, z, a1, ...)
        ecuaciones = []        # lista de (dic_coefs, constante)

        for ln in lineas:
            # Separar lado izquierdo y derecho
            if "=" in ln:
                left, right = ln.split("=", 1)
            else:
                left, right = ln, "0"

            # Parsear cada lado
            L, constL, varsL = self._parse_expr_vars_y_const(left)
            R, constR, varsR = self._parse_expr_vars_y_const(right)

            # Acumular variables encontradas
            for v in varsL + varsR:
                if v not in todas_variables:
                    todas_variables.append(v)

            # Pasar todo al lado izquierdo: L - R = 0  →  (coefs)·x = const
            coefs = {v: L.get(v, Fraction(0)) - R.get(v, Fraction(0))
                     for v in set(L) | set(R)}
            ecuaciones.append((coefs, constR - constL))

        # Construir A y b en el orden de todas_variables
        A, b = [], []
        for coefs, cte in ecuaciones:
            fila = [coefs.get(v, Fraction(0)) for v in todas_variables]
            A.append(fila)
            b.append(cte)

        return A, b
    def _parse_expr_vars_y_const(self, expr: str):
        """
        Dada una expresión tipo '2x-3y+4' devuelve:
          coefs: {'x': 2, 'y': -3}
          const: 4   (Fraction)
          vars_: ['x', 'y']
        Acepta variables tipo: x, y, z, a1, b2, var3, etc.
        """
        # Quitamos espacios para simplificar
        expr = expr.replace(" ", "")

        # patrón: signo opcional, coeficiente opcional, *, nombre_variable
        pat = re.compile(r'([+\-]?)(\d+(?:/\d+)?)?\*?([A-Za-z]\w*)')

        coefs = {}
        vars_ = []
        spans = []

        # Buscar todos los términos con variable
        for m in pat.finditer(expr):
            sign = -1 if m.group(1) == '-' else 1
            coef = Fraction(m.group(2)) if m.group(2) else Fraction(1)
            var = m.group(3)

            coefs[var] = coefs.get(var, Fraction(0)) + sign * coef
            vars_.append(var)
            spans.append((m.start(), m.end()))

        # El resto de la expresión (sin términos con variable) son constantes
        resto = re.sub(pat, "", expr)
        const = Fraction(0)

        # Capturamos cosas tipo +5, -3, +10/7...
        for sign, num in re.findall(r'([+\-]?)(\d+(?:/\d+)?)', resto):
            val = Fraction(num)
            const += -val if sign == '-' else val

        return coefs, const, vars_
    def _a_fracciones(self, M):
        """
        Convierte todos los elementos de la matriz M a Fraction.
        Acepta enteros, floats, Fraction y strings tipo '3/5', '2', '1,5', etc.
        """
        resultado = []
        for fila in M:
            nueva_fila = []
            for x in fila:
                try:
                    if isinstance(x, Fraction):
                        nueva_fila.append(x)
                    else:
                        # Pasar a string y normalizar coma decimal
                        s = str(x).strip().replace(",", ".")
                        nueva_fila.append(Fraction(s))
                except Exception:
                    nueva_fila.append(Fraction(0))
                resultado.append(nueva_fila)
        return resultado

    # ===============================================================
    #                          GAUSS
    # ===============================================================
    
    def _gauss_detallado(self, M):
        """
        Eliminación hacia adelante (Gauss) usando Fraction.
        Devuelve:
        - lista de pasos (html+latex)
        - matriz escalonada
        - lista de columnas de pivote
        """

        # Trabajar siempre con fracciones exactas
        A = self._a_fracciones(M)
        n, m = len(A), len(A[0])
        row = 0
        pivots = []
        pasos = []

        # SNAP — para escribir cada paso en una sola línea + matriz debajo
        def snap(texto, latex=None):
            """
            texto -> texto normal
            latex -> expresion LaTeX inline (opcional)
            """
            if latex:
                linea = f"<b>{texto}</b> \\( {latex} \\)"
            else:
                linea = f"<b>{texto}</b>"

            pasos.append(
                "<div class='step' style='margin-bottom:14px;'>"
                f"<p style='margin:0; padding:6px 0; font-size:17px;'>{linea}</p>"
                f"<div class='card' style='margin-top:6px;'>$${self._matriz_a_latex(A)}$$</div>"
                "</div>"
            )

        # Primer snapshot: matriz inicial
        snap("Matriz inicial")

        # ---------------------------------------------------------------------
        #                  RECORRIDO POR COLUMNAS PARA OBTENER PIVOTES
        # ---------------------------------------------------------------------
        for col in range(m):

            # Buscar pivote diferente de 0
            sel = None
            for r in range(row, n):
                if A[r][col] != 0:
                    sel = r
                    break

            # No hay pivote en esta columna → columna libre
            if sel is None:
                continue

            # Intercambio de filas
            if sel != row:
                A[row], A[sel] = A[sel], A[row]
                snap(f"Intercambiar F{row+1} ↔ F{sel+1}")

            # Normalizar pivote a 1
            piv = A[row][col]
            if piv != 1:
                A[row] = [x / piv for x in A[row]]
                snap(
                    f"Normalizar F{row+1} dividiendo por",
                    self._fmt_latex(piv)
                )

            # Eliminar filas debajo
            for r in range(row + 1, n):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor * A[row][j] for j in range(m)]
                    snap(
                        f"F{r+1} → F{r+1} -",
                        f"{self._fmt_latex(factor)} \\cdot F{row+1}"
                    )

            pivots.append(col)
            row += 1
            if row == n:
                break

        return pasos, A, pivots

        """
        Eliminación hacia adelante (Gauss) usando Fraction.
        Devuelve:
        - lista de pasos (html+latex)
        - matriz escalonada
        - lista de columnas de pivote
        """
        # Trabajar SIEMPRE con fracciones exactas
        A = self._a_fracciones(M)
        n, m = len(A), len(A[0])
        row = 0
        pivots = []
        pasos = []

        # SNAP — tarjeta + matriz actual
        def snap(html_texto):
            if html_texto is None:
                html_texto = ""
            pasos.append(
                "<div class='step'>"
                f"<p><b>{html_texto}</b></p>"
                f"<div class='card'>$${self._matriz_a_latex(A)}$$</div>"
                "</div>"
            )

        snap("Matriz inicial")

        # ---------------------------------------------------------------------
        #                 RECORRIDO POR COLUMNAS PARA OBTENER PIVOTES
        # ---------------------------------------------------------------------
        for col in range(m):

            # ------------ BUSCAR PIVOTE != 0 ------------
            sel = None
            for r in range(row, n):
                if A[r][col] != 0:
                    sel = r
                    break

            # No hay pivote en esta columna → columna libre
            if sel is None:
                continue

            # ------------ INTERCAMBIO DE FILAS ------------
            if sel != row:
                A[row], A[sel] = A[sel], A[row]
                snap(f"Intercambiar F{row+1} ↔ F{sel+1}")

            # ------------ NORMALIZAR PIVOTE A 1 ------------
            piv = A[row][col]
            if piv != 1:
                A[row] = [x / piv for x in A[row]]
                snap(
                    f"Normalizar F{row+1} dividiendo por $$ {self._fmt_latex(piv)} $$"
                )

            # ------------ ELIMINAR FILAS DEBAJO ------------
            for r in range(row + 1, n):
                factor = A[r][col]
                if factor != 0:
                    A[r] = [A[r][j] - factor * A[row][j] for j in range(m)]
                    snap(
                        f"F{r+1} → F{r+1} - $$ {self._fmt_latex(factor)} $$ · F{row+1}"
                    )

            pivots.append(col)
            row += 1
            if row == n:
                break

        return pasos, A, pivots




    # ===============================================================
    #                        BACK ELIMINATION
    # ===============================================================
    def _back_gauss(self, A, pivots):
        """
        Fase hacia atrás (Gauss-Jordan) usando Fraction.
        A debe venir de _gauss_detallado con pivotes ya en 1.
        Devuelve:
            - lista de pasos HTML+LaTeX
            - matriz reducida final
        """

        # Copia segura en fracciones exactas
        R = self._a_fracciones(A)
        pasos = []
        n, m = len(R), len(R[0])

        # SNAP — texto + LaTeX inline + matriz debajo
        def snap(texto, latex=None):
            """
            texto -> texto normal
            latex -> expresión LaTeX inline opcional
            """
            if latex:
                linea = f"<b>{texto}</b> \\( {latex} \\)"
            else:
                linea = f"<b>{texto}</b>"

            pasos.append(
                "<div class='step' style='margin-bottom:14px;'>"
                f"<p style='margin:0; padding:6px 0; font-size:17px;'>{linea}</p>"
                f"<div class='card' style='margin-top:6px;'>$${self._matriz_a_latex(R)}$$</div>"
                "</div>"
            )

        snap("Inicio de la fase hacia atrás")

        # Procesamos las filas con pivote de abajo hacia arriba
        for r in reversed(range(len(pivots))):
            c = pivots[r]

            # Obtener el pivote actual
            piv = R[r][c]

            # Asegurar que pivote = 1
            if piv != 0 and piv != 1:
                R[r] = [x / piv for x in R[r]]
                snap(
                    f"Normalizar F{r+1} dividiendo por",
                    self._fmt_latex(piv)
                )

            # Eliminar por encima del pivote
            for up in range(r):
                factor = R[up][c]
                if factor != 0:
                    R[up] = [R[up][j] - factor * R[r][j] for j in range(m)]
                    snap(
                        f"F{up+1} → F{up+1} -",
                        f"{self._fmt_latex(factor)} \\cdot F{r+1}"
                    )

        return pasos, R


    def _a_fracciones(self, M):
        """
        Devuelve una copia de M donde cada elemento es Fraction.
        Acepta int, float, str, etc.
        """
        out = []
        for fila in M:
            nueva = []
            for x in fila:
                if isinstance(x, Fraction):
                    nueva.append(x)
                else:
                    nueva.append(Fraction(x))
            out.append(nueva)
        return out


    # ===============================================================
    #                  DIAGNÓSTICO DEL SISTEMA (Gauss)
    # ===============================================================
        # ===============================================================
    #      DIAGNÓSTICO DEL SISTEMA: PIVOTES, LIBRES, DEPENDENCIA
    # ===============================================================
    def _diagnostico(self, A):
        """
        A se asume en forma escalonada reducida (RREF) de una matriz aumentada [A|b].
        Devuelve HTML con:
        - Sistema inconsistente / único / infinitas
        - Columnas pivote
        - Variables libres
        - Comentario de dependencia lineal
        - Ecuaciones en notación LaTeX (bien renderizadas)
        """
        if not A or not A[0]:
            return "<div class='card'>Matriz vacía.</div>"

        n, m = len(A), len(A[0])
        NV = m - 1  # número de variables (última columna = término independiente)

        # --------- 1) Encontrar columnas pivote  ---------
        pivot_cols = []
        row_for_pivot = {}

        for r in range(n):
            first = None
            for c in range(NV):
                if A[r][c] != 0:
                    first = c
                    break
            if first is not None and first not in pivot_cols:
                pivot_cols.append(first)
                row_for_pivot[first] = r

        free_cols = [c for c in range(NV) if c not in pivot_cols]

        # Columnas pivote en una sola línea
        if pivot_cols:
            pivotes_str = ", ".join(f"x_{c+1}" for c in pivot_cols)
        else:
            pivotes_str = "Ninguna (no hay pivotes)."

        # Variables libres en formato VERTICAL
        if free_cols:
            libres_vertical = "<br>".join(
                f"x_{c+1} = variable libre" for c in free_cols
            )
        else:
            libres_vertical = "No hay variables libres."

        # --------- 2) Dependencia lineal  ---------
        if free_cols:
            dep_str = (
                "Sí hay <b>dependencia lineal</b>: el número de columnas pivote es "
                "menor que el número de variables."
            )
        else:
            dep_str = (
                "No hay <b>dependencia lineal</b> entre las columnas de la matriz de "
                "coeficientes: todas las variables son básicas."
            )

        # --------- 3) Comprobar inconsistencia  ---------
        inconsistente = False
        for r in range(n):
            if all(A[r][c] == 0 for c in range(NV)) and A[r][-1] != 0:
                inconsistente = True
                break

        if inconsistente:
            html = "<div class='card'>"
            html += "<b>❌ Sistema inconsistente</b><br><br>"
            html += (
                "Existe al menos una fila del tipo 0 = b, con b ≠ 0, "
                "por lo que el sistema no tiene solución.<br><br>"
            )
            html += f"<b>Columnas pivote:</b> {pivotes_str}<br>"
            html += "<b>Variables libres:</b><br>"
            html += f"{libres_vertical}<br>"
            html += f"<br><b>Dependencia:</b> {dep_str}"
            html += "</div>"
            return html

        # ================= SOLUCIÓN ÚNICA =================
        if len(pivot_cols) == NV:
            sol = [None] * NV
            for c in pivot_cols:
                r = row_for_pivot[c]
                sol[c] = A[r][-1]

            html = "<div class='card'>"
            html += "<b>✅ Sistema compatible determinado (solución única)</b><br><br>"
            html += f"<b>Columnas pivote:</b> {pivotes_str}<br>"
            html += "<b>Variables libres:</b><br>"
            html += f"{libres_vertical}<br>"
            html += f"<br><b>Dependencia:</b> {dep_str}<br><br>"
            html += "<b>Solución:</b><br>"

            html += "<ul>"
            for i, v in enumerate(sol):
                ecuacion = f"x_{i+1} = {self._fmt_latex(v)}"
                html += f"<li>$$ {ecuacion} $$</li>"
            html += "</ul></div>"

            return html

        # ================= INFINITAS SOLUCIONES =================
        html = "<div class='card'>"
        html += "<b>✅ Sistema compatible indeterminado (infinitas soluciones)</b><br><br>"
        html += f"<b>Columnas pivote:</b> {pivotes_str}<br>"
        html += "<b>Variables libres:</b><br>"
        html += f"{libres_vertical}<br>"
        html += f"<br><b>Dependencia:</b> {dep_str}<br>"

        if free_cols:
            html += "<br><b>Representación paramétrica (esquema):</b>"

            html += "<ul>"
            # Ecuaciones de variables básicas en función de las libres (sin t_1, t_2...)
            for c_piv in pivot_cols:
                r = row_for_pivot[c_piv]
                rhs = A[r][-1]

                expr = f"x_{c_piv+1} = {self._fmt_latex(rhs)}"
                for c_free in free_cols:
                    coef = A[r][c_free]
                    if coef != 0:
                        sign = "-" if coef > 0 else "+"
                        mag = self._fmt_latex(abs(coef))
                        # usamos directamente la variable libre x_{c_free+1}
                        expr += f" {sign} {mag}\\cdot x_{c_free+1}"

                html += f"<li>$$ {expr} $$</li>"

            # Variables libres: se muestran como "variable libre"
            for c_free in free_cols:
                expr = f"x_{c_free+1} = \\text{{variable libre}}"
                html += f"<li>$$ {expr} $$</li>"

            html += "</ul>"

        html += "</div>"
        return html


   
    
    





    # ===============================================================
    #                  EJECUTAR OPERACIÓN
    # ===============================================================
    def ejecutar_operacion(self):
        op = self.operacion_combo.currentText()
        A = self.leer_tabla(self.tabla_A)
        B = self.leer_tabla(self.tabla_B)

        try:
            # ---------------- SUMA ----------------
            if op == "Suma":
                C = [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                latex = self._procedimiento_suma(A, B, C)
                self.mostrar_procedimiento("", latex)

            # ---------------- RESTA ----------------
            elif op == "Resta":
                C = [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
                latex = self._procedimiento_resta(A, B, C)
                self.mostrar_procedimiento("", latex)

            # ---------------- MULTIPLICACIÓN ----------------
            elif op == "Multiplicacion":
                if len(A[0]) != len(B):
                    raise ValueError(" Número de columnas de A debe ser igual a número de filas de B.")
                C = [
                    [sum(A[i][k] * B[k][j] for k in range(len(B)))
                     for j in range(len(B[0]))]
                    for i in range(len(A))
                ]
                latex = self._procedimiento_multiplicacion(A, B, C)
                self.mostrar_procedimiento("", latex)

            # ---------------- TRASPUESTA ----------------
            elif op == "Traspuesta":
                T = [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]
                latex = self._procedimiento_traspuesta(A, T)
                self.mostrar_procedimiento("", latex)

            # ---------------- GAUSS ----------------
            elif op == "Gauss":
                pasos_fwd, escalonada, pivots = self._gauss_detallado(A)
                latex = "<h2>Gauss</h2>" + "".join(pasos_fwd)
                latex += "<h3>Resultado Escalonada</h3><div class='card'>"
                latex += f"$${self._matriz_a_latex(escalonada)}$$</div>"
                latex += self._diagnostico(escalonada)
                self.mostrar_procedimiento("", latex)

            # ---------------- GAUSS-JORDAN ----------------
            elif op == "Gauss-Jordan":
                pasos_fwd, escalonada, pivots = self._gauss_detallado(A)
                pasos_back, rref = self._back_gauss(escalonada, pivots)
                latex = "<h2>Gauss-Jordan</h2>" + "".join(pasos_fwd + pasos_back)
                latex += "<h3>Resultado RREF</h3><div class='card'>"
                latex += f"$${self._matriz_a_latex(rref)}$$</div>"
                latex += self._diagnostico(rref)
                self.mostrar_procedimiento("", latex)

            # ---------------- INVERSA ----------------
            elif op == "Inversa":
                latex, inv = self._inversa_detallada(A)
                self.mostrar_procedimiento(latex=latex)
                

        except Exception as e:
            self.mostrar_procedimiento("", f"<div class='card'>Error: {e}</div>")
    # ===============================================================
    #        INVERSA DE A (GAUSS–JORDAN SOBRE [A | I])
    # ===============================================================
    def _inversa(self, A):
        """
        Calcula la inversa de A usando Gauss–Jordan sobre la matriz aumentada [A | I].
        Devuelve la matriz inversa A^{-1} como lista de listas de Fraction.
        """
        n = len(A)
        if n == 0:
            raise ValueError("La matriz A está vacía.")
        if n != len(A[0]):
            raise ValueError("La matriz no es cuadrada; no tiene inversa.")

        # Construir [A | I]
        AI = [
            A[i][:] + [Fraction(int(i == j)) for j in range(n)]
            for i in range(n)
        ]

        # Gauss–Jordan sobre la aumentada
        for i in range(n):

            # Si el pivote es 0, buscar fila abajo
            if AI[i][i] == 0:
                swap = None
                for k in range(i + 1, n):
                    if AI[k][i] != 0:
                        swap = k
                        break
                if swap is None:
                    raise ValueError("La matriz no es invertible (det = 0).")
                AI[i], AI[swap] = AI[swap], AI[i]

            # Normalizar fila pivote
            piv = AI[i][i]
            if piv == 0:
                raise ValueError("La matriz no es invertible (pivote nulo).")
            AI[i] = [x / piv for x in AI[i]]

            # Hacer ceros arriba y abajo
            for r in range(n):
                if r == i:
                    continue
                factor = AI[r][i]
                if factor != 0:
                    AI[r] = [AI[r][j] - factor * AI[i][j] for j in range(2 * n)]

        # Extraer la parte derecha (I transformada en A^{-1})
        inv = [fila[n:] for fila in AI]
        return inv
    def _inversa_detallada(self, A):
        """
        Calcula la inversa de A usando Gauss–Jordan y genera
        un HTML+LaTeX con el procedimiento paso a paso.

        Devuelve (latex, inv)
        """
        n = len(A)
        if n == 0:
            raise ValueError("La matriz A está vacía.")
        if n != len(A[0]):
            raise ValueError("La matriz no es cuadrada; no tiene inversa.")

        # Construir [A | I] con Fraction
        AI = [
            [Fraction(x) for x in A[i]] +
            [Fraction(int(i == j)) for j in range(n)]
            for i in range(n)
        ]

        pasos = []

        def snap(descripcion):
            pasos.append(f"<div class='step'><b>{descripcion}</b></div>")
            pasos.append(
                "<div class='card'>$$" +
                self._matriz_a_latex(AI) +
                "$$</div>"
            )

        latex = "<h2>Inversa de A mediante Gauss–Jordan</h2>"

        # Mostrar A y [A | I] inicial
        latex += "<h3>Matriz A</h3>"
        latex += "<div class='card'>$$A = " + self._matriz_a_latex(A) + "$$</div>"

        latex += "<h3>Matriz aumentada inicial [A \\mid I]</h3>"
        snap("Matriz aumentada inicial [A \\mid I]")

        # Gauss–Jordan sobre la aumentada
        for i in range(n):

            # Si el pivote es 0, buscar fila abajo
            if AI[i][i] == 0:
                swap = None
                for k in range(i + 1, n):
                    if AI[k][i] != 0:
                        swap = k
                        break
                if swap is None:
                    raise ValueError("La matriz no es invertible (det = 0).")
                AI[i], AI[swap] = AI[swap], AI[i]
                snap(f"Intercambiamos fila {i+1} con fila {swap+1} para obtener pivote distinto de 0")

            # Normalizar fila pivote
            piv = AI[i][i]
            if piv == 0:
                raise ValueError("La matriz no es invertible (pivote nulo).")
            AI[i] = [x / piv for x in AI[i]]
            snap(f"Normalizamos la fila {i+1} dividiendo por el pivote {self._fmt_latex(piv)}")

            # Hacer ceros arriba y abajo
            for r in range(n):
                if r == i:
                    continue
                factor = AI[r][i]
                if factor != 0:
                    AI[r] = [AI[r][j] - factor * AI[i][j] for j in range(2 * n)]
            snap(f"Anulamos los elementos de la columna {i+1} por encima y por debajo del pivote")

        # Extraer la parte derecha (I transformada en A^{-1})
        inv = [fila[n:] for fila in AI]

        latex += "".join(pasos)

        latex += "<h3>Resultado final</h3>"
        latex += "<p>La matriz aumentada ha quedado como \\([I \\mid A^{-1}]\\). "
        latex += "La parte derecha es la inversa buscada:</p>"
        latex += "<div class='card'>$$A^{-1} = " + self._matriz_a_latex(inv) + "$$</div>"

        return latex, inv


# ===============================================================
#                   MAIN DE PRUEBA
# ===============================================================
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    ventana = VentanaMatrices()
    ventana.show()

    sys.exit(app.exec())

