# -- coding: utf-8 --
from __future__ import annotations
import math
import re
import warnings
from dataclasses import dataclass
from typing import Callable, Optional, List, Tuple

import numpy as np
import pandas
import openpyxl
from sympy import (
    symbols, lambdify, exp, sin, cos, tan, sqrt, log,
    asin, acos, atan, sinh, cosh, tanh, pi, E
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)

from PyQt6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup, QRect, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDoubleSpinBox, QSpinBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QSplitter, QSizePolicy,
    QGridLayout, QTabWidget, QFileDialog, QToolButton, QTextEdit, QCheckBox
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# ----------------- Helpers y validaciones -----------------

X = symbols("x")
SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_SIGNS = "⁻⁺"
SUP_MAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")


def reemplazar_superindices_por_potencia(expr: str) -> str:
    patt = r"(?P<base>(?:\d+|\w+|[\)\]])+)(?P<sup>[{}{}]+)".format(SUP_DIGITS, SUP_SIGNS)
    def repl(m):
        base = m.group("base")
        sup = m.group("sup").translate(SUP_MAP)
        return f"{base}({sup})"
    return re.sub(patt, repl, expr)


def _preprocesos_adicionales(s: str) -> str:
    """Normalizaciones amigables: √x, cos x, 2x, x3, etc."""
    if not s:
        return s

    s = re.sub(r"√\s*\(([^)]+)\)", r"sqrt(\1)", s)
    s = re.sub(r"√\s*([A-Za-z0-9_\.]+)", r"sqrt(\1)", s)

    funcs = r"(?:sin|cos|tan|log|ln|sqrt|exp|asin|acos|atan|sinh|cosh|tanh)"
    s = re.sub(rf"\b({funcs})\s+([A-Za-z0-9_\.\-]+)\b", r"\1(\2)", s)

    s = re.sub(
        r"(?P<a>(?:\d+\.?\d*|\b[xX]\b|\)|\]))\s*(?P<b>(?:\b[A-Za-z_][A-Za-z0-9_]*\b|\())",
        r"\g<a>*\g<b>",
        s
    )

    s = re.sub(r"\b(x)\s*([0-9])\b", r"\1**\2", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalizar_expresion_usuario(user_expr: str) -> str:
    s = user_expr.strip()
    if not s:
        return s

    try:
        s = _preprocesos_adicionales(s)
    except Exception:
        pass

    if "=" in s:
        p = s.split("=")
        if len(p) != 2:
            raise ValueError("Sólo una igualdad con '='.")
        s = f"({p[0].strip()}) - ({p[1].strip()})"

    s = re.sub(r"\bX\b", "x", s)
    s = s.replace("^", "")
    s = re.sub(r"\bln\(", "log(", s, flags=re.IGNORECASE)
    s = re.sub(r"\bsen\(", "sin(", s, flags=re.IGNORECASE)
    s = s.replace("π", "pi")
    s = reemplazar_superindices_por_potencia(s)
    return s


def comprobar_parentesis_y_comillas(s: str) -> Tuple[bool, str]:
    stack = []
    pares = {"(": ")", "[": "]", "{": "}"}
    for i, ch in enumerate(s):
        if ch in pares.keys():
            stack.append((ch, i))
        elif ch in pares.values():
            if not stack:
                return False, f"Paréntesis desbalanceado: '{ch}' en posición {i}"
            top, idx = stack.pop()
            if pares[top] != ch:
                return False, f"Tipo de paréntesis incompatible en posición {i}: '{top}' ... '{ch}'"
    if stack:
        top, idx = stack[-1]
        return False, f"Falta cerrar paréntesis '{top}' (posición {idx})"
    single = s.count("'") % 2 == 0
    double = s.count('"') % 2 == 0
    if not single:
        return False, "Número impar de comillas simples"
    if not double:
        return False, "Número impar de comillas dobles"
    return True, ""


def numero_desde_texto(txt: str) -> float:
    s = normalizar_expresion_usuario(txt.strip())
    ok, msg = comprobar_parentesis_y_comillas(s)
    if not ok:
        raise ValueError("Expresión inválida: {}".format(msg))
    expr = parse_expr(
        s,
        transformations=(standard_transformations + (implicit_multiplication_application,)),
        local_dict={
            "x": X, "pi": pi, "e": E, "abs": abs,
            "asin": asin, "acos": acos, "atan": atan,
            "sinh": sinh, "cosh": cosh, "tanh": tanh,
            "exp": exp, "sqrt": sqrt, "log": log, "sin": sin, "cos": cos, "tan": tan
        }
    )
    free_symbols = getattr(expr, "free_symbols", set())
    if free_symbols:
        raise ValueError("Se esperaba un número (ej. 1.5) en xi/xf; no incluyas 'x' u otras variables.")
    return float(expr.evalf())


def vista_previa_superindice(expr: str) -> str:
    s = re.sub(r"\^\(([^)]+)\)", lambda m: "<sup>" + m.group(1) + "</sup>", expr)
    s = re.sub(r"\^([\-+]?\d+(?:\.\d+)?)", lambda m: "<sup>" + m.group(1) + "</sup>", s)
    s = re.sub(r"\^([a-zA-Z])", lambda m: "<sup>" + m.group(1) + "</sup>", s)
    return "<span style='font-size:18px;'>f(x) = {}</span>".format(s)


# ----------------- Estructuras -----------------

@dataclass
class FilaFalsa:
    i: int
    xi: float
    xf: float
    xr: float
    fxi: float
    fxf: float
    fxr: float
    error_pct: Optional[float]
    subintervalo: str


@dataclass
class ResultadoFalsa:
    raiz: Optional[float]
    iteraciones: int
    ultimo_error_pct: Optional[float]
    tabla: List[FilaFalsa]
    mensaje: str
    pasos: List[str]


# ----------------- Detección de intervalos por muestreo -----------------

def detectar_intervalos_cambio_signo(f: Callable[[float], float], a: float, b: float, muestras: int = 2000, eps: float = 1e-12):
    xs = np.linspace(a, b, muestras)
    ys = np.empty_like(xs)
    finite_mask = np.ones_like(xs, dtype=bool)
    for i, x in enumerate(xs):
        try:
            y = f(x)
            ys[i] = float(y)
            if not np.isfinite(ys[i]):
                finite_mask[i] = False
        except Exception:
            ys[i] = np.nan
            finite_mask[i] = False
    signos = np.sign(ys)
    intervals = []
    for i in range(len(xs) - 1):
        if finite_mask[i] and finite_mask[i+1]:
            if signos[i] * signos[i+1] < 0:
                intervals.append((float(xs[i]), float(xs[i+1])))
    zeros_idx = np.where((np.abs(ys) <= eps) & finite_mask)[0]
    for zi in zeros_idx:
        left = zi - 1
        right = zi + 1
        while left >= 0 and not finite_mask[left]:
            left -= 1
        while right < len(xs) and not finite_mask[right]:
            right += 1
        if 0 <= left < len(xs) and 0 <= right < len(xs):
            if np.isfinite(ys[left]) and np.isfinite(ys[right]) and np.sign(ys[left]) * np.sign(ys[right]) < 0:
                intervals.append((float(xs[left]), float(xs[right])))
    merged = []
    for (l, r) in intervals:
        if not merged:
            merged.append((l, r))
        else:
            pl, pr = merged[-1]
            if l <= pr + 1e-8:
                merged[-1] = (pl, max(pr, r))
            else:
                merged.append((l, r))
    return merged


# ----------------- Gráfica -----------------

class LienzoGrafica(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 3), dpi=120)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.ax.grid(True, alpha=.35)

    def graficar_f(self, f, a, b, raiz=None):
        self.ax.clear(); self.ax.grid(True, alpha=.35); self.ax.set_title("f(x) en [a, b]")
        xs = np.linspace(a, b, 600)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ys = np.array([f(x) for x in xs], dtype=float)
        self.ax.plot(xs, ys, linewidth=2)
        self.ax.axhline(0, color="black", linewidth=1)
        if raiz is not None and np.isfinite(raiz):
            try:
                self.ax.scatter([raiz], [f(raiz)], s=80, zorder=5)
                self.ax.axvline(raiz, linestyle="--", linewidth=1)
            except Exception:
                pass
        self.draw_idle()

    def marcar_raiz(self, f, raiz):
        if raiz is None or not np.isfinite(raiz):
            return
        try:
            self.ax.scatter([raiz], [f(raiz)], s=80, zorder=5)
            self.ax.axvline(raiz, linestyle="--", linewidth=1)
            self.draw_idle()
        except Exception:
            pass


# ----------------- Interfaz y lógica -----------------

class Tarjeta(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")


class VentanaFalsaPosicion(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowFlag(Qt.Window, True)
        except Exception:
            pass
        self.setWindowTitle("Método de Falsa Posición — Compacto y amigable")
        self.resize(1180, 720)
        self.setMinimumSize(1020, 660)
        self._anim_refs = []
        self._last_norm: Optional[str] = None
        self._last_range: Optional[Tuple[float, float]] = None
        self.construir_ui()
        self.aplicar_estilos()
        self._animar_entrada()

    def construir_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        titulo = QLabel("Método de Falsa Posición (Regula Falsi)")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        root.addWidget(titulo)

        split = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(split, 1)

        # Izquierda: entradas
        izquierdo = QWidget(); L = QVBoxLayout(izquierdo); L.setSpacing(10)
        izquierdo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        tarjeta_entrada = Tarjeta()
        grid = QGridLayout(tarjeta_entrada)
        grid.setHorizontalSpacing(10); grid.setVerticalSpacing(8); grid.setContentsMargins(12, 12, 12, 12)

        r = 0
        self.le_f = QLineEdit(); self.le_f.setPlaceholderText("Ej.: cos(x) - x = 0   ó   x^3 - x - 2")
        self.le_f.textChanged.connect(self.actualizar_vista_previa)
        self.lbl_prev = QLabel("<i>Escribe una función...</i>")
        self.lbl_prev.setTextFormat(Qt.TextFormat.RichText); self.lbl_prev.setWordWrap(True)

        # fuente grande para campos numéricos
        big_font = QFont("Segoe UI", 12, QFont.Weight.DemiBold)
        # campos xi/xf y error con tamaño mayor y alineación a la derecha
        self.le_xi = QLineEdit(""); self.le_xi.setFont(big_font); self.le_xi.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.le_xf = QLineEdit(""); self.le_xf.setFont(big_font); self.le_xf.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.le_err_pct = QLineEdit("1"); self.le_err_pct.setFont(big_font); self.le_err_pct.setAlignment(Qt.AlignmentFlag.AlignRight)
        # placeholder para guiar
        self.le_xi.setPlaceholderText("Dejar vacío para auto-detectar")
        self.le_xf.setPlaceholderText("Dejar vacío para auto-detectar")
        self.le_err_pct.setPlaceholderText("Ej: 1  ó 0.01  (porcentaje)")

        self.sp_iter = QSpinBox(); self.sp_iter.setRange(1, 5000); self.sp_iter.setValue(50)

        grid.addWidget(self.etiqueta_negrita("Escribe la función"), r, 0, 1, 2); r += 1
        grid.addWidget(self.le_f, r, 0, 1, 2); r += 1
        grid.addWidget(self.etiqueta_suave("Vista previa"), r, 0, 1, 2); r += 1
        grid.addWidget(self.lbl_prev, r, 0, 1, 2); r += 1

        grid.addWidget(self.etiqueta_negrita("xi (límite izquierdo)"), r, 0)
        grid.addWidget(self.etiqueta_negrita("xf (límite derecho)"), r, 1); r += 1
        grid.addWidget(self.le_xi, r, 0); grid.addWidget(self.le_xf, r, 1); r += 1

        self.le_singulares = QLineEdit()
        self.le_singulares.setPlaceholderText("Opcional: puntos singulares (ej: -1, 0.5)")
        grid.addWidget(self.etiqueta_negrita("Puntos singulares (opc.)"), r, 0)
        grid.addWidget(self.le_singulares, r, 1); r += 1

        self.chk_prefer_pos = QCheckBox("Preferir raíz positiva al auto-detectar")
        self.chk_prefer_pos.setChecked(True)
        grid.addWidget(self.chk_prefer_pos, r, 0, 1, 2); r += 1

        grid.addWidget(self.etiqueta_negrita("Error permitido (%)"), r, 0)
        grid.addWidget(self.etiqueta_negrita("Iteraciones máx."), r, 1); r += 1
        grid.addWidget(self.le_err_pct, r, 0); grid.addWidget(self.sp_iter, r, 1); r += 1

        L.addWidget(tarjeta_entrada)

        # KPIs: agrandar la cifra y centrarla
        kpi = Tarjeta(); K = QHBoxLayout(kpi)
        self.k_roots = self.crear_kpi("Número de raíces (estimado)", "--")
        self.k_err = self.crear_kpi("Error relativo (%)", "--")
        self.k_root = self.crear_kpi("Raíz aproximada", "--")
        # mejorar apariencia de la etiqueta KPI (hacer cifras grandes y centradas)
        for w in (self.k_roots, self.k_err, self.k_root):
            lbl_val = w.findChild(QLabel, "KPI")
            if lbl_val:
                lbl_val.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
                lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        K.addWidget(self.k_roots, 1); K.addWidget(self.k_err, 1); K.addWidget(self.k_root, 1)
        L.addWidget(kpi)

        # Botones
        btns = QHBoxLayout(); btns.setSpacing(8)
        self.bt_run = QPushButton("Resolver")
        self.bt_plot = QPushButton("Graficar")
        self.bt_clear = QPushButton("Limpiar")
        self.bt_export = QPushButton("Exportar Excel")
        for b in (self.bt_run, self.bt_plot, self.bt_clear, self.bt_export):
            b.setMinimumHeight(36)
        self.bt_run.clicked.connect(self.resolver)
        self.bt_plot.clicked.connect(self.graficar)
        self.bt_clear.clicked.connect(self.limpiar)
        self.bt_export.clicked.connect(self.exportar_excel)
        btns.addWidget(self.bt_run, 3); btns.addWidget(self.bt_plot, 2); btns.addWidget(self.bt_clear, 1); btns.addWidget(self.bt_export, 2)
        L.addLayout(btns)

        # Teclado (idéntico)
        kb_tarjeta = Tarjeta(); kb_v = QVBoxLayout(kb_tarjeta); kb_v.setSpacing(8); kb_v.setContentsMargins(10, 8, 10, 10)
        encabezado = QHBoxLayout()
        self.toggle_kb = QToolButton(); self.toggle_kb.setText("Teclado matemático")
        self.toggle_kb.setCheckable(True); self.toggle_kb.setChecked(False)
        self.toggle_kb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        encabezado.addWidget(self.toggle_kb); encabezado.addStretch(1)
        kb_v.addLayout(encabezado)

        kb_contenedor = QWidget(); kb_grid = QGridLayout(kb_contenedor); kb_grid.setSpacing(6)
        for col in range(6): kb_grid.setColumnStretch(col, 1)

        def agregar_boton(r, c, texto, insertar=None):
            b = QPushButton(texto); b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            b.setMinimumHeight(34)
            b.clicked.connect(lambda _=False, t=(texto if insertar is None else insertar): self.al_teclar(t))
            kb_grid.addWidget(b, r, c)

        agregar_boton(0, 0, "sin", "sin("); agregar_boton(0, 1, "cos", "cos("); agregar_boton(0, 2, "tan", "tan(")
        agregar_boton(0, 3, "ln", "ln("); agregar_boton(0, 4, "log", "log("); agregar_boton(0, 5, "exp", "exp(")
        agregar_boton(1, 0, "√", "sqrt("); agregar_boton(1, 1, "(", "("); agregar_boton(1, 2, ")", ")")
        agregar_boton(1, 3, "π", "pi"); agregar_boton(1, 4, "e", "e"); agregar_boton(1, 5, "^", "^")
        agregar_boton(2, 0, "7"); agregar_boton(2, 1, "8"); agregar_boton(2, 2, "9"); agregar_boton(2, 3, "", ""); agregar_boton(2, 4, "/", "/"); agregar_boton(2, 5, "=", "=")
        agregar_boton(3, 0, "4"); agregar_boton(3, 1, "5"); agregar_boton(3, 2, "6"); agregar_boton(3, 3, "+", "+"); agregar_boton(3, 4, "-", "-"); agregar_boton(3, 5, "x", "x")
        agregar_boton(4, 0, "1"); agregar_boton(4, 1, "2"); agregar_boton(4, 2, "3"); agregar_boton(4, 3, "0", "0"); agregar_boton(4, 4, ".", "."); agregar_boton(4, 5, "←", "<BACK>")
        agregar_boton(5, 0, "⁰", "⁰"); agregar_boton(5, 1, "¹", "¹"); agregar_boton(5, 2, "²", "²"); agregar_boton(5, 3, "³", "³"); agregar_boton(5, 4, "⁴", "⁴"); agregar_boton(5, 5, "C", "<CLEAR>")
        agregar_boton(6, 0, "⁵", "⁵"); agregar_boton(6, 1, "⁶", "⁶"); agregar_boton(6, 2, "⁷", "⁷"); agregar_boton(6, 3, "⁸", "⁸"); agregar_boton(6, 4, "⁹", "⁹"); agregar_boton(6, 5, "⁻", "⁻")

        kb_v.addWidget(kb_contenedor)
        kb_contenedor.setVisible(False)
        self.toggle_kb.toggled.connect(kb_contenedor.setVisible)
        L.addWidget(kb_tarjeta)

        split.addWidget(izquierdo)

        # Derecho: gráfica, tabla y procedimiento
        derecho = QWidget(); R = QVBoxLayout(derecho); R.setSpacing(10)
        cab = QLabel("Procedimiento y gráfica"); cab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cab.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold)); R.addWidget(cab)

        tabs = QTabWidget()
        tab_plot = QWidget(); tp = QVBoxLayout(tab_plot); tp.setContentsMargins(6, 6, 6, 6)
        self.canvas = LienzoGrafica(); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        tp.addWidget(self.toolbar); tp.addWidget(self.canvas, 1)
        tabs.addTab(tab_plot, "Gráfica")

        tab_table = QWidget(); tt = QVBoxLayout(tab_table); tt.setContentsMargins(6, 6, 6, 6)
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["i", "xi", "xf", "xr", "f(xi)", "f(xf)", "f(xr)", "Error (%)", "subintervalo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tt.addWidget(self.table, 1)
        tabs.addTab(tab_table, "Tabla")

        tab_proc = QWidget(); tp2 = QVBoxLayout(tab_proc); tp2.setContentsMargins(6, 6, 6, 6)
        self.procedimiento_text = QTextEdit()
        self.procedimiento_text.setReadOnly(True)
        self.procedimiento_text.setFont(QFont("Consolas", 11))
        self.procedimiento_text.setPlaceholderText("Aquí aparecerán los pasos que realizó el algoritmo...")
        tp2.addWidget(self.procedimiento_text, 1)
        tabs.addTab(tab_proc, "Procedimiento")

        R.addWidget(tabs, 1)
        split.addWidget(derecho)
        split.setSizes([520, 640])

        from PyQt6.QtGui import QAction
        act_run = QAction(self); act_run.setShortcut("Ctrl+R"); act_run.triggered.connect(self.resolver); self.addAction(act_run)
        act_plot = QAction(self); act_plot.setShortcut("Ctrl+G"); act_plot.triggered.connect(self.graficar); self.addAction(act_plot)
        act_clear = QAction(self); act_clear.setShortcut("Ctrl+L"); act_clear.triggered.connect(self.limpiar); self.addAction(act_clear)
        act_exp = QAction(self); act_exp.setShortcut("Ctrl+S"); act_exp.triggered.connect(self.exportar_excel); self.addAction(act_exp)

    # ---------- utilidades UI ----------
    def etiqueta_negrita(self, t: str) -> QLabel:
        l = QLabel(t); l.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold)); return l

    def etiqueta_suave(self, t: str) -> QLabel:
        l = QLabel(t); l.setStyleSheet("color:#5b6b7a;"); return l

    def crear_kpi(self, titulo: str, valor: str) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(6, 6, 6, 6)
        t = QLabel(titulo); t.setStyleSheet("color:#6b7280; font-size:12px;")
        val = QLabel(valor); val.setObjectName("KPI"); val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t); v.addWidget(val); return w

    def aplicar_estilos(self):
        self.setStyleSheet(
            """
            QWidget { background: #ffffff; color: #0f172a; font-family: 'Segoe UI', Arial; font-size: 11pt; }
            QFrame#Card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; }
            QLineEdit, QDoubleSpinBox, QSpinBox { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 8px 10px; }
            QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus { border-color: #2563eb; }
            QLabel#KPI { font-size: 20px; font-weight: 700; color: #0f172a; }
            QPushButton { background: #2563eb; color: white; border: none; border-radius: 10px; padding: 8px 10px; font-weight: 600; }
            QPushButton:hover { background: #1e40af; }
            QPushButton:disabled { background: #93c5fd; }
            QTableWidget { background: #ffffff; alternate-background-color: #f1f5f9; gridline-color: #e2e8f0; border: 1px solid #e2e8f0; border-radius: 12px; }
            QHeaderView::section { background: #e2e8f0; padding: 8px; border: none; border-right: 1px solid #cbd5e1; font-weight:600; }
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 10px; }
            QTabBar::tab { padding: 8px 14px; }
            """
        )

    def preparar_spin(self, sp: QDoubleSpinBox, mn: float, mx: float, val: float):
        sp.setRange(mn, mx); sp.setDecimals(8); sp.setSingleStep(0.1); sp.setValue(val)
        sp.setKeyboardTracking(False); sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    # teclado helpers
    def _editor_objetivo(self) -> QLineEdit:
        from PyQt6.QtWidgets import QApplication
        w = QApplication.focusWidget()
        return w if isinstance(w, QLineEdit) else self.le_f

    def al_teclar(self, t: str):
        edit = self._editor_objetivo()
        if t == "<BACK>":
            pos = edit.cursorPosition()
            if pos > 0:
                txt = edit.text(); edit.setText(txt[:pos-1] + txt[pos:])
                edit.setCursorPosition(pos-1)
            return
        if t == "<CLEAR>":
            edit.clear(); return
        edit.insert(t); edit.setFocus()

    # ---------- construir función segura ----------
    def construir_funcion(self) -> Optional[Callable[[float], float]]:
        raw = self.le_f.text().strip()
        if not raw:
            QMessageBox.warning(self, "Falta la función", "Por favor, escribe la función f(x) a analizar.")
            return None

        ok, msg = comprobar_parentesis_y_comillas(raw)
        if not ok:
            QMessageBox.warning(self, "Expresión inválida", "Problema de sintaxis: {}".format(msg))
            return None

        try:
            norm = normalizar_expresion_usuario(raw)
        except Exception as e:
            QMessageBox.critical(self, "Error al normalizar", "No pude normalizar la función.\nDetalles: {}".format(e))
            return None

        try:
            expr = parse_expr(
                norm,
                transformations=(standard_transformations + (implicit_multiplication_application,)),
                local_dict={
                    "x": X, "pi": pi, "e": E, "abs": abs,
                    "asin": asin, "acos": acos, "atan": atan,
                    "sinh": sinh, "cosh": cosh, "tanh": tanh,
                    "exp": exp, "sqrt": sqrt, "log": log, "sin": sin, "cos": cos, "tan": tan
                }
            )
        except Exception as e:
            hint = ("Revisa la sintaxis. Usa: sin(x), cos(x), exp(-x) en lugar de 'e-x', "
                    "y usa sqrt(x) o el botón '√' del teclado.")
            QMessageBox.critical(self, "Error al interpretar", "No pude interpretar la función.\n\nDetalle: {}\n\nSugerencia: {}".format(e, hint))
            return None

        try:
            f = lambdify(X, expr, modules=["numpy"])
        except Exception:
            def f(x):
                try:
                    return float(expr.evalf(subs={X: x}))
                except Exception:
                    return float('nan')

        self._last_norm = normalizar_expresion_usuario(raw)

        def envuelta(x: float) -> float:
            try:
                y = f(x)
            except Exception:
                y = np.nan
            try:
                return float(y)
            except Exception:
                return float('nan')

        return envuelta

    # ------------- comprobación de dominio ----------------
    def comprobar_dominio(self, f: Callable[[float], float], a: float, b: float, muestras: int = 200) -> Tuple[bool, Optional[float], Optional[str]]:
        xs = np.linspace(a, b, muestras)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for x in xs:
                try:
                    y = f(x)
                    if not np.isfinite(y):
                        return False, float(x), "valor no finito (Inf o NaN)"
                except Exception:
                    return False, float(x), "excepción al evaluar (posible dominio)"
        return True, None, None

    # ---------------- algoritmo Falsa Posición (ahora con parada por f(xr)) ----------------
    def falsa_posicion(
        self,
        f: Callable[[float], float],
        xi: float,
        xf: float,
        error_rel_decimal: float = 0.01,
        max_iter: int = 50,
        tol_f: float = 1e-12
    ) -> ResultadoFalsa:
        tabla: List[FilaFalsa] = []
        pasos: List[str] = []
        pasos.append("Iniciando falsa posición en [{}, {}] con error permitido {}% y máximo {} iteraciones.".format(xi, xf, error_rel_decimal*100.0, max_iter))
        try:
            fxi = float(f(xi)); fxf = float(f(xf))
        except Exception:
            pasos.append("Error: no se pudo evaluar f en xi o xf (posible dominio inválido).")
            return ResultadoFalsa(None, 0, None, [], "Error al evaluar f(xi) o f(xf) en los extremos.", pasos)

        pasos.append("f(xi) = f({}) = {}".format(xi, fxi))
        pasos.append("f(xf) = f({}) = {}".format(xf, fxf))

        if not np.isfinite(fxi) or not np.isfinite(fxf):
            pasos.append("Error: f(xi) o f(xf) no es finito en el intervalo.")
            return ResultadoFalsa(None, 0, None, [], "f(xi) o f(xf) no es finito en el intervalo.", pasos)
        if fxi * fxf > 0:
            pasos.append("Error: no hay cambio de signo en [xi, xf]. f(xi)*f(xf) > 0.")
            return ResultadoFalsa(None, 0, None, [], "No hay cambio de signo en [xi,xf]. Elige otro intervalo.", pasos)

        denom = (fxi - fxf)
        if denom == 0:
            pasos.append("Error: denominador nulo inicial (f(xi) == f(xf)).")
            return ResultadoFalsa(None, 0, None, [], "Denominador nulo (f(xi) == f(xf)).", pasos)

        xr = xf - (fxf * (xi - xf)) / denom
        fxr = float(f(xr))
        pasos.append("Cálculo inicial de xr usando la fórmula de la falsa posición:")
        pasos.append("xr = xf - f(xf)*(xi - xf)/(f(xi) - f(xf)) = {}".format(xr))
        pasos.append("f(xr) = f({}) = {}".format(xr, fxr))

        xr_prev = None
        err_pct = None

        if fxi * fxr < 0:
            sub0 = "[xi,xr]"
        elif fxr * fxf < 0:
            sub0 = "[xr,xf]"
        else:
            sub0 = "indeterminado"
        tabla.append(FilaFalsa(1, xi, xf, xr, fxi, fxf, fxr, None, sub0))

        if abs(fxr) < tol_f:
            pasos.append("Convergencia por |f(xr)| < tol_f ({}).".format(tol_f))
            return ResultadoFalsa(xr, 1, 0.0, tabla, "Convergencia por f(xr) < tol_f.", pasos)

        for i in range(2, max_iter + 1):
            pasos.append("\n--- Iteración {} ---".format(i))
            if fxi * fxr < 0:
                pasos.append("f(xi)*f(xr) < 0 -> la raíz está en [xi, xr]. Actualizando xf = xr.")
                xf = xr; fxf = fxr; sub = "[xi,xr]"
            else:
                pasos.append("En caso contrario la raíz está en [xr, xf]. Actualizando xi = xr.")
                xi = xr; fxi = fxr; sub = "[xr,xf]"

            denom = (fxi - fxf)
            pasos.append("Denominador para nueva xr: f(xi) - f(xf) = {}".format(denom))
            if denom == 0:
                pasos.append("Denominador nulo durante iteraciones -> parada.")
                tabla.append(FilaFalsa(i, xi, xf, xr, fxi, fxf, fxr, None, sub))
                return ResultadoFalsa(None, i, None, tabla, "Denominador nulo en iteración (f(xi) == f(xf)).", pasos)

            xr_prev = xr
            xr = xf - (fxf * (xi - xf)) / denom
            fxr = float(f(xr))
            pasos.append("Nuevo xr calculado: xr = {}".format(xr))
            pasos.append("f(xr) = f({}) = {}".format(xr, fxr))

            if abs(fxr) < tol_f:
                err_rel = abs((xr - xr_prev) / xr) if (xr_prev is not None and xr != 0) else None
                err_pct = (err_rel * 100.0) if err_rel is not None else None
                pasos.append("Criterio de paro: |f(xr)| < tol_f ({}).".format(tol_f))
                tabla.append(FilaFalsa(i, xi, xf, xr, fxi, fxf, fxr, None if err_pct is None else err_pct, sub))
                return ResultadoFalsa(xr, i, err_pct, tabla, "Convergencia por f(xr) < tol_f.", pasos)

            if xr_prev is not None and xr != 0:
                err_rel = abs((xr - xr_prev) / xr)
                err_pct = err_rel * 100.0
                pasos.append("Error relativo (decimal) = |xr - xr_prev|/|xr| = {}".format(err_rel))
                pasos.append("Error relativo (%) = {}".format(err_pct))
            elif xr_prev is not None:
                err_rel = abs(xr - xr_prev)
                err_pct = err_rel * 100.0
                pasos.append("xr actual es 0 -> usamos error absoluto.")
                pasos.append("Error absoluto = {} (mostrado como % multiplicado por 100)".format(err_rel))

            tabla.append(FilaFalsa(i, xi, xf, xr, fxi, fxf, fxr, None if err_pct is None else err_pct, sub))

            if err_pct is not None and (err_rel < error_rel_decimal):
                pasos.append("Criterio de paro satisfecho: error_rel ({}) < error_rel_decimal ({}).".format(err_rel, error_rel_decimal))
                return ResultadoFalsa(xr, i, err_pct, tabla, "Convergencia por error relativo.", pasos)
            if abs(fxr) < 1e-14:
                pasos.append("Criterio de paro: f(xr) ≈ 0.")
                return ResultadoFalsa(xr, i, err_pct, tabla, "Convergencia por f(xr) ≈ 0.", pasos)

        pasos.append("Se alcanzó el máximo de iteraciones sin satisfacer el criterio de error relativo o f(xr).")
        return ResultadoFalsa(xr, max_iter, (err_pct if err_pct is not None else None), tabla, "Se alcanzó el máximo de iteraciones.", pasos)

    # ---------- acciones UI ----------
    def resolver(self):
        f = self.construir_funcion()
        if f is None:
            return
        try:
            xi = float(numero_desde_texto(self.le_xi.text()))
            xf = float(numero_desde_texto(self.le_xf.text()))
        except Exception as e:
            QMessageBox.warning(self, "Intervalo inválido", "No pude interpretar xi/xf: {}".format(e))
            return
        if xi >= xf:
            QMessageBox.warning(self, "Intervalo inválido", "Se requiere que xi < xf")
            return

        try:
            err_pct_user = float(self.le_err_pct.text())
            if err_pct_user < 0:
                raise ValueError("No negativo")
            error_rel_decimal = err_pct_user / 100.0
        except Exception as e:
            QMessageBox.warning(self, "Error inválido", "No pude interpretar el porcentaje de error: {}".format(e))
            return

        itmax = int(self.sp_iter.value())

        sing_text = self.le_singulares.text().strip() if hasattr(self, "le_singulares") else ""
        if sing_text:
            nums = re.findall(r"[+-]?\d+(?:\.\d+)?", sing_text)
            puntos = []
            for n in nums:
                try:
                    puntos.append(float(n))
                except Exception:
                    pass
            hits = [p for p in puntos if xi <= p <= xf]
            if hits:
                QMessageBox.warning(self, "Punto singular en intervalo", "Has declarado puntos singulares {} y uno(s) cae(n) dentro de [{}, {}].".format(puntos, xi, xf))
                return

        ok, bad_x, reason = self.comprobar_dominio(f, xi, xf)
        if not ok:
            QMessageBox.warning(self, "Problema de dominio", "La función parece no estar definida o da Inf/NaN en x = {} dentro de [{}, {}].\nMotivo: {}\nPor favor ajusta el intervalo o la función.".format(bad_x, xi, xf, reason))
            return

        try:
            nr = estimar_raices(f, xi, xf)
            self._set_kpi(self.k_roots, str(nr))
        except Exception:
            self._set_kpi(self.k_roots, "—")

        res = self.falsa_posicion(f, xi, xf, error_rel_decimal=error_rel_decimal, max_iter=itmax, tol_f=1e-12)

        # Volcar tabla
        self.table.setRowCount(0)
        for r in res.tabla:
            row = self.table.rowCount(); self.table.insertRow(row)
            err_txt = "{:.6g}".format(r.error_pct) if (r.error_pct is not None) else ""
            values = [r.i, r.xi, r.xf, r.xr, r.fxi, r.fxf, r.fxr, err_txt, r.subintervalo]
            for c, val in enumerate(values):
                if isinstance(val, (int, float, np.floating)) and np.isfinite(val):
                    txt = "{:.10g}".format(val)
                elif val is None or (isinstance(val, float) and not np.isfinite(val)):
                    txt = ""
                else:
                    txt = str(val)
                item = QTableWidgetItem(txt); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, c, item)

        pasos_text = "\n\n".join(res.pasos) if res.pasos else "(Sin pasos disponibles)"
        self.procedimiento_text.setPlainText(pasos_text)

        self._set_kpi(self.k_root, "{:.10f}".format(res.raiz) if res.raiz is not None else "—", flash=True)
        self._set_kpi(self.k_err, "—" if res.ultimo_error_pct is None else "{:.6g}%".format(res.ultimo_error_pct), flash=True)

        # Actualizar gráfica: preferimos marcar sobre la gráfica existente si corresponde
        try:
            a = float(numero_desde_texto(self.le_xi.text()))
            b = float(numero_desde_texto(self.le_xf.text()))
        except Exception:
            a, b = None, None

        raw_norm = None
        try:
            raw_norm = normalizar_expresion_usuario(self.le_f.text().strip())
        except Exception:
            raw_norm = None

        if a is not None and b is not None and self._last_norm == raw_norm and self._last_range == (a, b):
            try:
                self.canvas.marcar_raiz(f, res.raiz)
            except Exception:
                pass
        else:
            try:
                if a is None or b is None:
                    a = float(numero_desde_texto(self.le_xi.text() or "-5"))
                    b = float(numero_desde_texto(self.le_xf.text() or "5"))
                self.canvas.graficar_f(f, a, b, raiz=res.raiz)
                self._fade_widget(self.canvas, 160)
                self._last_range = (a, b)
                self._last_norm = raw_norm
            except Exception:
                pass

        realizado = res.iteraciones
        pedidas = itmax
        msg = res.mensaje + ("\nRaíz ≈ {:.10f}".format(res.raiz) if res.raiz is not None else "")
        msg += "\nIteraciones realizadas: {} / {} máximas".format(realizado, pedidas)
        QMessageBox.information(self, "Resultado", msg)

    def graficar(self):
        f = self.construir_funcion()
        if f is None:
            return

        a_text = self.le_xi.text().strip()
        b_text = self.le_xf.text().strip()
        use_user_interval = bool(a_text and b_text)

        if use_user_interval:
            try:
                a = float(numero_desde_texto(a_text))
                b = float(numero_desde_texto(b_text))
            except Exception:
                QMessageBox.warning(self, "Intervalo inválido", "No pude interpretar xi/xf"); return
            if a >= b:
                QMessageBox.warning(self, "Intervalo inválido", "Se requiere que xi < xf"); return
        else:
            a, b = -10.0, 10.0
            xs_test = np.linspace(a, b, 500)
            fin_count = 0
            for x in xs_test:
                try:
                    y = f(x)
                    if np.isfinite(y):
                        fin_count += 1
                except Exception:
                    pass
            if fin_count < 50:
                a, b = -5.0, 5.0

        ok, bad_x, reason = self.comprobar_dominio(f, a, b, muestras=400)
        if not ok:
            QMessageBox.warning(self, "Problema de dominio", "La función no es válida en x = {} dentro de [{}, {}].\nMotivo: {}".format(bad_x, a, b, reason))
            return

        try:
            self.canvas.graficar_f(f, a, b)
            self._fade_widget(self.canvas, 160)
            self._last_range = (a, b)
            try:
                self._last_norm = normalizar_expresion_usuario(self.le_f.text().strip())
            except Exception:
                self._last_norm = None
        except Exception as e:
            QMessageBox.warning(self, "Error al graficar", "No pude graficar la función:\n{}".format(e))
            return

        try:
            intervals = detectar_intervalos_cambio_signo(f, a, b, muestras=2000)
        except Exception:
            intervals = []

        try:
            self._set_kpi(self.k_roots, str(len(intervals)))
        except Exception:
            pass

        if intervals:
            prefer_pos = bool(self.chk_prefer_pos.isChecked()) if hasattr(self, "chk_prefer_pos") else False
            if prefer_pos:
                def score_interval(iv):
                    mid = 0.5*(iv[0]+iv[1])
                    return (0 if mid > 0 else 1, abs(mid))
                intervals = sorted(intervals, key=score_interval)

            first = intervals[0]
            if not use_user_interval:
                self.le_xi.setText("{:.8g}".format(first[0]))
                self.le_xf.setText("{:.8g}".format(first[1]))
            display_intervals = intervals[:8]
            s = ", ".join(["[{:.6g}, {:.6g}]".format(li, ri) for li, ri in display_intervals])
            more = "" if len(intervals) <= 8 else " y {} más...".format(len(intervals)-8)
            QMessageBox.information(self, "Intervalos detectados", "Se detectaron {} intervalo(s) con cambio de signo:\n{}{}\n\nHe rellenado automáticamente xi/xf con el primer intervalo.".format(len(intervals), s, more))
        else:
            QMessageBox.information(self, "Sin cambios de signo", "No se detectaron intervalos con cambio de signo en el rango graficado.\nPrueba ampliar el intervalo o revisa la función.")

    def limpiar(self):
        self.le_f.clear(); self.lbl_prev.setText("<i>Escribe una función...</i>")
        self.le_xi.setText(""); self.le_xf.setText(""); self.le_err_pct.setText("1"); self.sp_iter.setValue(50)
        if hasattr(self, "le_singulares"): self.le_singulares.setText("")
        self.table.setRowCount(0); self._set_kpi(self.k_root, "--"); self._set_kpi(self.k_err, "--"); self._set_kpi(self.k_roots, "--")
        self.procedimiento_text.clear()
        self.canvas.ax.clear(); self.canvas.draw_idle()
        self._last_norm = None; self._last_range = None

    def exportar_excel(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Exportar Excel", "No hay datos para exportar."); return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "falsa_posicion.xlsx", "Excel (*.xlsx)")
        if not path: return
        try:
            encabezados = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            filas = []
            for r in range(self.table.rowCount()):
                fila = []
                for c in range(self.table.columnCount()):
                    item = self.table.item(r, c)
                    fila.append(item.text() if item else "")
                filas.append(fila)
            df = pandas.DataFrame(filas, columns=encabezados)
            df.to_excel(path, index=False, engine="openpyxl")
            QMessageBox.information(self, "Exportar Excel", "Archivo guardado en:\n{}".format(path))
        except Exception as e:
            QMessageBox.critical(self, "Exportar Excel", "Error al guardar:\n{}".format(e))

    def actualizar_vista_previa(self, texto: str):
        if not texto.strip():
            self.lbl_prev.setText("<i>Escribe una función...</i>"); return
        try:
            self.lbl_prev.setText(vista_previa_superindice(texto))
        except Exception:
            self.lbl_prev.setText(texto)

    # animaciones & util
    def _fade_widget(self, w: QWidget, dur_ms: int = 220):
        eff = QGraphicsOpacityEffect(w); w.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", w); anim.setDuration(dur_ms)
        anim.setStartValue(0.0); anim.setEndValue(1.0); anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim_refs.append(anim)

    def _flash(self, w: QWidget, dur_ms: int = 220):
        eff = QGraphicsOpacityEffect(w); w.setGraphicsEffect(eff)
        a1 = QPropertyAnimation(eff, b"opacity", w); a1.setDuration(int(dur_ms * 0.5))
        a1.setStartValue(0.35); a1.setEndValue(1.0); a1.setEasingCurve(QEasingCurve.Type.OutCubic)
        a2 = QPropertyAnimation(eff, b"opacity", w); a2.setDuration(int(dur_ms * 0.5))
        a2.setStartValue(1.0); a2.setEndValue(1.0)
        group = QParallelAnimationGroup(w); group.addAnimation(a1); group.addAnimation(a2)
        group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim_refs.append(group)

    def _set_kpi(self, contenedor: QWidget, valor: str, flash: bool = False):
        lbl = contenedor.findChild(QLabel, "KPI")
        if lbl:
            lbl.setText(valor)
            if flash: self._flash(lbl, 220)

    def _animar_entrada(self):
        try:
            self.setWindowFlag(Qt.Window, True)
        except Exception:
            pass
        def _run_anim():
            try:
                start_geo = self.geometry()
                if start_geo.width() < 10 or start_geo.height() < 10:
                    return
                eff = QGraphicsOpacityEffect(self)
                self.setGraphicsEffect(eff)
                anim_op = QPropertyAnimation(eff, b"opacity", self)
                anim_op.setDuration(240)
                anim_op.setStartValue(0.0)
                anim_op.setEndValue(1.0)
                anim_op.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim_geo = QPropertyAnimation(self, b"geometry", self)
                anim_geo.setDuration(240)
                anim_geo.setEasingCurve(QEasingCurve.Type.OutCubic)
                sx, sy, sw, sh = start_geo.x(), start_geo.y(), start_geo.width(), start_geo.height()
                anim_geo.setStartValue(QRect(sx, sy - 12, sw, sh))
                anim_geo.setEndValue(QRect(sx, sy, sw, sh))
                group = QParallelAnimationGroup(self)
                group.addAnimation(anim_op)
                group.addAnimation(anim_geo)
                group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
                self._anim_refs.append(group)
            except Exception:
                try:
                    self.setGraphicsEffect(None)
                except Exception:
                    pass
        QTimer.singleShot(120, _run_anim)


# Estimador de cambios de signo
def estimar_raices(f: Callable[[float], float], a: float, b: float, muestras: int = 400, eps: float = 1e-8) -> int:
    xs = np.linspace(a, b, muestras)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ys = np.array([f(x) for x in xs], dtype=float)
    signos = np.sign(ys * (np.abs(ys) > eps))
    return int(np.count_nonzero(np.diff(signos)))


# ---------- lanzamiento ----------
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    w = VentanaFalsaPosicion()
    w.show()
    sys.exit(app.exec())