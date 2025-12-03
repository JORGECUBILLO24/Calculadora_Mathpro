import sys
import re
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from sympy import sympify, Symbol, latex

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
    QFileDialog, QGraphicsDropShadowEffect, QSizePolicy
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

CHAR_MAP = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '/': '⁄', '=': '⁼',
    '(': '⁽', ')': '⁾',
    'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 
    'f': 'ᶠ', 'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ', 
    'k': 'ᵏ', 'l': 'ˡ', 'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 
    'p': 'ᵖ', 'r': 'ʳ', 's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ', 
    'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ',
    'π': 'pi' 
}

REVERSE_MAP = {v: k for k, v in CHAR_MAP.items()}
SUP_CHARS = "".join(CHAR_MAP.values())


def _transform_sup_de_python(sup_norm: str) -> str:
    sup_norm = sup_norm.strip()
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
                expr_sym = sympify(norm_txt)
                return f"^{{ {latex(expr_sym)} }}"
            except Exception:
                return f"^{{ {norm_txt} }}"
        if "/" in norm_txt:
            num, den = norm_txt.split("/", 1)
            num = num.strip()
            den = den.strip()
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
    def __init__(self, visor):
        super().__init__()
        self.visor = visor
        self.modo_super = False
        self.setPlaceholderText("Ej: x³ - 2x - 5")

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
                self.insert(CHAR_MAP['-'])
                return
            txt_low = text.lower() 
            if txt_low in CHAR_MAP:
                self.insert(CHAR_MAP[txt_low])
                return
            if key == Qt.Key.Key_Slash:
                self.insert(CHAR_MAP["/"])
                return
            return
        super().keyPressEvent(e)

# =============================================================================
#  VENTANA PRINCIPAL (MÉTODO SECANTE)
# =============================================================================

class VentanaSecante(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Método de la Secante")
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

        lbl = QLabel("Método de la Secante")
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

        # --- CAMBIOS PARA SECANTE: x0 y x1 ---
        g.addWidget(QLabel("Valor Inicial (x₀):", objectName="Bold"), 0, 0)
        self.ix0 = QLineEdit("0.0")
        self.ix0.textChanged.connect(self.trigger)
        
        self.bx0 = QPushButton("📍") # Botón pequeño para seleccionar
        self.bx0.setToolTip("Seleccionar x₀ en la gráfica")
        self.bx0.setFixedWidth(30)
        self.bx0.clicked.connect(self.act_x0)
        
        h_x0 = QHBoxLayout()
        h_x0.addWidget(self.ix0)
        h_x0.addWidget(self.bx0)
        g.addLayout(h_x0, 0, 1)

        g.addWidget(QLabel("Valor Inicial (x₁):", objectName="Bold"), 1, 0)
        self.ix1 = QLineEdit("1.0")
        self.ix1.textChanged.connect(self.trigger)
        g.addWidget(self.ix1, 1, 1)

        g.addWidget(QLabel("Tolerancia:", objectName="Bold"), 2, 0)
        self.itol = QLineEdit("0.0001")
        g.addWidget(self.itol, 2, 1)

        g.addWidget(QLabel("Iteraciones:", objectName="Bold"), 3, 0)
        self.iter = QLineEdit("100")
        g.addWidget(self.iter, 3, 1)
        # --------------------------------------

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
        t1 = QWidget()
        v1 = QVBoxLayout(t1)
        self.fig = Figure(figsize=(8, 5), dpi=110)
        self.canvas = FigureCanvasQTAgg(self.fig)
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
        self.tab = QTableWidget(0, 6) # Una columna más para Secante
        self.tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tab.setStyleSheet("QTableWidget::item { color: #000000; }")
        
        # Columnas ajustadas para Secante
        self.tab.setHorizontalHeaderLabels(["Iter", "x_{n-1}", "x_n", "f(x_n)", "x_{n+1}", "Error %"])
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
        QTableView {
            selection-background-color: #004d40;
            selection-color: #ffffff;
            gridline-color: #d0d0d0;
        }
        QTableView::item:selected { background: #004d40; color: #ffffff; }
        QTableView::item:focus { outline: none; }
    """)

    # ================= FUNCIONES GRÁFICAS =================

    def inicializar_plano_fijo(self):
        self.ax.clear()
        self.fig.patch.set_facecolor("white")
        self.ax.set_facecolor("white")

        self.ax.grid(which="major", linestyle="-", linewidth=0.45, color="#d5d5d5")
        self.ax.minorticks_on()
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
        self.ax.tick_params(axis="both", which="major", length=6, width=0.8, color="#333", pad=6, labelsize=8)
        self.ax.tick_params(axis="both", which="minor", length=1, width=0.3, color="#aaa")

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
            x_calc = np.linspace(xlim[0], xlim[1], 2000)
            ys = np.array([evaluar(txt, x) for x in x_calc])
            y_span = ylim[1] - ylim[0]
            ys[np.abs(ys) > ylim[1] + y_span * 2] = np.nan

            self.ax.plot(
                x_calc, ys, color="#007a78", linewidth=1.1,
                solid_capstyle="round", zorder=4
            )

            # Puntos críticos (max/min)
            dy = np.gradient(ys, x_calc)
            critical = np.where(np.diff(np.sign(dy)) != 0)[0]
            crit_x = x_calc[critical]
            crit_y = ys[critical]
            self.ax.scatter(crit_x, crit_y, color="#555555", s=25, zorder=4, edgecolors="white", linewidths=1.1)

            # === MARCAR x0 ===
            if self.ix0.text():
                try:
                    x0 = float(self.ix0.text())
                    self.ax.plot(x0, 0, 'o', color='#1b5e20', markersize=4, zorder=6) # Verde
                    self.ax.text(x0, 0.2, "x₀", color='#1b5e20', fontsize=8, ha='center')
                    self.ax.axvline(x0, color='#1b5e20', linestyle='--', alpha=0.5)
                except Exception: pass

            # === MARCAR x1 (Nuevo) ===
            if self.ix1.text():
                try:
                    x1 = float(self.ix1.text())
                    self.ax.plot(x1, 0, 'o', color='#e65100', markersize=4, zorder=6) # Naranja
                    self.ax.text(x1, -0.5, "x₁", color='#e65100', fontsize=8, ha='center')
                    self.ax.axvline(x1, color='#e65100', linestyle='--', alpha=0.5)
                except Exception: pass

            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.draw()

        except Exception:
            pass

    # ================= CÁLCULO SECANTE =================

    def resolver(self):
        # Reset visual
        self.tab.setRowCount(0)
        self.lbl_raiz.setText("--")
        self.lbl_iter.setText("--")

        try:
            expr_txt = self.inp_f.text()
            if not expr_txt:
                return

            # Para mostrar bonito en LaTeX
            try:
                expr_limpia = normalizar_python(expr_txt)
                f_sym = sympify(expr_limpia.replace("e_val", "E"))
                f_latex = latex(f_sym)
            except Exception:
                f_latex = expr_txt

            # Parámetros iniciales
            try:
                x_prev = float(self.ix0.text()) # x0 (i-1)
                x_curr = float(self.ix1.text()) # x1 (i)
                tol = float(self.itol.text())
                imax = int(self.iter.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Verifica que los valores numéricos sean correctos")
                return

            html = f"""
            <html><body style='font-family:Segoe UI; padding:20px; color:#333; line-height:1.5'>
            <h2 style='color:#1565c0; border-bottom:2px solid #1565c0; padding-bottom:10px'>
                Procedimiento: Método de la Secante
            </h2>
            <p><b>Función:</b> $$f(x) = {f_latex}$$</p>
            <p><b>Valores iniciales:</b> $x_0 = {x_prev}, \quad x_1 = {x_curr}$</p>
            <p><b>Fórmula Recurrente:</b> 
               $$x_{{n+1}} = x_n - \\frac{{f(x_n)(x_n - x_{{n-1}})}}{{f(x_n) - f(x_{{n-1}})}}$$
            </p>
            <hr>
            """

            found = False

            # Evaluar funciones iniciales
            f_prev = evaluar(expr_txt, x_prev)
            
            for i in range(1, imax + 1):
                f_curr = evaluar(expr_txt, x_curr)

                if np.isnan(f_curr) or np.isnan(f_prev):
                    html += "<div style='background:#ffebee; color:#c62828; padding:15px;'>⚠️ Error: Valor indefinido (NaN).</div>"
                    break

                denom = f_curr - f_prev
                if abs(denom) < 1e-15:
                    html += "<div style='background:#ffebee; color:#c62828; padding:15px;'>⚠️ División por cero (f(xn) ≈ f(xn-1)).</div>"
                    break

                # Fórmula de la Secante
                x_next = x_curr - (f_curr * (x_curr - x_prev) / denom)
                
                err = abs((x_next - x_curr) / x_next) * 100 if x_next != 0 else 100

                # ----------------- Tabla -----------------
                r = self.tab.rowCount()
                self.tab.insertRow(r)
                # Cols: Iter, x_{n-1}, x_n, f(x_n), x_{n+1}, Error
                datos_fila = [i, x_prev, x_curr, f_curr, x_next, err]
                
                for j, val in enumerate(datos_fila):
                    item_text = f"{val:.6f}" if j > 0 else str(int(val))
                    it = QTableWidgetItem(item_text)
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tab.setItem(r, j, it)

                # ----------------- Paso a paso HTML -----------------
                html += f"""
                <div style='background:#fff; border:1px solid #e0e0e0; padding:15px;
                            margin-bottom:15px; border-radius:8px; border-left:5px solid #1565c0;'>
                    <b>Iteración {i}</b><br>
                    $x_{{n-1}} = {x_prev:.5f}, \quad f(x_{{n-1}}) = {f_prev:.5f}$<br>
                    $x_n = {x_curr:.5f}, \quad f(x_n) = {f_curr:.5f}$<br>
                    $$x_{{{i+1}}} = {x_curr:.5f} - \\frac{{{f_curr:.4f}({x_curr:.4f} - {x_prev:.4f})}}{{{f_curr:.4f} - {f_prev:.4f}}} 
                    = \\mathbf{{{x_next:.6f}}}$$<br>
                    <small style='color:#666'>Error Relativo: {err:.5f}%</small>
                </div>
                """

                # Actualizar variables para siguiente iteración
                x_prev = x_curr
                f_prev = f_curr
                x_curr = x_next # El nuevo calculado pasa a ser el actual

                # ¿Convergencia?
                if abs(f_curr) < 1e-15 or err < tol:
                    root = x_next
                    html += f"""
                    <div style='background:#e8f5e9; color:#2e7d32; padding:20px;
                                border-radius:8px; text-align:center;'>
                       <h3>✅ Raíz Aproximada: {root:.6f}</h3>
                    </div>
                    """
                    self.lbl_raiz.setText(f"{root:.6f}")
                    self.lbl_iter.setText(str(i))

                    # Graficar punto final
                    self.graficar()
                    self.ax.plot(root, 0, 'o', color='#d32f2f', markersize=6, 
                                 markeredgecolor='white', markeredgewidth=1.1, zorder=10)
                    self.canvas.draw()
                    found = True
                    break

            if not found:
                html += "<div style='color:#d32f2f; text-align:center;'>⚠️ No convergió o límite de iteraciones alcanzado.</div>"
                self.lbl_raiz.setText(f"{x_curr:.6f}")
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
        self.ix0.setText("0.0")
        self.ix1.setText("1.0")
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
        path, _ = QFileDialog.getSaveFileName(self, "Guardar", "secante.xlsx", "Excel (*.xlsx)")
        if path:
            # Columnas corregidas para exportación
            cols = ["Iter", "x(n-1)", "xn", "f(xn)", "x(n+1)", "Err"]
            d = [[self.tab.item(r, c).text() for c in range(6)] for r in range(self.tab.rowCount())]
            pd.DataFrame(d, columns=cols).to_excel(path, index=False)
            QMessageBox.information(self, "Ok", "Exportado correctamente")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = VentanaSecante()
    w.show()
    sys.exit(app.exec())