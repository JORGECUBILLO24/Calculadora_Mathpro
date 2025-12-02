from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import re
import math
import sys
import pandas as pd

# =============================================================================
#  CONFIGURACIÓN Y PARSER MATEMÁTICO (MEJORADO - VERSIÓN DEFINITIVA)
# =============================================================================

SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_SIGNS = "⁻⁺"
SUP_LETTERS = "ˣʸᶻⁿᵉ"  # Soporte para letras en superíndice
NORMAL_DIGITS = "0123456789"
NORMAL_SIGNS = "-+"
NORMAL_LETTERS = "xyzne"

# Mapas de traducción
ALL_SUP = SUP_DIGITS + SUP_SIGNS + SUP_LETTERS
ALL_NORMAL = NORMAL_DIGITS + NORMAL_SIGNS + NORMAL_LETTERS

SUP_MAP = str.maketrans(ALL_SUP, ALL_NORMAL)
NORMAL_TO_SUP_MAP = str.maketrans(ALL_NORMAL, ALL_SUP)

def reemplazar_superindices(expr: str) -> str:
    patt = r"(?P<base>(?:\d+|\w+|[\)\]])+)(?P<sup>[" + ALL_SUP + "]+)"
    def repl(m):
        base = m.group("base")
        sup = m.group("sup").translate(SUP_MAP)
        return f"{base}**({sup})"
    return re.sub(patt, repl, expr)

def normalizar_expresion_usuario(expr: str) -> str:
    # 0. Limpieza inicial y minúsculas
    s = expr.strip().lower()
    if not s: return s

    # --- NUEVO: SOPORTE PARA ECUACIONES (=) ---
    # Si el usuario escribe "e^x - 3 = 0", lo convertimos internamente a "(e^x - 3) - (0)"
    if "=" in s:
        # Dividimos en dos partes por el signo igual
        partes = s.split("=", 1) 
        lhs = partes[0].strip() # Lado izquierdo
        rhs = partes[1].strip() # Lado derecho
        # Creamos la expresión de resta
        s = f"({lhs}) - ({rhs})"

    # 1. Reemplazos básicos de símbolos matemáticos
    s = s.replace("√", "sqrt").replace("∛", "cbrt")
    s = s.replace("π", "pi")
    
    # 2. Protección de 'e' (Euler)
    # Evita romper palabras como 'sen', 'sec' si contienen 'e'
    s = re.sub(r"\be\b", "e_val", s) 

    # 3. Superíndices y potencias
    s = reemplazar_superindices(s)
    s = s.replace("^", "**")

    # 4. Multiplicación Implícita (Mejorada)
    # Caso: Número seguido de letra (2x -> 2*x)
    s = re.sub(r'(\d)([a-z(])', r'\1*\2', s)
    # Caso: Cierre paréntesis seguido de algo ((x)2 -> (x)*2)
    s = re.sub(r'(\))([a-z0-9(])', r'\1*\2', s)

    # 5. Funciones (Español -> Inglés/Numpy)
    s = re.sub(r"\bln\b", "log", s)
    s = re.sub(r"\barcsen\b", "arcsin", s)
    s = re.sub(r"\bsen\b", "sin", s)
    s = re.sub(r"\barctg\b", "arctan", s)
    s = re.sub(r"\btg\b", "tan", s)
    s = re.sub(r"\bctg\b", "cot", s)
    s = re.sub(r"\bcotg\b", "cot", s)
    s = re.sub(r"\braiz\b", "sqrt", s)

    return s

def contexto_matematico():
    # Usamos NUMPY para robustez gráfica y cálculo vectorizado
    return {
        "x": 0,
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "log": np.log, "log10": np.log10, "exp": np.exp,
        "sqrt": np.sqrt, "abs": np.abs, "pi": np.pi, "e": np.e,
        "e_val": np.e,
        "cot": lambda x: 1 / np.tan(x),
        "cbrt": lambda t: np.cbrt(t) if hasattr(np, 'cbrt') else np.sign(t) * np.abs(t)**(1/3)
    }

def numero_desde_texto(txt: str) -> float:
    expr = normalizar_expresion_usuario(txt)
    try:
        val = eval(expr, contexto_matematico())
        return float(val)
    except Exception as e:
        raise ValueError(f"Valor incorrecto: {txt}") from e

# =============================================================================
#  CAMPO INTELIGENTE (SOPORTE DE LETRAS SUPERÍNDICE)
# =============================================================================

class CampoMatematico(QLineEdit):
    def __init__(self):
        super().__init__()
        self._ultima_flecha = False 
        self._modo_superindice = False 

    def keyPressEvent(self, e):
        key = e.key()
        txt = e.text()
        mods = e.modifiers()

        if key == Qt.Key.Key_Up:
            if self._ultima_flecha:
                self._modo_superindice = True
                self._ultima_flecha = False
                return 
            self._ultima_flecha = True
            super().keyPressEvent(e)
            return
        self._ultima_flecha = False

        if self._modo_superindice:
            if txt in ALL_NORMAL and txt != "":
                self.insert(txt.translate(NORMAL_TO_SUP_MAP)); 
                return
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Space, Qt.Key.Key_Right, Qt.Key.Key_Plus):
                self._modo_superindice = False
                if key == Qt.Key.Key_Down: return 
            elif key == Qt.Key.Key_Backspace: pass
            else: self._modo_superindice = False

        if key == Qt.Key.Key_AsciiCircum: self.insert("²"); return
        
        if mods == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_R: self.insert("√()"); self.setCursorPosition(self.cursorPosition()-1); return
            if key == Qt.Key.Key_3: self.insert("∛()"); self.setCursorPosition(self.cursorPosition()-1); return
            if key == Qt.Key.Key_L: self.insert("ln()"); self.setCursorPosition(self.cursorPosition()-1); return
            if key == Qt.Key.Key_S: self.insert("sen()"); self.setCursorPosition(self.cursorPosition()-1); return
            if key == Qt.Key.Key_P: self.insert("π"); return

        super().keyPressEvent(e)

# =============================================================================
#  GRÁFICA OPTIMIZADA (NUMPY + ANTI-ASÍNTOTAS)
# =============================================================================

class LienzoGrafica(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self._configurar_estilo_geogebra()

    def _configurar_estilo_geogebra(self):
        ax = self.ax
        ax.clear()
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.grid(True, which='both', linestyle='-', linewidth=0.5, color='#d1d5db', alpha=0.8)
        ax.tick_params(axis='both', colors='#4b5563', labelsize=9)

    def graficar_f(self, f, x0, raiz=None):
        self._configurar_estilo_geogebra()
        
        # Determinar centro y rango dinámico
        center = x0 if raiz is None else raiz
        if np.abs(center) > 1e6: span = np.abs(center)*0.2 
        else: span = 10
        
        x_min, x_max = center - span, center + span
        
        # 1. Generación de datos VECTORIZADA
        xs = np.linspace(x_min, x_max, 1000)
        try:
            ys = f(xs)
            if np.isscalar(ys): ys = np.full_like(xs, ys)
        except:
            ys = []
            for x in xs:
                try: ys.append(f(x))
                except: ys.append(np.nan)
            ys = np.array(ys)

        # 2. Limpieza
        if np.iscomplexobj(ys): ys = ys.real
        ys[np.isinf(ys)] = np.nan

        # 3. Anti-Asíntotas
        threshold = np.nanpercentile(np.abs(ys), 90) * 2
        if np.isnan(threshold) or threshold < 1: threshold = 10
        dy = np.abs(np.diff(ys, prepend=ys[0]))
        ys[dy > threshold] = np.nan

        # 4. Graficar
        self.ax.plot(xs, ys, linewidth=2, color="#1565c0", label="f(x)")
        self.ax.set_xlim(x_min, x_max)
        
        # 5. Escalado Inteligente Y
        valid_y = ys[np.isfinite(ys)]
        if len(valid_y) > 0:
            ymin_p, ymax_p = np.percentile(valid_y, [2, 98])
            h = ymax_p - ymin_p
            if h == 0: h = 1.0
            self.ax.set_ylim(ymin_p - h*0.2, ymax_p + h*0.2)

        # Puntos de interés
        try:
            y0 = float(f(x0))
            if np.isfinite(y0):
                self.ax.scatter([x0], [y0], color="#ff9800", s=60, zorder=10, label="x0")
                self.ax.text(x0, y0, " x0", color="#e65100", fontsize=9, fontweight='bold')
        except: pass

        if raiz is not None and np.isfinite(raiz):
            try:
                yr = float(f(raiz))
                if np.isfinite(yr):
                    self.ax.scatter([raiz], [yr], color="#d32f2f", s=80, zorder=10, edgecolors='white')
                    self.ax.vlines(raiz, *self.ax.get_ylim(), colors="#d32f2f", linestyles="--")
                    self.ax.text(raiz, yr, f" x≈{raiz:.4f}", color="#d32f2f", fontsize=9, fontweight='bold')
            except: pass
        
        self.draw_idle()

# =============================================================================
#  VENTANA PRINCIPAL NEWTON-RAPHSON
# =============================================================================

class VentanaNewton(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Newton-Raphson Pro")
        self.resize(1250, 800)
        
        self.x0 = None
        self.seleccionando_x0 = False
        self._anim_refs = []
        
        self.timer_autoplot = QTimer()
        self.timer_autoplot.setInterval(600)
        self.timer_autoplot.setSingleShot(True)
        self.timer_autoplot.timeout.connect(self.graficar_automatico)

        self.construir_ui()
        self._aplicar_estilos()
        self._animar_entrada()
        self.conectar_eventos_grafica()

    def construir_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(15,15,15,15)
        
        lbl = QLabel("Método de Newton-Raphson")
        lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(lbl)
        
        split = QSplitter(Qt.Orientation.Horizontal); root.addWidget(split, 1)

        # === IZQ ===
        izq = QWidget(); v_izq = QVBoxLayout(izq)
        card = QFrame(); card.setObjectName("Card")
        grid = QGridLayout(card); grid.setSpacing(12)
        
        grid.addWidget(QLabel("Función f(x):"), 0, 0)
        cont = QWidget(); hf = QHBoxLayout(cont); hf.setContentsMargins(0,0,0,0)
        self.le_f = CampoMatematico(); self.le_f.setPlaceholderText("Ej: x^3 - 2x - 5")
        self.le_f.textChanged.connect(self.on_func_change)
        self.btn_info = QPushButton("?"); self.btn_info.setObjectName("BtnInfo")
        self.btn_info.setFixedSize(32,32); self.btn_info.clicked.connect(self.mostrar_atajos)
        hf.addWidget(self.le_f); hf.addWidget(self.btn_info)
        grid.addWidget(cont, 0, 1, 1, 2)
        
        self.lbl_prev = QLabel("..."); self.lbl_prev.setStyleSheet("color:#1565c0;font-weight:bold")
        grid.addWidget(self.lbl_prev, 1, 1, 1, 2)
        
        grid.addWidget(QLabel("Valor Inicial ($x_0$):"), 2, 0)
        self.le_x0 = CampoMatematico(); bx = QPushButton("🎯 Seleccionar")
        bx.clicked.connect(self.sel_x0)
        grid.addWidget(self.le_x0, 2, 1); grid.addWidget(bx, 2, 2)
        
        grid.addWidget(QLabel("Tolerancia (%):"), 3, 0)
        self.le_err = CampoMatematico(); self.le_err.setText("0.01")
        grid.addWidget(self.le_err, 3, 1)
        
        grid.addWidget(QLabel("Iteraciones:"), 4, 0)
        self.le_iter = CampoMatematico(); self.le_iter.setText("50")
        grid.addWidget(self.le_iter, 4, 1)
        v_izq.addWidget(card)

        kpi_card = QFrame(); kpi_card.setObjectName("Card")
        kl = QHBoxLayout(kpi_card)
        self.k_root = self._mk_kpi("Raíz", "--")
        self.k_iter = self._mk_kpi("Pasos", "--")
        self.k_err = self._mk_kpi("Error Final", "--")
        kl.addWidget(self.k_root); kl.addWidget(self.k_iter); kl.addWidget(self.k_err)
        v_izq.addWidget(kpi_card)

        hbs = QHBoxLayout()
        self.run_btn = QPushButton("🚀 Resolver"); self.run_btn.setObjectName("BtnRun")
        self.run_btn.setFixedHeight(50); self.run_btn.clicked.connect(self.resolver)
        cl_btn = QPushButton("Limpiar"); cl_btn.setFixedHeight(50); cl_btn.clicked.connect(self.limpiar)
        ex_btn = QPushButton("Excel"); ex_btn.setFixedHeight(50); ex_btn.clicked.connect(self.exportar)
        hbs.addWidget(self.run_btn, 2); hbs.addWidget(cl_btn, 1); hbs.addWidget(ex_btn, 1)
        v_izq.addLayout(hbs); v_izq.addStretch()
        split.addWidget(izq)

        # === DER ===
        der = QWidget(); v_der = QVBoxLayout(der)
        self.tabs = QTabWidget()
        
        t1 = QWidget(); v1 = QVBoxLayout(t1)
        self.cv = LienzoGrafica(); self.tb = NavigationToolbar(self.cv, self)
        v1.addWidget(self.tb); v1.addWidget(self.cv)
        self.tabs.addTab(t1, "📈 Gráfica")
        
        t2 = QWidget(); v2 = QVBoxLayout(t2)
        self.tab = QTableWidget(0, 5)
        self.tab.setHorizontalHeaderLabels(["#", "x_i", "f(x_i)", "f'(x_i)", "Error(%)"])
        self.tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v2.addWidget(self.tab)
        self.tabs.addTab(t2, "📋 Tabla")
        
        t3 = QWidget(); v3 = QVBoxLayout(t3)
        self.web = QWebEngineView()
        self.web.setStyleSheet("background-color: #ffffff;")
        v3.addWidget(self.web)
        self.tabs.addTab(t3, "📝 Procedimiento")
        
        v_der.addWidget(self.tabs)
        split.addWidget(der)
        split.setSizes([450, 800])

    def _mk_kpi(self, t, v):
        w = QWidget(); l = QVBoxLayout(w)
        l1 = QLabel(t); l1.setStyleSheet("color:#666;font-size:11px;text-transform:uppercase")
        l2 = QLabel(v); l2.setObjectName("KV"); l2.setStyleSheet("font-size:20px;font-weight:bold;color:#1565c0")
        l2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(l1); l.addWidget(l2)
        return w

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget{background:#f4f6f9;color:#333;font-family:'Segoe UI',sans-serif;font-size:14px}
            QFrame#Card{background:white;border:1px solid #e0e0e0;border-radius:12px}
            QLineEdit{border:1px solid #ccc;border-radius:8px;padding:8px;background:#fff}
            QLineEdit:focus{border:2px solid #1565c0}
            QPushButton{background:#e9ecef;border:none;border-radius:8px;padding:0 15px;font-weight:600}
            QPushButton:hover{background:#dee2e6}
            QPushButton#BtnRun{background:#1565c0;color:white;font-size:16px;font-weight:bold}
            QPushButton#BtnRun:hover{background:#0d47a1}
            QPushButton#BtnInfo{background:#e3f2fd;color:#1565c0;border-radius:16px}
            QTabWidget::pane{border:1px solid #ddd;background:white;border-radius:8px}
            QTabBar::tab{background:#f1f3f5;padding:10px 15px;margin-right:2px;border-top-left-radius:6px;border-top-right-radius:6px}
            QTabBar::tab:selected{background:white;border-bottom:3px solid #1565c0;color:#1565c0;font-weight:bold}
        """)

    def _animar_entrada(self):
        a = QPropertyAnimation(self, b"windowOpacity"); a.setDuration(600)
        a.setStartValue(0); a.setEndValue(1); a.start()
        self._anim_refs.append(a)

    def mostrar_atajos(self):
        QMessageBox.information(self, "Atajos", """
        <h3>Atajos</h3>
        <ul>
        <li><b>↑+↑</b>: Superíndice (e⁻²ˣ)</li>
        <li><b>Ctrl+3</b>: Raíz Cúbica</li>
        <li><b>Ctrl+R</b>: Raíz Cuadrada</li>
        <li><b>Ctrl+S</b>: sen()</li>
        <li><b>Ctrl+L</b>: ln()</li>
        </ul>
        """)

    # --- LÓGICA ---

    def on_func_change(self, txt):
        p = reemplazar_superindices(txt.replace("**","^").replace("*","·"))
        self.lbl_prev.setText(f"f(x) = {p}" if txt else "...")
        self.timer_autoplot.start()

    def graficar_automatico(self):
        try: 
            if self.le_x0.text():
                x0 = float(numero_desde_texto(self.le_x0.text()))
                self.cv.graficar_f(self._crear_f(), x0)
            else:
                self.cv.graficar_f(self._crear_f(), 0)
        except: pass

    def _crear_f(self):
        raw = self.le_f.text()
        if not raw.strip(): raise ValueError("Función vacía")
        code = compile(normalizar_expresion_usuario(raw), "<string>", "eval")
        ctx = contexto_matematico()
        return lambda x: (ctx.update({"x":x}), eval(code, ctx))[1]
    
    def _derivada(self, f, x, h=1e-5):
        # Derivada numérica centrada simple
        return (f(x + h) - f(x - h)) / (2 * h)

    def sel_x0(self):
        self.seleccionando_x0 = True
        self.run_btn.setEnabled(False)
        QMessageBox.information(self, "Seleccionar X0", "Haz clic en la gráfica.")

    def conectar_eventos_grafica(self):
        self.cv.mpl_connect('motion_notify_event', self._hover)
        self.cv.mpl_connect('button_press_event', self._click)

    def _hover(self, e):
        if e.inaxes!=self.cv.ax or not self.seleccionando_x0: return
        if hasattr(self,'tl') and self.tl: self.tl.remove()
        self.tl = self.cv.ax.axvline(e.xdata, color='#66bb6a', linestyle='--'); self.cv.draw_idle()

    def _click(self, e):
        if e.inaxes!=self.cv.ax: return
        if self.seleccionando_x0:
            self.le_x0.setText(f"{e.xdata:.4f}")
            self.seleccionando_x0 = False
            if hasattr(self,'tl') and self.tl: self.tl.remove(); self.tl=None
            self.run_btn.setEnabled(True)
            self.cv.draw_idle()

    def resolver(self):
        try:
            f = self._crear_f()
            x_i = float(numero_desde_texto(self.le_x0.text()))
            tol_pct = float(self.le_err.text())
            tol = tol_pct / 100.0
            mit = int(self.le_iter.text())
        except Exception as e:
            QMessageBox.critical(self,"Error", str(e)); return

        data_rows = []
        html_steps = []
        exito = False
        error_final = 0
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
        <script>
        window.MathJax = {
          tex: {
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
          },
          svg: { fontCache: 'global' }
        };
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
            body { font-family: 'Segoe UI', sans-serif; padding: 20px; color: #333; background-color: #fff; }
            .formula-box { border: 2px solid #1565c0; border-radius: 8px; padding: 15px; margin-bottom: 20px; background: #e3f2fd; text-align: center; }
            .iter-box { border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fafafa; }
            .iter-title { font-weight: bold; color: #1565c0; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px; margin-bottom: 10px; }
            .math-row { margin: 8px 0; font-size: 1.1em; }
            .success { background-color: #e8f5e9; border: 1px solid #c8e6c9; color: #2e7d32; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: center; }
        </style>
        </head>
        <body>
        
        <div class="formula-box">
            <h3 style="margin-top:0; color:#0d47a1;">Fórmula General Newton-Raphson</h3>
            $$ x_{i+1} = x_i - \\frac{f(x_i)}{f'(x_i)} $$
        </div>
        """

        for i in range(1, mit + 1):
            try:
                y = float(f(x_i))
                dy = float(self._derivada(f, x_i))
            except:
                QMessageBox.warning(self, "Error", "No se pudo evaluar f(x) o f'(x)."); break

            if abs(dy) < 1e-12:
                QMessageBox.warning(self, "Derivada Cero", f"La derivada es casi 0 en x={x_i:.4f}. El método falla."); break

            x_next = x_i - (y / dy)
            
            if i == 1 or x_next == 0: err = 100.0
            else: err = abs((x_next - x_i) / x_next) * 100.0
            
            data_rows.append((i, x_i, y, dy, err))

            step_html = f"""
            <div class="iter-box">
                <div class="iter-title">Iteración {i}</div>
                <div class="math-row">
                    Valores: $x_{{{i-1}}} = {x_i:.6f}, \\quad f(x_{{{i-1}}}) = {y:.6f}, \\quad f'(x_{{{i-1}}}) = {dy:.6f}$
                </div>
                <div class="math-row">
                    $$x_{{{i}}} = {x_i:.6f} - \\frac{{{y:.6f}}}{{{dy:.6f}}} = \\mathbf{{{x_next:.6f}}}$$
                </div>
                <div class="math-row">
                    Error: $\\varepsilon = {err:.4f}\\%$
                </div>
            </div>
            """
            html_steps.append(step_html)

            # Criterio de Convergencia
            if abs(y) < tol or (i > 1 and err < tol_pct):
                exito = True
                error_final = err
                html_steps.append(f"""
                <div class="success">
                    <strong>¡Convergencia Alcanzada!</strong><br>
                    $$x \\approx {x_next:.6f}$$
                </div>
                """)
                # Agregar la fila final para mostrar que f(x_next) es casi 0
                data_rows.append((i+1, x_next, float(f(x_next)), float(self._derivada(f, x_next)), 0.0))
                x_i = x_next
                break
            
            x_i = x_next

        html_content += "".join(html_steps) + "</body></html>"

        self.tab.setUpdatesEnabled(False)
        self.tab.setRowCount(0)
        for r_idx, row_data in enumerate(data_rows):
            self.tab.insertRow(r_idx)
            for c_idx, val in enumerate(row_data):
                if c_idx == 0: text = str(int(val))
                else: text = f"{val:.6f}"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tab.setItem(r_idx, c_idx, item)
        self.tab.setUpdatesEnabled(True)

        self.web.setHtml(html_content)
        
        # Graficar con punto x0 y raíz
        try:
            initial_x0 = float(numero_desde_texto(self.le_x0.text()))
            self.cv.graficar_f(f, initial_x0, raiz=x_i)
        except: pass

        if not exito: error_final = err
        self.k_root.findChild(QLabel,"KV").setText(f"{x_i:.6f}")
        self.k_iter.findChild(QLabel,"KV").setText(str(len(data_rows)))
        self.k_err.findChild(QLabel,"KV").setText(f"{error_final:.4e}%")
        self.tabs.setCurrentIndex(2)

    def limpiar(self):
        self.le_f.clear(); self.le_x0.clear()
        self.tab.setRowCount(0); self.web.setHtml("")
        self.k_root.findChild(QLabel,"KV").setText("--")
        self.k_iter.findChild(QLabel,"KV").setText("--")
        self.k_err.findChild(QLabel,"KV").setText("--")
        self.cv._configurar_estilo_geogebra(); self.cv.draw_idle()

    def exportar(self):
        if self.tab.rowCount()==0: return
        p, _ = QFileDialog.getSaveFileName(self,"Guardar","newton.xlsx","Excel (*.xlsx)")
        if p:
            d = [[self.tab.item(r,c).text() for c in range(5)] for r in range(self.tab.rowCount())]
            pd.DataFrame(d,columns=["Iter","xi","f(xi)","f'(xi)","Err(%)"]).to_excel(p,index=False)
            QMessageBox.information(self,"Ok","Guardado")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VentanaNewton()
    w.show()
    sys.exit(app.exec())