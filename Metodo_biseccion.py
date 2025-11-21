# -*- coding: utf-8 -*-
"""
biseccion_final_fix_latex.py
"""
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
#  CONFIGURACIÓN Y PARSER MATEMÁTICO
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
    if not s:
        return s
    s = s.replace("√", "sqrt").replace("∛", "cbrt")
    s = s.replace("π", "pi")   # ya NO tocamos 'e'
    s = reemplazar_superindices(s)
    s = s.replace("^", "**")
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
        "cbrt": lambda t: math.copysign(abs(t)**(1/3), t)
    }

def numero_desde_texto(txt: str) -> float:
    expr = normalizar_expresion_usuario(txt)
    try:
        return float(eval(expr, contexto_matematico()))
    except Exception as e:
        raise ValueError(f"Valor incorrecto: {txt}") from e

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
                self._modo_superindice = True
                self._ultima_flecha = False
                return
            self._ultima_flecha = True
            super().keyPressEvent(e)
            return
        self._ultima_flecha = False

        if self._modo_superindice:
            if txt.isdigit():
                self.insert(txt.translate(DIGIT_TO_SUP))
                return
            if key == Qt.Key.Key_Minus or txt == "-":
                self.insert("⁻")
                return
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Space, Qt.Key.Key_Right, Qt.Key.Key_Plus):
                self._modo_superindice = False
                if key == Qt.Key.Key_Down:
                    return
            elif key == Qt.Key.Key_Backspace:
                pass
            else:
                self._modo_superindice = False

        if key == Qt.Key.Key_AsciiCircum:
            self.insert("²")
            return

        if mods == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_R:
                self.insert("√()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_3:
                self.insert("∛()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_L:
                self.insert("ln()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_S:
                self.insert("sen()")
                self.setCursorPosition(self.cursorPosition() - 1)
                return
            if key == Qt.Key.Key_P:
                self.insert("π")
                return

        super().keyPressEvent(e)

# =============================================================================
#  GRÁFICA OPTIMIZADA
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
        ax.grid(True, which='both', linestyle='-', linewidth=0.5,
                color='#d1d5db', alpha=0.8)
        ax.tick_params(axis='both', colors='#4b5563', labelsize=9)

    def graficar_f(self, f, a, b, raiz=None):
        self._configurar_estilo_geogebra()
        span = abs(b - a)
        if span == 0:
            span = 10
        margin = span * 0.2
        x_min, x_max = a - margin, b + margin

        xs = np.linspace(x_min, x_max, 600)
        ys = []
        for x in xs:
            try:
                v = f(x)
                ys.append(v if np.isfinite(v) else np.nan)
            except Exception:
                ys.append(np.nan)
        ys = np.array(ys)

        self.ax.plot(xs, ys, linewidth=2, color="#1565c0", label="f(x)")
        self.ax.set_xlim(x_min, x_max)

        valid_y = ys[np.isfinite(ys)]
        if len(valid_y) > 0:
            ymean, ystd = np.median(valid_y), np.std(valid_y)
            mask = (valid_y > ymean - 4 * ystd) & (valid_y < ymean + 4 * ystd)
            if np.any(mask):
                f_ys = valid_y[mask]
                ymin, ymax = f_ys.min(), f_ys.max()
                pad = (ymax - ymin) * 0.1 if ymax != ymin else 1.0
                self.ax.set_ylim(ymin - pad, ymax + pad)

        if raiz is not None and np.isfinite(raiz):
            try:
                yr = f(raiz)
                self.ax.scatter([raiz], [yr], color="#d32f2f", s=80,
                                zorder=10, edgecolors='white')
                self.ax.vlines(raiz, 0, yr, colors="#d32f2f", linestyles="--")
                self.ax.text(raiz, yr, f" x≈{raiz:.4f}", color="#d32f2f",
                             fontsize=9, fontweight='bold')
            except Exception:
                pass

        self.draw_idle()

# =============================================================================
#  VENTANA PRINCIPAL
# =============================================================================

class VentanaBiseccion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Bisección Pro")
        self.resize(1250, 800)

        self.x_a = None
        self.x_b = None
        self.estableciendo_a = False
        self.estableciendo_b = False
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
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)

        lbl = QLabel("Método de Bisección")
        lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(lbl)

        split = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(split, 1)

        # === IZQ ===
        izq = QWidget()
        v_izq = QVBoxLayout(izq)
        card = QFrame()
        card.setObjectName("Card")
        grid = QGridLayout(card)
        grid.setSpacing(12)

        grid.addWidget(QLabel("Función f(x):"), 0, 0)
        cont = QWidget()
        hf = QHBoxLayout(cont)
        hf.setContentsMargins(0, 0, 0, 0)
        self.le_f = CampoMatematico()
        self.le_f.setPlaceholderText("Ej: x^3 - 2*x - 5")
        self.le_f.textChanged.connect(self.on_func_change)
        self.btn_info = QPushButton("?")
        self.btn_info.setObjectName("BtnInfo")
        self.btn_info.setFixedSize(32, 32)
        self.btn_info.clicked.connect(self.mostrar_atajos)
        hf.addWidget(self.le_f)
        hf.addWidget(self.btn_info)
        grid.addWidget(cont, 0, 1, 1, 2)

        self.lbl_prev = QLabel("...")
        self.lbl_prev.setStyleSheet("color:#1565c0;font-weight:bold")
        grid.addWidget(self.lbl_prev, 1, 1, 1, 2)

        grid.addWidget(QLabel("Intervalo a:"), 2, 0)
        self.le_a = CampoMatematico()
        ba = QPushButton("🎯 A")
        ba.clicked.connect(self.sel_a)
        grid.addWidget(self.le_a, 2, 1)
        grid.addWidget(ba, 2, 2)

        grid.addWidget(QLabel("Intervalo b:"), 3, 0)
        self.le_b = CampoMatematico()
        bb = QPushButton("🎯 B")
        bb.clicked.connect(self.sel_b)
        grid.addWidget(self.le_b, 3, 1)
        grid.addWidget(bb, 3, 2)

        grid.addWidget(QLabel("Tolerancia (%):"), 4, 0)
        self.le_err = CampoMatematico()
        self.le_err.setText("0.01")
        grid.addWidget(self.le_err, 4, 1)

        grid.addWidget(QLabel("Iteraciones:"), 5, 0)
        self.le_iter = CampoMatematico()
        self.le_iter.setText("50")
        grid.addWidget(self.le_iter, 5, 1)
        v_izq.addWidget(card)

        kpi_card = QFrame()
        kpi_card.setObjectName("Card")
        kl = QHBoxLayout(kpi_card)
        self.k_root = self._mk_kpi("Raíz", "--")
        self.k_iter = self._mk_kpi("Pasos", "--")
        self.k_err = self._mk_kpi("Error Final", "--")
        kl.addWidget(self.k_root)
        kl.addWidget(self.k_iter)
        kl.addWidget(self.k_err)
        v_izq.addWidget(kpi_card)

        hbs = QHBoxLayout()
        self.run_btn = QPushButton("🚀 Resolver")
        self.run_btn.setObjectName("BtnRun")
        self.run_btn.setFixedHeight(50)
        self.run_btn.clicked.connect(self.resolver)
        cl_btn = QPushButton("Limpiar")
        cl_btn.setFixedHeight(50)
        cl_btn.clicked.connect(self.limpiar)
        ex_btn = QPushButton("Excel")
        ex_btn.setFixedHeight(50)
        ex_btn.clicked.connect(self.exportar)
        hbs.addWidget(self.run_btn, 2)
        hbs.addWidget(cl_btn, 1)
        hbs.addWidget(ex_btn, 1)
        v_izq.addLayout(hbs)
        v_izq.addStretch()
        split.addWidget(izq)

        # === DER ===
        der = QWidget()
        v_der = QVBoxLayout(der)
        self.tabs = QTabWidget()

        t1 = QWidget()
        v1 = QVBoxLayout(t1)
        self.cv = LienzoGrafica()
        self.tb = NavigationToolbar(self.cv, self)
        v1.addWidget(self.tb)
        v1.addWidget(self.cv)
        self.tabs.addTab(t1, "📈 Gráfica")

        t2 = QWidget()
        v2 = QVBoxLayout(t2)
        self.tab = QTableWidget(0, 5)
        self.tab.setHorizontalHeaderLabels(["#", "a", "b", "c", "f(c)"])
        self.tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v2.addWidget(self.tab)
        self.tabs.addTab(t2, "📋 Tabla de Datos")

        t3 = QWidget()
        v3 = QVBoxLayout(t3)
        self.web = QWebEngineView()
        self.web.setStyleSheet("background-color: #ffffff;")
        v3.addWidget(self.web)
        self.tabs.addTab(t3, "📝 Procedimiento (LaTeX)")

        v_der.addWidget(self.tabs)
        split.addWidget(der)
        split.setSizes([450, 800])

    def _mk_kpi(self, t, v):
        w = QWidget()
        l = QVBoxLayout(w)
        l1 = QLabel(t)
        l1.setStyleSheet("color:#666;font-size:11px;text-transform:uppercase")
        l2 = QLabel(v)
        l2.setObjectName("KV")
        l2.setStyleSheet("font-size:20px;font-weight:bold;color:#1565c0")
        l2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(l1)
        l.addWidget(l2)
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
        a = QPropertyAnimation(self, b"windowOpacity")
        a.setDuration(600)
        a.setStartValue(0)
        a.setEndValue(1)
        a.start()
        self._anim_refs.append(a)

    def mostrar_atajos(self):
        QMessageBox.information(self, "Atajos", """
        <h3>Atajos</h3>
        <ul>
        <li><b>↑+↑</b>: Superíndice</li>
        <li><b>Ctrl+3</b>: Raíz Cúbica</li>
        <li><b>Ctrl+R</b>: Raíz Cuadrada</li>
        <li><b>Ctrl+S</b>: sen()</li>
        <li><b>Ctrl+L</b>: ln()</li>
        <li><b>Ctrl+P</b>: π</li>
        </ul>
        """)

    # --- LÓGICA ---

    def on_func_change(self, txt):
        p = reemplazar_superindices(txt.replace("**", "^").replace("*", "·"))
        self.lbl_prev.setText(f"f(x) = {p}" if txt else "...")
        self.timer_autoplot.start()

    def graficar_automatico(self):
        try:
            self.cv.graficar_f(self._crear_f(), -10, 10)
        except Exception:
            pass

    def _crear_f(self):
        raw = self.le_f.text()
        if not raw.strip():
            raise ValueError("La función f(x) está vacía.")
        code = compile(normalizar_expresion_usuario(raw), "<string>", "eval")
        ctx = contexto_matematico()
        return lambda x: (ctx.update({"x": x}), eval(code, ctx))[1]

    def sel_a(self):
        self.estableciendo_a = True
        self.estableciendo_b = False
        self.run_btn.setEnabled(False)
        QMessageBox.information(self, "Seleccionar A", "Haz clic en la gráfica para fijar 'a'.")

    def sel_b(self):
        if not self.le_a.text():
            QMessageBox.warning(self, "Aviso", "Primero selecciona o escribe el valor de 'a'.")
            return
        self.estableciendo_b = True
        self.estableciendo_a = False
        self.run_btn.setEnabled(False)
        QMessageBox.information(self, "Seleccionar B", "Haz clic en la gráfica para fijar 'b'.")

    def conectar_eventos_grafica(self):
        self.cv.mpl_connect('motion_notify_event', self._hover)
        self.cv.mpl_connect('button_press_event', self._click)

    def _hover(self, e):
        if e.inaxes != self.cv.ax or not (self.estableciendo_a or self.estableciendo_b):
            return
        if hasattr(self, 'tl') and self.tl:
            self.tl.remove()
        c = '#ef5350'
        try:
            f = self._crear_f()
            if self.estableciendo_a:
                if np.isfinite(f(e.xdata)):
                    c = '#66bb6a'
            elif self.estableciendo_b:
                fa = f(float(numero_desde_texto(self.le_a.text())))
                if np.isfinite(f(e.xdata)) and fa * f(e.xdata) < 0:
                    c = '#66bb6a'
        except Exception:
            pass
        self.tl = self.cv.ax.axvline(e.xdata, color=c, linestyle='--')
        self.cv.draw_idle()

    def _click(self, e):
        if e.inaxes != self.cv.ax:
            return
        if self.estableciendo_a:
            self.le_a.setText(f"{e.xdata:.4f}")
            self.estableciendo_a = False
        elif self.estableciendo_b:
            self.le_b.setText(f"{e.xdata:.4f}")
            self.estableciendo_b = False
        else:
            return
        if hasattr(self, 'tl') and self.tl:
            self.tl.remove()
            self.tl = None
        self.run_btn.setEnabled(True)
        self.cv.draw_idle()

    def resolver(self):
        """Resuelve usando bisección SIN cerrar la ventana aunque haya errores."""
        import traceback
        try:
            # 1. Crear f(x)
            try:
                f = self._crear_f()
            except Exception as e:
                QMessageBox.critical(self, "Error en f(x)", f"No se pudo interpretar la función:\n{e}")
                return

            # 2. Leer datos numéricos
            try:
                a = float(numero_desde_texto(self.le_a.text()))
                b = float(numero_desde_texto(self.le_b.text()))
                tol_pct = float(self.le_err.text())      # tolerancia en %
                tol_rel = tol_pct / 100.0                # tolerancia como valor relativo
                mit = int(self.le_iter.text())
            except Exception as e:
                QMessageBox.critical(self, "Datos incorrectos",
                                     f"Revisa a, b, tolerancia o iteraciones.\n{e}")
                return

            if a == b:
                QMessageBox.warning(self, "Error", "El intervalo no puede tener a = b.")
                return

            # 3. Verificar f(a) y f(b)
            try:
                fa = f(a)
                fb = f(b)
            except Exception as e:
                QMessageBox.critical(self, "Error al evaluar f(x)",
                                     f"No se pudo evaluar f(x) en el intervalo inicial:\n{e}")
                return

            if fa * fb > 0:
                QMessageBox.warning(
                    self,
                    "Error",
                    "f(a) y f(b) tienen el mismo signo.\n"
                    "El método de bisección requiere un cambio de signo en el intervalo."
                )
                return

            data_rows = []
            html_steps = []
            c = 0.0
            exito = False
            err = 100.0
            error_final = 0.0

            # --- HTML + MathJax ---
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
            <script id="MathJax-script" async
                    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body { font-family: 'Segoe UI', sans-serif; padding: 20px; color: #333; background-color: #fff; }
                .iter-box { border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fafafa; }
                .iter-title { font-weight: bold; color: #1565c0; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px; margin-bottom: 10px; }
                .math-row { margin: 8px 0; font-size: 1.1em; }
                .success { background-color: #e8f5e9; border: 1px solid #c8e6c9; color: #2e7d32; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: center; }
            </style>
            </head>
            <body>
            """

            # Bucle de bisección
            for i in range(1, mit + 1):
                c_prev = c
                c = (a + b) / 2.0
                try:
                    fc = f(c)
                except Exception as e:
                    QMessageBox.critical(self, "Error en f(c)",
                                         f"No se pudo evaluar f(c) en la iteración {i}:\n{e}")
                    break

                if i == 1 or c == 0:
                    err = 100.0
                else:
                    err = abs((c - c_prev) / c) * 100.0

                data_rows.append((i, a, b, c, fc))

                step_html = f"""
                <div class="iter-box">
                    <div class="iter-title">Iteración {i}</div>
                    <div class="math-row">
                        Intervalo: $[{a:.5f}, {b:.5f}]$
                    </div>
                    <div class="math-row">
                        $$c_{{{i}}} = \\frac{{{a:.5f} + {b:.5f}}}{{2}} = \\mathbf{{{c:.6f}}}$$
                    </div>
                    <div class="math-row">
                        $$f(c_{{{i}}}) = {fc:.6e}$$
                    </div>
                    <div class="math-row">
                        Error relativo: $\\varepsilon \\approx {err:.4f}\\%$
                    </div>
                </div>
                """
                html_steps.append(step_html)

                # Criterio de parada:
                #  - |f(c)| < tol_rel  (tolerancia como residuo)
                #  - o error relativo < tol_pct (en %)
                if abs(fc) < tol_rel or (i > 1 and err < tol_pct):
                    exito = True
                    error_final = err
                    html_steps.append(f"""
                    <div class="success">
                        <strong>¡Convergencia Alcanzada!</strong><br>
                        $$x \\approx {c:.6f}$$<br>
                        Error relativo aproximado: $\\varepsilon \\approx {err:.4f}\\%$
                    </div>
                    """)
                    break

                # Actualizar intervalo
                if fa * fc < 0:
                    b = c
                    fb = fc
                else:
                    a = c
                    fa = fc

            html_content += "".join(html_steps) + "</body></html>"

            # Actualización de la tabla
            self.tab.setUpdatesEnabled(False)
            self.tab.setRowCount(0)
            for r_idx, row_data in enumerate(data_rows):
                self.tab.insertRow(r_idx)
                for c_idx, val in enumerate(row_data):
                    if c_idx == 0:
                        text = str(int(val))
                    else:
                        text = f"{val:.6f}"
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tab.setItem(r_idx, c_idx, item)
            self.tab.setUpdatesEnabled(True)

            # Mostrar LaTeX
            self.web.setHtml(html_content)

            # Graficar
            try:
                a_plot = float(numero_desde_texto(self.le_a.text()))
                b_plot = float(numero_desde_texto(self.le_b.text()))
            except Exception:
                a_plot, b_plot = a, b

            try:
                self.cv.graficar_f(f, a_plot, b_plot, c)
            except Exception:
                pass

            # KPIs
            if data_rows:
                iter_count = len(data_rows)
            else:
                iter_count = 0

            if not exito:
                error_final = err

            self.k_root.findChild(QLabel, "KV").setText(f"{c:.6f}")
            self.k_iter.findChild(QLabel, "KV").setText(str(iter_count))
            self.k_err.findChild(QLabel, "KV").setText(f"{error_final:.4e}%")

            # Ir a la pestaña de LaTeX
            self.tabs.setCurrentIndex(2)

        except Exception as e:
            # Cualquier error que se haya escapado
            import traceback
            tb = traceback.format_exc()
            QMessageBox.critical(
                self,
                "Error inesperado en Resolver",
                f"Ocurrió un error inesperado, pero la ventana NO se cerró.\n\n{e}\n\n{tb}"
            )

    def limpiar(self):
        self.le_f.clear()
        self.le_a.clear()
        self.le_b.clear()
        self.tab.setRowCount(0)
        self.web.setHtml("")
        self.k_root.findChild(QLabel, "KV").setText("--")
        self.k_iter.findChild(QLabel, "KV").setText("--")
        self.k_err.findChild(QLabel, "KV").setText("--")
        self.cv._configurar_estilo_geogebra()
        self.cv.draw_idle()

    def exportar(self):
        if self.tab.rowCount() == 0:
            return
        p, _ = QFileDialog.getSaveFileName(self, "Guardar",
                                           "biseccion.xlsx", "Excel (*.xlsx)")
        if p:
            d = [[self.tab.item(r, c).text() for c in range(5)]
                 for r in range(self.tab.rowCount())]
            pd.DataFrame(d, columns=["Iter", "a", "b", "c", "f(c)"]).to_excel(p, index=False)
            QMessageBox.information(self, "Ok", "Guardado")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VentanaBiseccion()
    w.show()
    sys.exit(app.exec())
