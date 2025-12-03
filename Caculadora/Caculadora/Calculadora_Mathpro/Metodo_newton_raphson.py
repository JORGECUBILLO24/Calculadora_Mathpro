import sys
import re
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from sympy import sympify, diff, Symbol, latex

# Intentamos importar pandas para exportar (opcional)
try:
    import pandas as pd
except ImportError:
    pd = None
    

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog, QGraphicsDropShadowEffect,QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Matplotlib - Configuración
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

# =============================================================================
#  MOTOR MATEMÁTICO
# =============================================================================

# Busca esta sección en tu código y reemplázala completa:

CHAR_MAP = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '/': '⁄', '=': '⁼',
    '(': '⁽', ')': '⁾',
    
    # Variables y letras para funciones (ln, sen, cos, tan, log, exp, pi)
    'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 
    'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ', 
    'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 
    'p': 'ᵖ', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ', 
    'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ',
    
    # Mapeo especial para pi si quisieras escribirlo directo
    'π': 'pi' # Nota: no existe pi superíndice real en todas las fuentes, 
               # pero puedes usar 'ᴾ' si prefieres visualmente.
}

# (El resto de REVERSE_MAP y SUP_CHARS se actualiza solo porque dependen de este diccionario)
REVERSE_MAP = {v: k for k, v in CHAR_MAP.items()}
SUP_CHARS = "".join(CHAR_MAP.values())


def _transform_sup_de_python(sup_norm: str) -> str:
    """
    Interpreta el texto del exponente ya 'normalizado' desde superíndices.
    Soporta las variantes:
      - "-1/2"   -> -1/2        (signo fuera)
      - "1-/2"   -> (-1)/2      (signo dentro)
      - "-1-/2"  -> -(-1/2)     (dos signos)
      - con paréntesis: "-(-1/2)" se deja tal cual
    """
    sup_norm = sup_norm.strip()

    # Si tiene paréntesis, dejamos que SymPy lo entienda tal cual
    if "(" in sup_norm or ")" in sup_norm:
        return sup_norm

    if "/" not in sup_norm:
        return sup_norm

    num, den = sup_norm.split("/", 1)
    num = num.strip()
    den = den.strip()

    leading = num.startswith("-")
    trailing = num.endswith("-")
    core = num.strip("-").strip()

    if leading and trailing:
        # -1-  -> -(-1/den)
        return f"-(-{core})/{den}"
    elif leading:
        # -1   -> -(1/den)
        return f"-({core})/{den}"
    elif trailing:
        # 1-   -> (-1)/den
        return f"(-{core})/{den}"
    else:
        return f"{core}/{den}"


def normalizar_python(expr: str) -> str:
    """Convierte entrada visual (con superíndices unicode) a sintaxis Python ejecutable."""
    s = expr.strip().lower()
    if not s:
        return ""

    # Reemplazos básicos
    s = s.replace("π", "pi").replace("√", "sqrt")

    # Reemplazar 'e' por 'e_val' solo si es una palabra aislada
    s = re.sub(r'\be\b', 'e_val', s)

    # Manejo de superíndices (x² -> x**(2), x⁻¹⁄² -> x**(-1/2), x⁻¹⁻⁄² -> x**(-(-1/2)))
    pattern = f"(?P<base>[a-zA-Z0-9_\\)\\]])(?P<sup>[{re.escape(SUP_CHARS)}]+)"

    def repl(m):
        base = m.group('base')
        sup_raw = m.group('sup')
        sup_norm = "".join(REVERSE_MAP.get(ch, ch) for ch in sup_raw)
        sup_expr = _transform_sup_de_python(sup_norm)
        return f"{base}**({sup_expr})"

    s = re.sub(pattern, repl, s)

    # Multiplicación implícita: 2x -> 2*x, (x+1)2 -> (x+1)*2, etc
    s = re.sub(r'(\d)([a-z\(])', r'\1*\2', s)
    s = re.sub(r'(\))([a-z0-9\(])', r'\1*\2', s)

    # funciones trig / log en español
    replacements = {
        r"\bsen\b": "sin",
        r"\bln\b": "log",
        r"\btg\b": "tan"
    }
    for esp, eng in replacements.items():
        s = re.sub(esp, eng, s)

    return s.replace("^", "**").replace("⁄", "/")


def generar_latex_previsualizacion(expr_visual: str) -> str:
    """
    Generador de LaTeX para la vista previa.
    Soporta:
      x⁻¹⁄²    -> x^{-\frac{1}{2}}
      x¹⁻⁄²    -> x^{\frac{-1}{2}}
      x⁻¹⁻⁄²   -> x^{-\frac{-1}{2}}
      x⁻(⁻¹⁄²) -> x^{-( -1/2 )} -> x^{-\left(\frac{-1}{2}\right)}
    """
    if not expr_visual:
        return ""

    tex = expr_visual
    tex = tex.replace("sen", "\\sin").replace("cos", "\\cos").replace("tan", "\\tan")
    tex = tex.replace("ln", "\\ln").replace("log", "\\ln")
    tex = tex.replace("sqrt", "\\sqrt").replace("pi", "\\pi")

    pattern = f"([{re.escape(SUP_CHARS)}]+)"

    def repl_latex(m):
        # Convertimos superíndices unicode a texto "normal"
        norm_txt = "".join(REVERSE_MAP.get(c, c) for c in m.group(1)).strip()

        # Caso: exponente con paréntesis, lo pasa por SymPy para LaTeX bonito
        if "(" in norm_txt and ")" in norm_txt:
            try:
                expr_sym = sympify(norm_txt)
                return f"^{{ {latex(expr_sym)} }}"
            except Exception:
                return f"^{{ {norm_txt} }}"

        # Caso: fracción tipo (combinaciones con signos)
        if "/" in norm_txt:
            num, den = norm_txt.split("/", 1)
            num = num.strip()
            den = den.strip()

            leading = num.startswith("-")
            trailing = num.endswith("-")
            core = num.strip("-").strip()

            # x⁻¹⁄² -> "-1/2" -> fuera
            if leading and not trailing:
                return f"^{{ -\\frac{{{core}}}{{{den}}} }}"

            # x¹⁻⁄² -> "1-" -> dentro
            if trailing and not leading:
                return f"^{{ \\frac{{-{core}}}{{{den}}} }}"

            # x⁻¹⁻⁄² -> "-1-" -> dos signos
            if leading and trailing:
                return f"^{{ -\\frac{{-{core}}}{{{den}}} }}"

            # sin signos
            return f"^{{ \\frac{{{num}}}{{{den}}} }}"

        # resto de exponentes normales
        return f"^{{{norm_txt}}}"

    tex = re.sub(pattern, repl_latex, tex)
    tex = tex.replace("*", " \\cdot ").replace("exp", "\\exp")
    return tex


def contexto_mat():
    """Contexto seguro para evaluar expresiones numéricas."""
    ctx = {k: v for k, v in np.__dict__.items() if callable(v) or isinstance(v, float)}
    ctx.update({"x": 0, "e_val": np.e, "pi": np.pi, "log": np.log})
    return ctx


def evaluar(expr, x_val):
    """Evalúa una expresión matemática en un punto x."""
    try:
        norm = normalizar_python(expr)
        ctx = contexto_mat()
        ctx['x'] = x_val
        val = eval(compile(norm, "<string>", "eval"), ctx)
        return float(val)
    except Exception:
        return np.nan

# =============================================================================
#  COMPONENTES UI
# =============================================================================

class VisorLatex(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(80)
        self.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.setHtml(self._wrap(""))

    def actualizar(self, txt):
        latex_code = generar_latex_previsualizacion(txt) if txt else "\\text{Escribe tu función...}"
        self.setHtml(self._wrap(latex_code))

    def _wrap(self, formula):
        return f"""<html><head>
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
        body {{
            font-family:'Segoe UI'; color:#1565c0;
            display:flex; justify-content:center; align-items:center;
            height:100%; margin:0; font-size:22px;
        }}
        </style>
        </head><body>$$ {formula} $$</body></html>"""


class CampoMatematico(QLineEdit):
    """
    QLineEdit que permite escribir superíndices Unicode.
    - Flecha ↑  -> entra en modo superíndice
    - Flecha ↓  -> sale de modo superíndice
    - En modo super:
        - "-" (cualquiera) -> "⁻"
        - dígitos, +, /, x, y, n, (, ) -> versión super
    - Ctrl+P -> π
    """
    def __init__(self, visor):
        super().__init__()
        self.visor = visor
        self.modo_super = False
        self.setPlaceholderText("Ej: e²ˣ + ln(x) - 5x⁻¹⁄²")

    def keyPressEvent(self, e):
        key = e.key()
        text = e.text()

        # Activar/desactivar superíndice
        if key == Qt.Key.Key_Up:
            self.modo_super = True
            return
        if key == Qt.Key.Key_Down:
            self.modo_super = False
            return

        # π (Ctrl+P)
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_P:
            self.insert("π")
            return

        # ===================== MODO SUPERÍNDICE =====================
        # ===================== MODO SUPERÍNDICE =====================
        if self.modo_super:

            # Menos: soporte tecla principal, underscore y keypad
            if key in (Qt.Key.Key_Minus, Qt.Key.Key_Underscore):
                self.insert(CHAR_MAP['-'])
                return

            # --- CAMBIO AQUÍ: Convertir a minúscula para asegurar match con el mapa ---
            txt_low = text.lower() 
            if txt_low in CHAR_MAP:
                self.insert(CHAR_MAP[txt_low])
                return
            # ------------------------------------------------------------------------

            # Tecla "/"
            if key == Qt.Key.Key_Slash:
                self.insert(CHAR_MAP["/"])
                return
            
            # Ignorar otros
            return
        # ===================== MODO NORMAL =====================
        super().keyPressEvent(e)

# =============================================================================
#  VENTANA PRINCIPAL
# =============================================================================

class VentanaNewton(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Newton-Raphson")
        self.resize(1100, 750)

        self.sel_x0 = False
        self.linea_mouse = None

        self.timer = QTimer()
        self.timer.setInterval(400)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.graficar)

        self.setup_ui()
        self.aplicar_estilos()

        self.inicializar_plano_fijo()
        self.conectar_grafica()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        lbl = QLabel("Método de Newton-Raphson")
        lbl.setObjectName("H1")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(lbl)

        split = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(split, 1)

        # === IZQUIERDA ===
        izq = QWidget()
        vizq = QVBoxLayout(izq)
        vizq.setContentsMargins(0, 0, 5, 0)
        vizq.setSpacing(10)

        # Card función
        c_fun = QFrame()
        c_fun.setObjectName("Card")
        self.shadow(c_fun)
        l = QVBoxLayout(c_fun)
        l.setContentsMargins(10, 10, 10, 10)
        l.setSpacing(5)

        l.addWidget(QLabel("Función f(x):", objectName="Bold"))
        self.visor = VisorLatex()
        self.inp_f = CampoMatematico(self.visor)
        self.inp_f.textChanged.connect(self.on_change)
        l.addWidget(self.visor)
        l.addWidget(self.inp_f)
        vizq.addWidget(c_fun)

        # Card parámetros
        c_par = QFrame()
        c_par.setObjectName("Card")
        self.shadow(c_par)
        g = QGridLayout(c_par)
        g.setContentsMargins(10, 10, 10, 10)
        g.setVerticalSpacing(8)

        g.addWidget(QLabel("Valor Inicial (x₀):", objectName="Bold"), 0, 0)
        self.ix0 = QLineEdit("0.5")
        self.ix0.textChanged.connect(self.trigger)

        self.bx0 = QPushButton(" Seleccionar x₀")
        self.bx0.clicked.connect(self.act_x0)

        g.addWidget(self.ix0, 0, 1)
        g.addWidget(self.bx0, 0, 2)

        g.addWidget(QLabel("Tolerancia:", objectName="Bold"), 1, 0)
        self.itol = QLineEdit("0.0001")
        g.addWidget(self.itol, 1, 1)

        g.addWidget(QLabel("Iteraciones:", objectName="Bold"), 2, 0)
        self.iter = QLineEdit("100")
        g.addWidget(self.iter, 2, 1)

        vizq.addWidget(c_par)

        # Botones calcular / limpiar
        hbtn = QHBoxLayout()
        self.b_calc = QPushButton("CALCULAR RAÍZ")
        self.b_calc.setObjectName("BlueBtn")
        self.b_calc.setFixedHeight(45)
        self.b_calc.clicked.connect(self.resolver)

        self.b_clr = QPushButton("Limpiar")
        self.b_clr.setFixedHeight(45)
        self.b_clr.clicked.connect(self.limpiar)

        hbtn.addWidget(self.b_calc, 2)
        hbtn.addWidget(self.b_clr, 1)
        vizq.addLayout(hbtn)

        # Card resultados
        self.c_res = QFrame()
        self.c_res.setObjectName("CardRes")
        self.shadow(self.c_res)
        vl_res = QVBoxLayout(self.c_res)
        vl_res.setContentsMargins(15, 10, 15, 10)
        vl_res.setSpacing(2)

        l_t1 = QLabel("Raíz Aproximada:")
        l_t1.setStyleSheet(
            "color:#666; font-size:11px; font-weight:bold; text-transform:uppercase;")
        self.lbl_raiz = QLabel("--")
        self.lbl_raiz.setStyleSheet(
            "color:#1565c0; font-size:22px; font-weight:bold;")

        l_t2 = QLabel("Iteraciones:")
        l_t2.setStyleSheet(
            "color:#666; font-size:11px; font-weight:bold; text-transform:uppercase; margin-top:5px;")
        self.lbl_iter = QLabel("--")
        self.lbl_iter.setStyleSheet(
            "color:#333; font-size:16px; font-weight:bold;")

        vl_res.addWidget(l_t1)
        vl_res.addWidget(self.lbl_raiz)
        vl_res.addWidget(l_t2)
        vl_res.addWidget(self.lbl_iter)
        vizq.addWidget(self.c_res)
        vizq.addStretch()

        split.addWidget(izq)

        # === DERECHA ===
        der = QWidget()
        vder = QVBoxLayout(der)
        vder.setContentsMargins(5, 0, 0, 0)

        self.tabs = QTabWidget()

        # Tab 1: Gráfica
        # Tab 1: Gráfica
        # Tab 1: Gráfica estilo GeoGebra
        # Tab 1: Gráfica estilo GeoGebra
        t1 = QWidget()
        v1 = QVBoxLayout(t1)

        # Tamaño mayor y DPI para líneas más nítidas
        self.fig = Figure(figsize=(8, 5), dpi=110)
        self.canvas = FigureCanvasQTAgg(self.fig)

        # Que use todo el espacio disponible
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.canvas.setMinimumHeight(480)

        self.ax = self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        v1.addWidget(self.toolbar)
        v1.addWidget(self.canvas)

        self.tabs.addTab(t1, "📈 Gráfica GeoGebra")



        # Tab 2: Tabla
        t2 = QWidget()
        v2 = QVBoxLayout(t2)
        self.tab = QTableWidget(0, 5)
        self.tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tab.setStyleSheet("QTableWidget::item { color: #000000; }")

        self.tab.setHorizontalHeaderLabels(["Iter", "x_n", "f(x_n)", "f'(x_n)", "Error %"])
        self.tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab.verticalHeader().setDefaultSectionSize(35)
        self.tab.setAlternatingRowColors(True)
        v2.addWidget(self.tab)
        b_exp = QPushButton("Exportar Excel")
        b_exp.clicked.connect(self.exportar)
        v2.addWidget(b_exp, alignment=Qt.AlignmentFlag.AlignRight)
        self.tabs.addTab(t2, "📋 Tabla de Datos")

        # Tab 3: Procedimiento
        t3 = QWidget()
        v3 = QVBoxLayout(t3)
        self.web = QWebEngineView()
        v3.addWidget(self.web)
        self.tabs.addTab(t3, "📝 Procedimiento")

        vder.addWidget(self.tabs)
        split.addWidget(der)
        split.setSizes([350, 1100])


    def shadow(self, w):
        eff = QGraphicsDropShadowEffect()
        eff.setBlurRadius(15)
        eff.setOffset(0, 4)
        eff.setColor(QColor(0, 0, 0, 30))
        w.setGraphicsEffect(eff)

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget { font-family: 'Segoe UI'; background: #f4f7f9; color:#333; }
        QLabel#H1 { font-size:24px; font-weight:bold; color:#1565c0; margin-bottom:5px; }
        QLabel#Bold { font-weight:bold; color:#444; }
        QFrame#Card { background:white; border-radius:10px; border:1px solid #e0e0e0; }
        QFrame#CardRes {
            background:white; border-radius:10px; border:1px solid #bbdefb;
            border-left: 5px solid #1565c0;
        }
        QLineEdit {
            border:2px solid #cfd8dc; border-radius:6px;
            padding:6px; background:white; font-size:14px;
        }
        QLineEdit:focus { border-color:#1565c0; }
        QPushButton {
            background:white; border:1px solid #cfd8dc;
            border-radius:6px; font-weight:600; padding:5px;
        }
        QPushButton:hover { background:#e3f2fd; border-color:#1565c0; }
        QPushButton#BlueBtn {
            background:#1565c0; color:white; border:none; font-size:16px;
        }
        QPushButton#BlueBtn:hover { background:#0d47a1; }

        /* ====== ESTILO TABLA ====== */

        QTableView {
            selection-background-color: #004d40;   /* color fila seleccionada */
            selection-color: #ffffff;              /* texto blanco en selección */
            gridline-color: #d0d0d0;
        }

        QTableView::item:selected {
            background: #004d40;
            color: #ffffff;
            
            
        }

        /* Quitar borde/rectángulo de foco azul */
        QTableView::item:focus {
            outline: none;
        }
    """)



    # ================= FUNCIONES GRÁFICAS =================

    def inicializar_plano_fijo(self):
        self.ax.clear()

        # Fondo blanco
        # Fondo blanco
        self.fig.patch.set_facecolor("white")
        self.ax.set_facecolor("white")

        # === GRID MAYOR: cada 1, muy suave como GeoGebra ===
        self.ax.grid(
            which="major",
            linestyle="-",
            linewidth=0.45,
            color="#d5d5d5"
        )

        # === GRID MENOR: aún más suave ===
        self.ax.minorticks_on()
        self.ax.set_xticks(np.arange(-50, 51, 0.5), minor=True)
        self.ax.set_yticks(np.arange(-50, 51, 0.5), minor=True)

        self.ax.grid(
            which="minor",
            linestyle="-",
            linewidth=0.25,
            color="#efefef"
        )

        # === Ejes más delgados (tipo GeoGebra) ===
        axis_color = "#333333"

        self.ax.spines["left"].set_position(("data", 0))
        self.ax.spines["left"].set_linewidth(0.9)   # antes 1.2
        self.ax.spines["left"].set_color(axis_color)

        self.ax.spines["bottom"].set_position(("data", 0))
        self.ax.spines["bottom"].set_linewidth(0.9)  # antes 1.2
        self.ax.spines["bottom"].set_color(axis_color)

        self.ax.spines["top"].set_color("none")
        self.ax.spines["right"].set_color("none")

        # === Ticks principales (cada 1) ===
        self.ax.set_xticks(np.arange(-50, 51, 1))
        self.ax.set_yticks(np.arange(-50, 51, 1))

        # === Ticks menores (cada 0.5) ===
        self.ax.set_xticks(np.arange(-50, 51, 0.5), minor=True)
        self.ax.set_yticks(np.arange(-50, 51, 0.5), minor=True)

        # === Estilo de ticks (más finos y números pequeños) ===
        self.ax.tick_params(
            axis="both",
            which="major",
            length=6,       # antes 8
            width=0.8,      # antes 1
            color="#333333",
            pad=6,          # menos separación
            labelsize=4     # números más pequeños
        )

        self.ax.tick_params(
            axis="both",
            which="minor",
            length=1,       # antes 3
            width=0.3,      # antes 0.6
            color="#aaaaaa"
        )


        # === Límites visibles ===
        self.ax.set_xlim(-9, 9)
        self.ax.set_ylim(-6, 6)


        self.canvas.draw()







    def conectar_grafica(self):
        self.canvas.mpl_connect('button_press_event', self._click)
        self.canvas.mpl_connect('motion_notify_event', self._hover)

    def act_x0(self):
        self.sel_x0 = True
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)

    def _hover(self, e):
        if e.inaxes != self.ax:
            return
        if not self.sel_x0:
            return
        if self.linea_mouse:
            try:
                self.linea_mouse.remove()
            except Exception:
                pass
        self.linea_mouse = self.ax.axvline(e.xdata, color='#ff9800', linestyle='--', linewidth=2)
        self.canvas.draw_idle()

    def _click(self, e):
        if e.inaxes != self.ax:
            return
        val = f"{e.xdata:.4f}"
        if self.sel_x0:
            self.ix0.setText(val)
            self.sel_x0 = False
            self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
            self.graficar()

    def on_change(self, t):
        self.visor.actualizar(t)
        self.trigger()

    def trigger(self):
        self.timer.start()

    def graficar(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        for artist in self.ax.lines + self.ax.collections + self.ax.texts:
            artist.remove()

        txt = self.inp_f.text()
        if not txt:
            self.canvas.draw()
            return

        try:
            # Muchísimos puntos para una curva super suave
            x_calc = np.linspace(xlim[0], xlim[1], 2000)
            ys = np.array([evaluar(txt, x) for x in x_calc])

            # Evitar blow-up a ±infinito
            y_span = ylim[1] - ylim[0]
            ys[np.abs(ys) > ylim[1] + y_span * 2] = np.nan

            # ===================== CURVA PRINCIPAL =====================
            self.ax.plot(
                x_calc,
                ys,
                color="#007a78",        # color verde azulado
                linewidth=1.1,         # aqui se controla el grosor
                solid_capstyle="round",
                zorder=4 # capa superior del gráfico
            )

            # ===================== DETECCIÓN DE MÁXIMOS Y MÍNIMOS =====================
            dy = np.gradient(ys, x_calc)
            ddy = np.gradient(dy, x_calc)

            # índices donde dy cambia de signo (picos y valles)
            critical = np.where(np.diff(np.sign(dy)) != 0)[0]

            crit_x = x_calc[critical]
            crit_y = ys[critical]

            # ===================== PUNTOS TIPO GEOGEBRA =====================
            self.ax.scatter( # este es el punto gris de los máximos y mínimos
                crit_x, # coordenadas x de los puntos críticos
                crit_y, # coordenadas y de los puntos críticos
                color="#555555", # color gris oscuro
                s=25, # tamaño de los puntos
                zorder=4, # capa superior del gráfico
                edgecolors="white", # borde blanco
                linewidths=1.1
            )

            # ================= MARCAR x0 =================
            if self.ix0.text():
                try:
                    x0 = float(self.ix0.text())
                    self.ax.plot( # punto verde 
                        x0, 0,
                        'o',
                        color='#1b5e20',
                        markersize=4, # tamaño del punto
                        markeredgecolor='white',
                        markeredgewidth=1.3,
                        zorder=6
                    )
                    self.ax.axvline(x0, color='#1b5e20', linestyle='--', alpha=0.7)
                except Exception:
                    pass

            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.draw()

        except Exception:
            pass

    # ================= CÁLCULO NEWTON-RAPHSON =================

        # ================= CÁLCULO NEWTON-RAPHSON =================

    def resolver(self):
        # Reset visual
        self.tab.setRowCount(0)
        self.lbl_raiz.setText("--")
        self.lbl_iter.setText("--")

        try:
            expr_txt = self.inp_f.text()
            if not expr_txt:
                return

            # --------- Derivación simbólica ---------
            try:
                x_sym = Symbol('x')
                expr_limpia = normalizar_python(expr_txt)
                expr_sym = sympify(expr_limpia.replace("e_val", "E"))
                f_sym = expr_sym
                df_sym = diff(f_sym, x_sym)

                f_latex = latex(f_sym)
                df_latex = latex(df_sym)
                df_txt_eval = str(df_sym)

            except Exception as e:
                QMessageBox.warning(self, "Error Matemático", f"No se pudo derivar: {e}")
                return

            # --------- Parámetros iniciales ---------
            x_n = float(self.ix0.text())
            tol = float(self.itol.text())
            imax = int(self.iter.text())

            html = f"""
            <html><body style='font-family:Segoe UI; padding:20px; color:#333; line-height:1.5'>
            <h2 style='color:#1565c0; border-bottom:2px solid #1565c0; padding-bottom:10px'>
                Procedimiento Newton-Raphson
            </h2>
            <p><b>Función:</b> $$f(x) = {f_latex}$$</p>
            <p><b>Derivada:</b> $$f'(x) = {df_latex}$$</p>
            <p><b>Fórmula:</b> $$x_{{n+1}} = x_n - \\frac{{f(x_n)}}{{f'(x_n)}}$$</p>
            <hr>
            """

            found = False

            for i in range(1, imax + 1):
                fx = evaluar(expr_txt, x_n)
                dfx = evaluar(df_txt_eval, x_n)

                if np.isnan(fx) or np.isnan(dfx):
                    html += "<div style='background:#ffebee; color:#c62828; padding:15px;'>⚠️ Error: Valor indefinido (NaN).</div>"
                    break

                if abs(dfx) < 1e-15:
                    html += "<div style='background:#ffebee; color:#c62828; padding:15px;'>⚠️ Derivada ≈ 0 (división por cero).</div>"
                    break

                x_next = x_n - (fx / dfx)
                err = abs((x_next - x_n) / x_next) * 100 if x_next != 0 else 100

                # ----------------- Tabla -----------------
                r = self.tab.rowCount()
                self.tab.insertRow(r)
                for j, val in enumerate([i, x_n, fx, dfx, err]):
                    item_text = f"{val:.6f}" if j > 0 else str(int(val))
                    it = QTableWidgetItem(item_text)
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tab.setItem(r, j, it)

                # ----------------- Paso a paso HTML -----------------
                html += f"""
                <div style='background:#fff; border:1px solid #e0e0e0; padding:15px;
                            margin-bottom:15px; border-radius:8px; border-left:5px solid #1565c0;'>
                    <b>Iteración {i}</b> (xₙ = {x_n:.5f})<br>
                    $$f({x_n:.4f}) = {fx:.4f}, \quad f'({x_n:.4f}) = {dfx:.4f}$$<br>
                    $$x_{{{i+1}}} = {x_n:.5f} - \\frac{{{fx:.4f}}}{{{dfx:.4f}}}
                    = \\mathbf{{{x_next:.6f}}}$$<br>
                    <small style='color:#666'>Error: {err:.5f}%</small>
                </div>
                """

                # Actualizamos x_n al nuevo valor
                x_n = x_next

                # ¿Convergencia?
                if abs(fx) < 1e-15 or err < tol:
                    root = x_n  # este es nuestro x*
                    html += f"""
                    <div style='background:#e8f5e9; color:#2e7d32; padding:20px;
                                border-radius:8px; text-align:center;'>
                       <h3>✅ Raíz: {root:.6f}</h3>
                    </div>
                    """

                    # ===>>> ACTUALIZAMOS LOS LABELS DEL PANEL IZQUIERDO
                    self.lbl_raiz.setText(f"{root:.6f}")
                    self.lbl_iter.setText(str(i))

                    # Redibujar gráfica y marcar raíz exacta sobre el eje x
                    self.graficar()
                    self.ax.plot(
                        root, 0,
                        'o',
                        color='#d32f2f',
                        markersize=6,
                        markeredgecolor='white',
                        markeredgewidth=1.1,
                        zorder=10
                    )
                    self.canvas.draw()

                    found = True
                    break

            # Si no convergió, al menos mostramos el último x_n como aproximación
            if not found:
                html += "<div style='color:#d32f2f; text-align:center;'>⚠️ No convergió dentro del número máximo de iteraciones.</div>"
                # Mostramos la última aproximación igual
                self.lbl_raiz.setText(f"{x_n:.6f}")
                self.lbl_iter.setText(str(imax))

            html += """
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async
                    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            </body></html>
            """

            self.web.setHtml(html)
            self.tabs.setCurrentIndex(2)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def limpiar(self):
        self.inp_f.clear()
        self.ix0.setText("0.5")
        self.tab.setRowCount(0)
        self.web.setHtml("")
        self.lbl_raiz.setText("--")
        self.lbl_iter.setText("--")
        self.graficar()

    def exportar(self):
        if not pd:
            QMessageBox.warning(self, "X", "Pandas no instalado")
            return
        if self.tab.rowCount() == 0:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar", "newton.xlsx", "Excel (*.xlsx)")
        if path:
            d = [[self.tab.item(r, c).text() for c in range(5)] for r in range(self.tab.rowCount())]
            pd.DataFrame(d, columns=["Iter", "xn", "f(xn)", "f'(xn)", "Err"]).to_excel(path, index=False)
            QMessageBox.information(self, "Ok", "Exportado correctamente")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = VentanaNewton()
    w.show()
    sys.exit(app.exec())
