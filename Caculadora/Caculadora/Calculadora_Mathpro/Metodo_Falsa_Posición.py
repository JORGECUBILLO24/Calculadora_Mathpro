import sys
import re
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from sympy import sympify, Symbol, latex, diff

# Intentamos importar pandas para exportar (opcional)
try:
    import pandas as pd
except ImportError:
    pd = None

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Matplotlib - Configuración
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

# =============================================================================
#  MOTOR MATEMÁTICO (IDÉNTICO)
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
    sup_norm = sup_norm.strip()
    if "(" in sup_norm or ")" in sup_norm:
        return sup_norm
    if "/" not in sup_norm:
        return sup_norm
    num, den = sup_norm.split("/", 1)
    num, den = num.strip(), den.strip()
    leading = num.startswith("-")
    trailing = num.endswith("-")
    core = num.strip("-").strip()
    if leading and trailing:
        return f"-(-{core})/{den}"
    elif leading:
        return f"-({core})/{den}"
    elif trailing:
        return f"(-{core})/{den}"
    else:
        return f"{core}/{den}"


def normalizar_python(expr: str) -> str:
    s = expr.strip().lower()
    if not s: 
        return ""
    s = s.replace("π", "pi").replace("√", "sqrt")
    s = re.sub(r'\be\b', 'e_val', s)

    pattern = f"(?P<base>[a-zA-Z0-9_\\)\\]])(?P<sup>[{re.escape(SUP_CHARS)}]+)"

    def repl(m):
        base = m.group('base')
        sup_raw = m.group('sup')
        sup_norm = "".join(REVERSE_MAP.get(ch, ch) for ch in sup_raw)
        sup_expr = _transform_sup_de_python(sup_norm)
        return f"{base}**({sup_expr})"

    s = re.sub(pattern, repl, s)
    s = re.sub(r'(\d)([a-z\(])', r'\1*\2', s)
    s = re.sub(r'(\))([a-z0-9\(])', r'\1*\2', s)

    replacements = {r"\bsen\b": "sin", r"\bln\b": "log", r"\btg\b": "tan"}
    for esp, eng in replacements.items():
        s = re.sub(esp, eng, s)

    return s.replace("^", "**").replace("⁄", "/")


def generar_latex_previsualizacion(expr_visual: str) -> str:
    if not expr_visual:
        return ""
    tex = expr_visual
    tex = tex.replace("sen", "\\sin").replace("cos", "\\cos").replace("tan", "\\tan")
    tex = tex.replace("ln", "\\ln").replace("log", "\\ln")
    tex = tex.replace("sqrt", "\\sqrt").replace("pi", "\\pi")

    pattern = f"([{re.escape(SUP_CHARS)}]+)"

    def repl_latex(m):
        norm_txt = "".join(REVERSE_MAP.get(c, c) for c in m.group(1)).strip()
        if "(" in norm_txt and ")" in norm_txt:
            try:
                return f"^{{ {latex(sympify(norm_txt))} }}"
            except:
                return f"^{{ {norm_txt} }}"
        if "/" in norm_txt:
            num, den = norm_txt.split("/", 1)
            num, den = num.strip(), den.strip()
            leading = num.startswith("-")
            trailing = num.endswith("-")
            core = num.strip("-").strip()

            if leading and not trailing: 
                return f"^{{ -\\frac{{{core}}}{{{den}}} }}"
            if trailing and not leading: 
                return f"^{{ \\frac{{-{core}}}{{{den}}} }}"
            if leading and trailing: 
                return f"^{{ -\\frac{{-{core}}}{{{den}}} }}"

            return f"^{{ \\frac{{{num}}}{{{den}}} }}"
        return f"^{{{norm_txt}}}"

    tex = re.sub(pattern, repl_latex, tex)
    tex = tex.replace("*", " \\cdot ").replace("exp", "\\exp")
    return tex


def contexto_mat():
    ctx = {k: v for k, v in np.__dict__.items() if callable(v) or isinstance(v, float)}
    ctx.update({"x": 0, "e_val": np.e, "pi": np.pi, "log": np.log})
    return ctx


def evaluar(expr, x_val):
    try:
        norm = normalizar_python(expr)
        ctx = contexto_mat()
        ctx["x"] = x_val
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
        return f"""
        <html><head>
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async 
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
        body {{
            font-family:'Segoe UI'; 
            color:#1565c0;
            display:flex; 
            justify-content:center; 
            align-items:center;
            height:100%; 
            margin:0; 
            font-size:22px;
        }}
        </style>
        </head><body>$$ {formula} $$</body></html>
        """


class CampoMatematico(QLineEdit):
    def __init__(self, visor):
        super().__init__()
        self.visor = visor
        self.modo_super = False
        self.setPlaceholderText("Ej: e²ˣ + ln(x) - 5x⁻¹⁄²")

    def keyPressEvent(self, e):
        key = e.key()
        text = e.text()

        if key == Qt.Key.Key_Up:
            self.modo_super = True
            return
        if key == Qt.Key.Key_Down:
            self.modo_super = False
            return

        if e.modifiers() & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_P:
            self.insert("π")
            return

        if self.modo_super:
            if key in (Qt.Key.Key_Minus, Qt.Key.Key_Underscore):
                self.insert(CHAR_MAP["-"])
                return
            if text in CHAR_MAP:
                self.insert(CHAR_MAP[text])
                return
            if key == Qt.Key.Key_Slash:
                self.insert(CHAR_MAP["/"])
                return
            return

        super().keyPressEvent(e)

# =============================================================================
#  VENTANA PRINCIPAL (FALSA POSICIÓN)
# =============================================================================

class VentanaFalsaPosicion(QWidget):
    def __init__(self):
        super().__init__()
        # CAMBIO 1: Título de ventana
        self.setWindowTitle("Calculadora Falsa Posición (Gráfica Mejorada)")
        self.resize(1150, 750)

        self.sel_a = False
        self.sel_b = False
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

        # CAMBIO 2: Etiqueta principal
        lbl = QLabel("Método de Falsa Posición")
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

        # Función
        c_fun = QFrame()
        c_fun.setObjectName("Card")
        self.shadow(c_fun)
        l = QVBoxLayout(c_fun)
        l.setContentsMargins(10, 10, 10, 10)
        l.addWidget(QLabel("Función f(x):", objectName="Bold"))
        self.visor = VisorLatex()
        self.inp_f = CampoMatematico(self.visor)
        self.inp_f.textChanged.connect(self.on_change)
        l.addWidget(self.visor)
        l.addWidget(self.inp_f)
        vizq.addWidget(c_fun)

        # Parámetros
        c_par = QFrame()
        c_par.setObjectName("Card")
        self.shadow(c_par)
        g = QGridLayout(c_par)
        g.setContentsMargins(10, 10, 10, 10)
        g.setVerticalSpacing(8)

        g.addWidget(QLabel("Intervalo A (a):", objectName="Bold"), 0, 0)
        self.ia = QLineEdit("-1.0")
        self.ia.textChanged.connect(self.trigger)
        self.ba = QPushButton(" Seleccionar a (Verde)")
        self.ba.clicked.connect(self.act_a)
        g.addWidget(self.ia, 0, 1)
        g.addWidget(self.ba, 0, 2)

        g.addWidget(QLabel("Intervalo B (b):", objectName="Bold"), 1, 0)
        self.ib = QLineEdit("1.0")
        self.ib.textChanged.connect(self.trigger)
        self.bb = QPushButton(" Seleccionar b (Rojo)")
        self.bb.clicked.connect(self.act_b)
        g.addWidget(self.ib, 1, 1)
        g.addWidget(self.bb, 1, 2)

        g.addWidget(QLabel("Tolerancia:", objectName="Bold"), 2, 0)
        self.itol = QLineEdit("0.0001")
        g.addWidget(self.itol, 2, 1)

        g.addWidget(QLabel("Iteraciones:", objectName="Bold"), 3, 0)
        self.iter = QLineEdit("100")
        g.addWidget(self.iter, 3, 1)

        vizq.addWidget(c_par)

        # Botones
        hbtn = QHBoxLayout()
        self.b_calc = QPushButton("CALCULAR RAÍZ")
        self.b_calc.setObjectName("BlueBtn")
        self.b_calc.setFixedHeight(45)
        self.b_calc.clicked.connect(self.usar_metodo_falsa_posicion) # Conectado al nuevo método
        self.b_clr = QPushButton("Limpiar")
        self.b_clr.setFixedHeight(45)
        self.b_clr.clicked.connect(self.limpiar)

        hbtn.addWidget(self.b_calc, 2)
        hbtn.addWidget(self.b_clr, 1)
        vizq.addLayout(hbtn)

        # Resultados
        self.c_res = QFrame()
        self.c_res.setObjectName("CardRes")
        self.shadow(self.c_res)
        vl_res = QVBoxLayout(self.c_res)
        vl_res.setContentsMargins(15, 10, 15, 10)

        l_t1 = QLabel("Raíz Aproximada:")
        l_t1.setStyleSheet("color:#666; font-size:11px; font-weight:bold; text-transform:uppercase;")
        self.lbl_raiz = QLabel("--")
        self.lbl_raiz.setStyleSheet("color:#1565c0; font-size:22px; font-weight:bold;")

        l_t2 = QLabel("Iteraciones:")
        l_t2.setStyleSheet("color:#666; font-size:11px; font-weight:bold; text-transform:uppercase; margin-top:5px;")
        self.lbl_iter = QLabel("--")
        self.lbl_iter.setStyleSheet("color:#333; font-size:16px; font-weight:bold;")

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

        # Gráfica
        t1 = QWidget()
        v1 = QVBoxLayout(t1)

        self.fig = Figure(figsize=(8, 5), dpi=110)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ax = self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        v1.addWidget(self.toolbar)
        v1.addWidget(self.canvas)
        self.tabs.addTab(t1, "📈 Gráfica GeoGebra")

        # Tabla
        t2 = QWidget()
        v2 = QVBoxLayout(t2)

        self.tab = QTableWidget(0, 6)
        self.tab.setHorizontalHeaderLabels(["Iter", "a", "b", "c (Raíz)", "f(c)", "Error %"])
        self.tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab.setAlternatingRowColors(True)
        v2.addWidget(self.tab)

        b_exp = QPushButton("Exportar Excel")
        b_exp.clicked.connect(self.exportar)
        v2.addWidget(b_exp, alignment=Qt.AlignmentFlag.AlignRight)

        self.tabs.addTab(t2, "📋 Tabla de Datos")

        # Procedimiento
        t3 = QWidget()
        v3 = QVBoxLayout(t3)

        self.web = QWebEngineView()
        v3.addWidget(self.web)
        self.tabs.addTab(t3, "📝 Procedimiento")

        vder.addWidget(self.tabs)
        split.addWidget(der)
        split.setSizes([380, 1100])

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
        QFrame#CardRes { background:white; border-radius:10px; border:1px solid #bbdefb; border-left: 5px solid #1565c0; }
        QLineEdit { border:2px solid #cfd8dc; border-radius:6px; padding:6px; background:white; font-size:14px; }
        QLineEdit:focus { border-color:#1565c0; }
        QPushButton { background:white; border:1px solid #cfd8dc; border-radius:6px; font-weight:600; padding:5px; }
        QPushButton:hover { background:#e3f2fd; border-color:#1565c0; }
        QPushButton#BlueBtn { background:#1565c0; color:white; border:none; font-size:16px; }
        QPushButton#BlueBtn:hover { background:#0d47a1; }
        QTableView { selection-background-color: #004d40; selection-color: #ffffff; gridline-color: #d0d0d0; }
        """)

    def inicializar_plano_fijo(self):
        self.ax.clear()
        self.fig.patch.set_facecolor("white")
        self.ax.set_facecolor("white")

        self.ax.grid(which="major", linestyle="-", linewidth=0.45, color="#d5d5d5")
        self.ax.minorticks_on()
        # GRID GRANDE COMO PEDISTE
        self.ax.set_xticks(np.arange(-50, 51, 0.5), minor=True)
        self.ax.set_yticks(np.arange(-50, 51, 0.5), minor=True)
        self.ax.grid(which="minor", linestyle="-", linewidth=0.25, color="#efefef")

        axis_color = "#333333"
        self.ax.spines["left"].set_position(("data", 0))
        self.ax.spines["left"].set_linewidth(0.9)   
        self.ax.spines["left"].set_color(axis_color)
        self.ax.spines["bottom"].set_position(("data", 0))
        self.ax.spines["bottom"].set_linewidth(0.9) 
        self.ax.spines["bottom"].set_color(axis_color)
        self.ax.spines["top"].set_color("none")
        self.ax.spines["right"].set_color("none")

        self.ax.set_xticks(np.arange(-50, 51, 1))
        self.ax.set_yticks(np.arange(-50, 51, 1))
        self.ax.tick_params(axis="both", which="major", length=6, width=0.8, color="#333333", pad=6, labelsize=4)
        self.ax.tick_params(axis="both", which="minor", length=1, width=0.3, color="#aaaaaa")
        self.ax.set_xlim(-9, 9)
        self.ax.set_ylim(-6, 6)
        self.canvas.draw()

    def conectar_grafica(self):
        self.canvas.mpl_connect("button_press_event", self._click)
        self.canvas.mpl_connect("motion_notify_event", self._hover)

    def act_a(self):
        self.sel_a = True
        self.sel_b = False
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)

    def act_b(self):
        self.sel_b = True
        self.sel_a = False
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)

    def _hover(self, e):
        if e.inaxes != self.ax: return
        if not (self.sel_a or self.sel_b): return
        color_linea = "#d32f2f"
        if self.sel_a:
            color_linea = "#2e7d32"
        elif self.sel_b:
            try:
                a_val = float(self.ia.text())
                b_val = e.xdata
                txt = self.inp_f.text()
                fa = evaluar(txt, a_val)
                fb = evaluar(txt, b_val)
                if fa * fb < 0: color_linea = "#2e7d32" 
                else: color_linea = "#d32f2f"
            except: color_linea = "#d32f2f"

        if self.linea_mouse:
            try: self.linea_mouse.remove()
            except: pass
        self.linea_mouse = self.ax.axvline(e.xdata, color=color_linea, linestyle="--", linewidth=2)
        self.canvas.draw_idle()

    def _click(self, e):
        if e.inaxes != self.ax: return
        val = f"{e.xdata:.4f}"
        if self.sel_a:
            self.ia.setText(val)
            self.sel_a = False
            self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
            self.graficar()
        elif self.sel_b:
            self.ib.setText(val)
            self.sel_b = False
            self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
            self.graficar()
        if self.linea_mouse:
            try: self.linea_mouse.remove()
            except: pass
            self.linea_mouse = None
            self.canvas.draw_idle()

    def graficar(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        for artist in self.ax.lines + self.ax.collections + self.ax.texts:
            try: artist.remove()
            except: pass
        
        txt = self.inp_f.text()
        if not txt:
            self.canvas.draw()
            return

        try:
            x_calc = np.linspace(xlim[0], xlim[1], 2000)
            ys = np.array([evaluar(txt, x) for x in x_calc])
            y_span = ylim[1] - ylim[0]
            ys[np.abs(ys) > ylim[1] + y_span * 2] = np.nan 

            self.ax.plot(x_calc, ys, color="#007a78", linewidth=1.1, solid_capstyle="round", zorder=4)

            dy = np.gradient(ys, x_calc)
            critical = np.where(np.diff(np.sign(dy)) != 0)[0]
            crit_x = x_calc[critical]
            crit_y = ys[critical]
            self.ax.scatter(crit_x, crit_y, color="#555555", s=25, zorder=4, edgecolors="white", linewidths=1.1)

            if self.ia.text():
                try:
                    a = float(self.ia.text())
                    self.ax.axvline(a, color="#2e7d32", linestyle="--", linewidth=1.2, alpha=0.8)
                    self.ax.plot(a, 0, "o", color="#2e7d32", markersize=5, markeredgecolor="white", markeredgewidth=1.2, zorder=6)
                except: pass

            if self.ib.text():
                try:
                    b = float(self.ib.text())
                    self.ax.axvline(b, color="#c62828", linestyle="--", linewidth=1.2, alpha=0.8)
                    self.ax.plot(b, 0, "o", color="#c62828", markersize=5, markeredgecolor="white", markeredgewidth=1.2, zorder=6)
                except: pass

            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.draw()
        except Exception: pass

    # =========================================================
    #  MÉTODO DE FALSA POSICIÓN (LÓGICA ACTUALIZADA)
    # =========================================================
    def usar_metodo_falsa_posicion(self):
        self.tab.setRowCount(0)
        self.lbl_raiz.setText("--")
        self.lbl_iter.setText("--")

        try:
            expr_txt = self.inp_f.text()
            if not expr_txt: return

            a = float(self.ia.text())
            b = float(self.ib.text())
            tol = float(self.itol.text())
            imax = int(self.iter.text())

            fa = evaluar(expr_txt, a)
            fb = evaluar(expr_txt, b)

            if fa * fb > 0:
                QMessageBox.critical(self, "Error de Bolzano", "f(a) y f(b) deben tener signos opuestos para iniciar.")
                return

            found = False
            root = None
            last_a = a
            last_b = b

            # CAMBIO 3: Actualizar HTML para explicar Falsa Posición
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; padding: 20px; color: #333; line-height: 1.6; }
                    h2 { color: #1565c0; border-bottom: 2px solid #1565c0; padding-bottom: 10px; }
                    .iter-box { 
                        border-left: 5px solid #1565c0; 
                        padding: 10px 15px; 
                        margin-bottom: 20px; 
                        background-color: #f9f9f9;
                        border-radius: 0 8px 8px 0;
                    }
                    .final-box { 
                        background-color: #e8f5e9; 
                        padding: 20px; 
                        border-radius: 8px; 
                        text-align: center; 
                        color: #2e7d32; 
                        border: 1px solid #c8e6c9;
                    }
                    .error-box { 
                        background-color: #ffebee; 
                        padding: 20px; 
                        border-radius: 8px; 
                        text-align: center; 
                        color: #c62828; 
                        border: 1px solid #ffcdd2;
                    }
                </style>
            </head>
            <body>
            <h2>Procedimiento - Método de Falsa Posición</h2>
            <p>Usando la intersección de la recta secante con el eje X:</p>
            <p>$$ c = b - \\frac{f(b) \cdot (a - b)}{f(a) - f(b)} $$</p>
            """

            for i in range(1, imax + 1):
                # CAMBIO 4: Fórmula de Falsa Posición (Regula Falsi)
                # Evitamos división por cero si fa == fb (imposible si signos opuestos y f continua no trivial)
                if fa == fb:
                    break 
                
                c = b - (fb * (a - b)) / (fa - fb)
                fc = evaluar(expr_txt, c)

                # Error estimado (aunque en falsa posición a veces se estanca un extremo, usamos distancia o valor de función)
                error = abs(b - a) # Mantenemos el criterio original o se puede usar abs(c_new - c_old)
                # Cálculo de error porcentual (referencial)
                err_p = (error/abs(c))*100 if abs(c) > 1e-15 else 100

                # Tabla
                r = self.tab.rowCount()
                self.tab.insertRow(r)
                row_data = [i, a, b, c, fc, err_p]
                for j, val in enumerate(row_data):
                    it = QTableWidgetItem(f"{val:.6f}" if j > 0 else str(int(val)))
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tab.setItem(r, j, it)

                # Reporte LaTeX
                html += f"""
                <div class='iter-box'>
                    <strong>Iteración {i}</strong><br>
                    $$ a = {a:.5f}, \quad f(a) = {fa:.5f} $$
                    $$ b = {b:.5f}, \quad f(b) = {fb:.5f} $$
                    $$ c_{{{i}}} = {b:.5f} - \\frac{{{fb:.5f}({a:.5f} - {b:.5f})}}{{{fa:.5f} - {fb:.5f}}} = \\mathbf{{{c:.6f}}} $$
                    $$ f(c_{{{i}}}) = {fc:.6f} $$
                </div>
                """

                if abs(fc) < 1e-15 or error < tol:
                    root = c
                    found = True
                    break

                if fa * fc < 0:
                    b = c
                    fb = fc
                    last_b = b
                else:
                    a = c
                    fa = fc
                    last_a = a

            self.graficar()

            if found:
                self.ax.axvline(root, color='#2e7d32', linestyle='-', linewidth=2.5)
                self.ax.plot(root, 0, 'o', color='#2e7d32', markersize=10, markeredgecolor='white', markeredgewidth=2, zorder=10)
                self.ax.axvline(last_a, color="#2e7d32", linestyle=":", alpha=0.5)
                self.ax.axvline(last_b, color="#c62828", linestyle=":", alpha=0.5)

                self.lbl_raiz.setText(f"{root:.6f}")
                self.lbl_iter.setText(str(i))

                html += f"""
                <div class='final-box'>
                    <h3>✅ Convergencia alcanzada</h3>
                    $$ x \\approx {root:.6f} $$
                    <p>Iteraciones totales: {i}</p>
                </div>
                </body></html>
                """
            else:
                final_c = b - (fb * (a - b)) / (fa - fb)
                self.ax.axvline(final_c, color='#d32f2f', linestyle='-', linewidth=2.5)
                self.lbl_raiz.setText(f"{final_c:.6f}")
                self.lbl_iter.setText(str(imax))

                html += f"""
                <div class='error-box'>
                    <h3>⚠️ No se alcanzó la tolerancia</h3>
                    Último valor calculado: $$ c = {final_c:.6f} $$
                </div>
                </body></html>
                """

            self.canvas.draw()
            self.web.setHtml(html)
            self.tabs.setCurrentIndex(2)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def limpiar(self):
        self.inp_f.clear()
        self.ia.setText("-1.0")
        self.ib.setText("1.0")
        self.tab.setRowCount(0)
        self.web.setHtml("")
        self.lbl_raiz.setText("--")
        self.lbl_iter.setText("--")
        self.graficar()

    def exportar(self):
        if not pd:
            QMessageBox.warning(self, "Error", "Pandas no está instalado.")
            return
        if self.tab.rowCount() == 0:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar", "falsa_posicion.xlsx", "Excel (*.xlsx)")
        if path:
            d = [[self.tab.item(r, c).text() for c in range(6)] for r in range(self.tab.rowCount())]
            pd.DataFrame(d, columns=["Iter", "a", "b", "c", "f(c)", "Err"]).to_excel(path, index=False)
            QMessageBox.information(self, "Exportado", "Archivo exportado correctamente.")

    def on_change(self, text):
        self.visor.actualizar(text)
        self.trigger()

    def trigger(self):
        self.timer.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = VentanaFalsaPosicion()
    ventana.show()
    sys.exit(app.exec())