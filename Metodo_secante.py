# -*- coding: utf-8 -*-
"""
metodo_secante_final_ui_fix.py
"""
import os
import sys

# =============================================================================
#  PARCHE GPU (Vital para evitar el error IDCompositionDevice4)
# =============================================================================
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

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
import pandas as pd

# =============================================================================
#  PARSER MATEMÁTICO INTELIGENTE
# =============================================================================

SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_SIGNS = "⁻⁺"
NORMAL_DIGITS = "0123456789"
NORMAL_SIGNS = "-+"
SUP_MAP = str.maketrans(SUP_DIGITS + SUP_SIGNS, NORMAL_DIGITS + NORMAL_SIGNS)
DIGIT_TO_SUP = str.maketrans(NORMAL_DIGITS + "-", SUP_DIGITS + "⁻")

def reemplazar_superindices(expr: str) -> str:
    patt = r"(?P<base>(?:\d+|\w+|[\)\]])+)(?P<sup>[" + SUP_DIGITS + SUP_SIGNS + "]+)"
    def repl(m):
        base = m.group("base")
        sup = m.group("sup").translate(SUP_MAP)
        return f"{base}**({sup})"
    return re.sub(patt, repl, expr)

def normalizar_expresion_usuario(expr: str) -> str:
    s = expr.strip()
    if not s: return s
    s = s.replace("√", "sqrt").replace("∛", "cbrt")
    s = s.replace("π", "pi").replace("e", "e_val")
    s = reemplazar_superindices(s)
    s = s.replace("^", "**")
    # Multiplicación Implícita
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)
    s = re.sub(r'(\))([a-zA-Z0-9(])', r'\1*\2', s)
    s = re.sub(r"\bln\(", "log(", s) 
    s = re.sub(r"\bsen\(", "sin(", s)
    return s

def contexto_matematico():
    return {
        "x": 0,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "log": math.log, "log10": math.log10, "exp": math.exp,
        "sqrt": math.sqrt, "abs": abs, "pi": math.pi, "e": math.e,
        "e_val": math.e, 
        "cbrt": lambda t: math.copysign(abs(t)**(1/3), t)
    }

def numero_desde_texto(txt: str) -> float:
    expr = normalizar_expresion_usuario(txt)
    try:
        return float(eval(expr, contexto_matematico()))
    except:
        raise ValueError(f"Valor incorrecto: {txt}")

# =============================================================================
#  CAMPO INTELIGENTE
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
                self._modo_superindice = True; self._ultima_flecha = False; return 
            self._ultima_flecha = True; super().keyPressEvent(e); return
        self._ultima_flecha = False

        if self._modo_superindice:
            if txt.isdigit(): self.insert(txt.translate(DIGIT_TO_SUP)); return
            if key == Qt.Key.Key_Minus or txt == "-": self.insert("⁻"); return
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Space, Qt.Key.Key_Right, Qt.Key.Key_Plus):
                self._modo_superindice = False; 
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
#  GRÁFICA
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

    def graficar_f(self, f, x0, x1, raiz=None):
        self._configurar_estilo_geogebra()
        
        points = [x0, x1]
        if raiz is not None: points.append(raiz)
        
        min_p, max_p = min(points), max(points)
        span = abs(max_p - min_p)
        if span == 0: span = 5
        
        x_min, x_max = min_p - span*0.5, max_p + span*0.5
        
        xs = np.linspace(x_min, x_max, 600)
        ys = []
        for x in xs:
            try:
                v = f(x)
                ys.append(v if np.isfinite(v) else np.nan)
            except: ys.append(np.nan)
        ys = np.array(ys)

        self.ax.plot(xs, ys, linewidth=2, color="#1565c0", label="f(x)")
        self.ax.set_xlim(x_min, x_max)
        
        valid_y = ys[np.isfinite(ys)]
        if len(valid_y) > 0:
            ymean, ystd = np.median(valid_y), np.std(valid_y)
            mask = (valid_y > ymean - 4*ystd) & (valid_y < ymean + 4*ystd)
            if np.any(mask):
                f_ys = valid_y[mask]
                ymin, ymax = f_ys.min(), f_ys.max()
                pad = (ymax - ymin) * 0.1 if ymax != ymin else 1.0
                self.ax.set_ylim(ymin - pad, ymax + pad)

        try:
            self.ax.scatter([x0, x1], [f(x0), f(x1)], color="#ff9800", s=50, zorder=10)
            self.ax.text(x0, f(x0), " x0", color="#e65100", fontsize=8, fontweight='bold')
            self.ax.text(x1, f(x1), " x1", color="#e65100", fontsize=8, fontweight='bold')
        except: pass

        if raiz is not None and np.isfinite(raiz):
            try:
                yr = f(raiz)
                self.ax.scatter([raiz], [yr], color="#d32f2f", s=80, zorder=10, edgecolors='white')
                self.ax.vlines(raiz, 0, yr, colors="#d32f2f", linestyles="--")
                self.ax.text(raiz, yr, f" Raíz\n {raiz:.4f}", color="#d32f2f", fontsize=9, fontweight='bold')
            except: pass
        
        self.draw_idle()

# =============================================================================
#  VENTANA PRINCIPAL
# =============================================================================

class VentanaSecante(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Método de la Secante")
        self.resize(1250, 800)
        
        self.estableciendo_x0 = False
        self.estableciendo_x1 = False
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
        
        lbl = QLabel("Método de la Secante")
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
        
        # --- AQUI ESTA EL CAMBIO PARA LAS ETIQUETAS ---
        # Usamos HTML <sub> para los subíndices en lugar de LaTeX
        lbl_x0 = QLabel("Valor x<sub>i-1</sub> (x<sub>0</sub>):")
        grid.addWidget(lbl_x0, 2, 0)
        
        self.le_x0 = CampoMatematico(); bx0 = QPushButton("🎯 Sel. x0")
        bx0.clicked.connect(self.sel_x0)
        grid.addWidget(self.le_x0, 2, 1); grid.addWidget(bx0, 2, 2)

        lbl_x1 = QLabel("Valor x<sub>i</sub> (x<sub>1</sub>):")
        grid.addWidget(lbl_x1, 3, 0)
        
        self.le_x1 = CampoMatematico(); bx1 = QPushButton("🎯 Sel. x1")
        bx1.clicked.connect(self.sel_x1)
        grid.addWidget(self.le_x1, 3, 1); grid.addWidget(bx1, 3, 2)
        
        grid.addWidget(QLabel("Tolerancia (%):"), 4, 0)
        self.le_err = CampoMatematico(); self.le_err.setText("0.01")
        grid.addWidget(self.le_err, 4, 1)
        
        grid.addWidget(QLabel("Iteraciones:"), 5, 0)
        self.le_iter = CampoMatematico(); self.le_iter.setText("50")
        grid.addWidget(self.le_iter, 5, 1)
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
        # En la tabla también usamos notación simple o HTML si se soporta, pero para header es mejor texto plano o unicode
        self.tab.setHorizontalHeaderLabels(["#", "x_i", "f(x_i)", "Error(%)", ""])
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
        <li><b>↑+↑</b>: Superíndice</li>
        <li><b>Ctrl+3</b>: Raíz Cúbica</li>
        <li><b>Ctrl+R</b>: Raíz Cuadrada</li>
        </ul>
        """)

    # --- LÓGICA ---

    def on_func_change(self, txt):
        p = reemplazar_superindices(txt.replace("**","^").replace("*","·"))
        self.lbl_prev.setText(f"f(x) = {p}" if txt else "...")
        self.timer_autoplot.start()

    def graficar_automatico(self):
        try: 
            if self.le_x0.text() and self.le_x1.text():
                x0 = float(numero_desde_texto(self.le_x0.text()))
                x1 = float(numero_desde_texto(self.le_x1.text()))
                self.cv.graficar_f(self._crear_f(), x0, x1)
            else:
                self.cv.graficar_f(self._crear_f(), -5, 5)
        except: pass

    def _crear_f(self):
        raw = self.le_f.text()
        if not raw.strip(): raise ValueError("Función vacía")
        code = compile(normalizar_expresion_usuario(raw), "<string>", "eval")
        ctx = contexto_matematico()
        return lambda x: (ctx.update({"x":x}), eval(code, ctx))[1]
    
    def sel_x0(self):
        self.estableciendo_x0 = True; self.estableciendo_x1 = False
        self.run_btn.setEnabled(False)
        QMessageBox.information(self, "Seleccionar x0", "Haz clic en la gráfica.")

    def sel_x1(self):
        self.estableciendo_x1 = True; self.estableciendo_x0 = False
        self.run_btn.setEnabled(False)
        QMessageBox.information(self, "Seleccionar x1", "Haz clic en la gráfica.")

    def conectar_eventos_grafica(self):
        self.cv.mpl_connect('motion_notify_event', self._hover)
        self.cv.mpl_connect('button_press_event', self._click)

    def _hover(self, e):
        if e.inaxes!=self.cv.ax or not (self.estableciendo_x0 or self.estableciendo_x1): return
        if hasattr(self,'tl') and self.tl: self.tl.remove()
        self.tl = self.cv.ax.axvline(e.xdata, color='#66bb6a', linestyle='--'); self.cv.draw_idle()

    def _click(self, e):
        if e.inaxes!=self.cv.ax: return
        if self.estableciendo_x0:
            self.le_x0.setText(f"{e.xdata:.4f}")
            self.estableciendo_x0 = False
        elif self.estableciendo_x1:
            self.le_x1.setText(f"{e.xdata:.4f}")
            self.estableciendo_x1 = False
        else: return
        
        if hasattr(self,'tl') and self.tl: self.tl.remove(); self.tl=None
        self.run_btn.setEnabled(True)
        self.cv.draw_idle()

    def resolver(self):
        try:
            f = self._crear_f()
            x_prev = float(numero_desde_texto(self.le_x0.text())) # x_0
            x_curr = float(numero_desde_texto(self.le_x1.text())) # x_1
            tol_pct = float(self.le_err.text())
            tol = tol_pct / 100.0
            mit = int(self.le_iter.text())
        except Exception as e:
            QMessageBox.critical(self,"Error", str(e)); return

        if x_prev == x_curr:
             QMessageBox.warning(self,"Error", "x0 y x1 no pueden ser iguales."); return

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
            <h3 style="margin-top:0; color:#0d47a1;">Fórmula General Método de la Secante</h3>
            $$ x_{i+1} = x_i - \\frac{f(x_i)(x_{i-1} - x_i)}{f(x_{i-1}) - f(x_i)} $$
        </div>
        """

        try:
            f_prev = f(x_prev)
            f_curr = f(x_curr)
        except:
             QMessageBox.warning(self,"Error", "Error evaluando f(x)."); return
        
        data_rows.append((0, x_prev, f_prev, 0, ""))
        data_rows.append((1, x_curr, f_curr, abs((x_curr - x_prev)/x_curr)*100 if x_curr!=0 else 100, ""))

        for i in range(1, mit + 1):
            denom = f_prev - f_curr
            if abs(denom) < 1e-12:
                QMessageBox.warning(self, "División por cero", "El denominador es casi cero. El método falla."); break

            x_next = x_curr - (f_curr * (x_prev - x_curr) / denom)
            
            try:
                f_next = f(x_next)
            except:
                break

            if x_next == 0: err = 100.0
            else: err = abs((x_next - x_curr) / x_next) * 100.0
            
            data_rows.append((i+1, x_next, f_next, err, ""))

            step_html = f"""
            <div class="iter-box">
                <div class="iter-title">Iteración {i} (Calculando $x_{{{i+1}}}$)</div>
                <div class="math-row">
                    $x_{{{i-1}}} = {x_prev:.5f}, \\quad f(x_{{{i-1}}}) = {f_prev:.5f}$
                </div>
                <div class="math-row">
                    $x_{{{i}}} = {x_curr:.5f}, \\quad f(x_{{{i}}}) = {f_curr:.5f}$
                </div>
                <div class="math-row">
                    $$x_{{{i+1}}} = {x_curr:.5f} - \\frac{{{f_curr:.5f}({x_prev:.5f} - {x_curr:.5f})}}{{{f_prev:.5f} - {f_curr:.5f}}} = \\mathbf{{{x_next:.6f}}}$$
                </div>
                <div class="math-row">
                    Error estimado: $\\varepsilon = {err:.4f}\\%$
                </div>
            </div>
            """
            html_steps.append(step_html)

            if abs(f_next) < tol or err < tol_pct:
                exito = True
                error_final = err
                html_steps.append(f"""
                <div class="success">
                    <strong>¡Convergencia Alcanzada!</strong><br>
                    $$x \\approx {x_next:.6f}$$
                </div>
                """)
                x_curr = x_next
                break
            
            x_prev = x_curr
            f_prev = f_curr
            x_curr = x_next
            f_curr = f_next

        html_content += "".join(html_steps) + "</body></html>"

        self.tab.setUpdatesEnabled(False)
        self.tab.setRowCount(0)
        for r_idx, row_data in enumerate(data_rows):
            self.tab.insertRow(r_idx)
            for c_idx, val in enumerate(row_data):
                if c_idx < 4: 
                    item = QTableWidgetItem(f"{val:.6f}")
                else:
                    item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tab.setItem(r_idx, c_idx, item)
        self.tab.setUpdatesEnabled(True)

        self.web.setHtml(html_content)
        self.cv.graficar_f(f, float(numero_desde_texto(self.le_x0.text())), float(numero_desde_texto(self.le_x1.text())), raiz=x_curr)

        if not exito: error_final = err
        self.k_root.findChild(QLabel,"KV").setText(f"{x_curr:.6f}")
        self.k_iter.findChild(QLabel,"KV").setText(str(len(data_rows)-2))
        self.k_err.findChild(QLabel,"KV").setText(f"{error_final:.4e}%")
        self.tabs.setCurrentIndex(2)

    def limpiar(self):
        self.le_f.clear(); self.le_x0.clear(); self.le_x1.clear()
        self.tab.setRowCount(0); self.web.setHtml("")
        self.k_root.findChild(QLabel,"KV").setText("--")
        self.cv._configurar_estilo_geogebra(); self.cv.draw_idle()

    def exportar(self):
        if self.tab.rowCount()==0: return
        p, _ = QFileDialog.getSaveFileName(self,"Guardar","secante.xlsx","Excel (*.xlsx)")
        if p:
            d = [[self.tab.item(r,c).text() for c in range(5)] for r in range(self.tab.rowCount())]
            pd.DataFrame(d,columns=["Iter","xi","f(xi)","Err(%)", "-"]).to_excel(p,index=False)
            QMessageBox.information(self,"Ok","Guardado")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VentanaSecante()
    w.show()
    sys.exit(app.exec())