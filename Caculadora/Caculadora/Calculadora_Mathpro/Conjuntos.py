
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGridLayout, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Matplotlib & Venn
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
try:
    from matplotlib_venn import venn2
except ImportError:
    venn2 = None

# ===============================================================
#                  PLANTILLA HTML (AZUL)
# ===============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
    body {{ font-family: 'Segoe UI', sans-serif; background-color: #ffffff; color: #333; padding: 10px; }}
    .card {{ 
        background: #f0f7ff; /* Azul muy pálido */
        border-left: 5px solid #1E88E5; /* AZUL PRINCIPAL */
        padding: 15px; 
        margin-bottom: 15px; 
        border-radius: 5px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    h3 {{ color: #1565C0; border-bottom: 1px solid #BBDEFB; padding-bottom: 5px; margin-top: 0; }}
    p {{ font-size: 1.1em; line-height: 1.6; }}
    .empty {{ color: #999; font-style: italic; }}
</style>
</head>
<body>
{content}
</body>
</html>
"""

class CalculadoraConjuntos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Conjuntos - MathPro")
        # Fondo gris azulado muy suave
        self.setStyleSheet("background-color: #ECEFF1; color: #263238;")
        
        if venn2 is None:
            QMessageBox.critical(self, "Error", "Falta la librería 'matplotlib-venn'.\nInstálala con: pip install matplotlib-venn")

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ==========================================
        #  PANEL IZQUIERDO (Entradas y Botones)
        # ==========================================
        left_card = QFrame()
        left_card.setStyleSheet("""
            QFrame { background-color: white; border-radius: 15px; border: 1px solid #CFD8DC; }
        """)
        left_card.setFixedWidth(380)
        l_layout = QVBoxLayout(left_card)
        l_layout.setSpacing(15)

        title = QLabel("Definición de Conjuntos")
        # Azul fuerte para el título
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1565C0; border: none;")
        l_layout.addWidget(title)

        # Inputs
        l_layout.addWidget(QLabel("Conjunto A (separar por comas):", objectName="lbl"))
        self.input_a = QLineEdit()
        self.input_a.setPlaceholderText("Ej: 1, 2, 3, 4")
        self._estilar_input(self.input_a)
        l_layout.addWidget(self.input_a)

        l_layout.addWidget(QLabel("Conjunto B (separar por comas):", objectName="lbl"))
        self.input_b = QLineEdit()
        self.input_b.setPlaceholderText("Ej: 3, 4, 5, 6")
        self._estilar_input(self.input_b)
        l_layout.addWidget(self.input_b)

        l_layout.addSpacing(10)
        
        # Grid de Botones
        lbl_ops = QLabel("Operaciones")
        lbl_ops.setStyleSheet("font-weight: bold; font-size: 14px; border: none; color: #455A64;")
        l_layout.addWidget(lbl_ops)

        grid_btns = QGridLayout()
        grid_btns.setSpacing(10)

        # --- COLORES AZULES ---
        # Principal: #1E88E5 (Azul Material)
        # Secundario: #546E7A (Gris Azulado)
        # Acento: #039BE5 (Azul Claro)
        
        btn_union = self._crear_boton("Unión (A ∪ B)", "#1E88E5")
        btn_inter = self._crear_boton("Intersección (A ∩ B)", "#1E88E5")
        btn_diff_a = self._crear_boton("Diferencia (A - B)", "#546E7A")
        btn_diff_b = self._crear_boton("Diferencia (B - A)", "#546E7A")
        btn_sim   = self._crear_boton("Dif. Simétrica (A Δ B)", "#546E7A")
        btn_clear = self._crear_boton("Limpiar Todo", "#B0BEC5") # Gris claro para limpiar

        # Conexiones
        btn_union.clicked.connect(lambda: self.calcular("union"))
        btn_inter.clicked.connect(lambda: self.calcular("intersection"))
        btn_diff_a.clicked.connect(lambda: self.calcular("diff_ab"))
        btn_diff_b.clicked.connect(lambda: self.calcular("diff_ba"))
        btn_sim.clicked.connect(lambda: self.calcular("symmetric"))
        btn_clear.clicked.connect(self.limpiar)

        grid_btns.addWidget(btn_union, 0, 0)
        grid_btns.addWidget(btn_inter, 0, 1)
        grid_btns.addWidget(btn_diff_a, 1, 0)
        grid_btns.addWidget(btn_diff_b, 1, 1)
        grid_btns.addWidget(btn_sim, 2, 0, 1, 2)
        grid_btns.addWidget(btn_clear, 3, 0, 1, 2)

        l_layout.addLayout(grid_btns)
        l_layout.addStretch()
        
        # ==========================================
        #  PANEL DERECHO (Gráfico y Resultados)
        # ==========================================
        right_card = QFrame()
        right_card.setStyleSheet("QFrame { background-color: white; border-radius: 15px; border: 1px solid #CFD8DC; }")
        r_layout = QVBoxLayout(right_card)
        r_layout.setContentsMargins(5,5,5,5)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # 1. Gráfico Venn
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')
        
        graph_container = QWidget()
        gl = QVBoxLayout(graph_container)
        gl.addWidget(QLabel("Diagrama de Venn", alignment=Qt.AlignmentFlag.AlignCenter))
        gl.addWidget(self.canvas)
        
        # 2. Resultados Web (LaTeX)
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background: white;")
        self.web_view.page().setBackgroundColor(Qt.GlobalColor.white)

        splitter.addWidget(graph_container)
        splitter.addWidget(self.web_view)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        r_layout.addWidget(splitter)

        main_layout.addWidget(left_card)
        main_layout.addWidget(right_card)
        
        # Estado inicial
        self._set_html("<p style='text-align:center; color:#666;'>Ingresa los conjuntos y selecciona una operación.</p>")
        self.dibujar_venn_vacio()

    # ===============================================================
    #                  ESTILOS Y HELPERS UI
    # ===============================================================
    def _estilar_input(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                background-color: #FAFAFA; border: 2px solid #CFD8DC; border-radius: 8px;
                padding: 10px; color: #37474F; font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #29B6F6; background-color: white; }
        """)

    def _crear_boton(self, texto, color_bg):
        btn = QPushButton(texto)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Efecto hover oscureciendo un poco el color
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_bg}; color: white; border-radius: 8px; 
                padding: 12px; font-weight: bold; font-size: 13px; border: none;
            }}
            QPushButton:hover {{ background-color: {self._darken(color_bg)}; }}
            QPushButton:pressed {{ background-color: #263238; }}
        """)
        return btn
    
    def _darken(self, hex_color):
        # Simple función para oscurecer el color en hover
        if hex_color == "#1E88E5": return "#1565C0"
        if hex_color == "#546E7A": return "#455A64"
        return "#90A4AE"

    def _set_html(self, content):
        self.web_view.setHtml(HTML_TEMPLATE.format(content=content))

    # ===============================================================
    #                  LÓGICA MATEMÁTICA
    # ===============================================================
    def obtener_conjunto(self, texto):
        elementos = [e.strip() for e in texto.split(",") if e.strip()]
        conjunto = set()
        for e in elementos:
            try:
                if "." in e: val = float(e)
                else: val = int(e)
                conjunto.add(val)
            except:
                conjunto.add(e)
        return conjunto

    def formato_set_latex(self, s):
        if not s: return "\\emptyset"
        try:
            lista = sorted(list(s), key=lambda x: (isinstance(x, str), x))
        except:
            lista = list(s)
        return "\\{ " + ", ".join(map(str, lista)) + " \\}"

    # ===============================================================
    #                  CÁLCULOS Y GRÁFICOS
    # ===============================================================
    def calcular(self, operacion):
        txt_a = self.input_a.text()
        txt_b = self.input_b.text()

        if not txt_a and not txt_b:
            self._set_html("<div class='card'><b>Error:</b> Los conjuntos están vacíos.</div>")
            self.dibujar_venn_vacio()
            return

        A = self.obtener_conjunto(txt_a)
        B = self.obtener_conjunto(txt_b)

        res = set()
        latex_op = ""
        titulo = ""
        
        if operacion == "union":
            res = A | B
            latex_op = "A \\cup B"
            titulo = "Unión"
        elif operacion == "intersection":
            res = A & B
            latex_op = "A \\cap B"
            titulo = "Intersección"
        elif operacion == "diff_ab":
            res = A - B
            latex_op = "A - B"
            titulo = "Diferencia A - B"
        elif operacion == "diff_ba":
            res = B - A
            latex_op = "B - A"
            titulo = "Diferencia B - A"
        elif operacion == "symmetric":
            res = A ^ B
            latex_op = "A \\Delta B"
            titulo = "Diferencia Simétrica"

        # Generar HTML con color azul en la fórmula
        html_res = f"""
        <div class='card'>
            <h3>Operación: {titulo}</h3>
            <p><b>Conjunto A:</b> $${self.formato_set_latex(A)}$$</p>
            <p><b>Conjunto B:</b> $${self.formato_set_latex(B)}$$</p>
            <hr>
            <h4>Resultado:</h4>
            <p style='font-size: 1.3em; color: #1565C0;'>$$ {latex_op} = {self.formato_set_latex(res)} $$</p>
            <p><b>Cardinalidad:</b> |Resultado| = {len(res)}</p>
        </div>
        """
        self._set_html(html_res)
        self.dibujar_venn(A, B, operacion)

    def dibujar_venn(self, A, B, operacion):
        self.ax.clear()
        
        # Colores
        color_A = '#4FC3F7' # Celeste claro
        color_B = '#7986CB' # Indigo claro
        alpha_base = 0.3
        alpha_high = 0.9 # Más opaco para resaltar

        if not A and not B:
            self.ax.text(0.5, 0.5, "Conjuntos Vacíos", ha='center', va='center')
            self.canvas.draw()
            return

        try:
            v = venn2([A, B], set_labels=('A', 'B'), ax=self.ax)
        except:
            self.ax.text(0.5, 0.5, "Error al graficar", ha='center')
            self.canvas.draw()
            return

        if v is None: 
            self.ax.text(0.5, 0.5, "Sin gráfico", ha='center')
            self.canvas.draw()
            return

        for label in v.set_labels:
            if label: label.set_fontsize(12)
        for label in v.subset_labels:
            if label: label.set_fontsize(10)

        # Color base (apagado)
        for region in ['10', '01', '11']:
            patch = v.get_patch_by_id(region)
            if patch:
                if region == '10': patch.set_color(color_A)
                elif region == '01': patch.set_color(color_B)
                elif region == '11': patch.set_color('#5C6BC0')
                patch.set_alpha(alpha_base)

        # Resaltar selección
        highlight = []
        if operacion == "union": highlight = ['10', '01', '11']
        elif operacion == "intersection": highlight = ['11']
        elif operacion == "diff_ab": highlight = ['10']
        elif operacion == "diff_ba": highlight = ['01']
        elif operacion == "symmetric": highlight = ['10', '01']

        for region in highlight:
            patch = v.get_patch_by_id(region)
            if patch:
                patch.set_alpha(alpha_high)
                patch.set_edgecolor('#1A237E') # Borde azul oscuro
                patch.set_linewidth(2)

        self.canvas.draw()

    def dibujar_venn_vacio(self):
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Introduce datos para ver el gráfico", 
                     ha='center', va='center', color='#aaa', fontsize=12)
        self.canvas.draw()

    def limpiar(self):
        self.input_a.clear()
        self.input_b.clear()
        self.dibujar_venn_vacio()
        self._set_html("<p style='text-align:center;'>Datos limpiados.</p>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CalculadoraConjuntos()
    ventana.show()
    sys.exit(app.exec())
