# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import math
import re
import warnings
from dataclasses import dataclass
from typing import Callable, Optional, List, Tuple

import numpy as np
import pandas
import openpyxl
import sympy as sp
from sympy import (
    symbols, lambdify, exp, sin, cos, tan, sqrt, log,
    asin, acos, atan, sinh, cosh, tanh, pi, E, sign, Abs, Rational
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)

from PyQt6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup, QRect, QTimer
from PyQt6.QtGui import QFont, QAction
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

# ----------------- Helpers y validaciones (idénticos a tu otro archivo) -----------------

X = symbols("x")
SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_SIGNS = "⁻⁺"
SUP_MAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")


def reemplazar_superindices_por_potencia(expr: str) -> str:
    patt = r"(?P<base>(?:\d+|\w+|[\)\]])+)(?P<sup>[{}{}]+)".format(SUP_DIGITS, SUP_SIGNS)
    def repl(m):
        base = m.group("base")
        sup = m.group("sup").translate(SUP_MAP)
        return f"{base}**({sup})"
    return re.sub(patt, repl, expr)


def _preprocesos_adicionales(s: str) -> str:
    if not s:
        return s

    s = re.sub(r"√\s*\(([^)]+)\)", r"sqrt(\1)", s)
    s = re.sub(r"√\s*([A-Za-z0-9_\.]+)", r"sqrt(\1)", s)

    funcs = r"(?:sin|cos|tan|log|ln|sqrt|exp|asin|acos|atan|sinh|cosh|tanh|cbrt)"
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

    s = re.sub(r"ra[ií]z\s*c[úu]bica\s+de\s*\(", "cbrt(", s, flags=re.IGNORECASE)
    s = re.sub(r"ra[ií]z\s*c[úu]bica\s+de\s+([A-Za-z0-9_\.\(\)]+)", r"cbrt(\1)", s, flags=re.IGNORECASE)
    s = re.sub(r"\bcbrt\s*\(", "cbrt(", s, flags=re.IGNORECASE)

    if "=" in s:
        p = s.split("=")
        if len(p) != 2:
            raise ValueError("Sólo una igualdad con '='.")
        s = f"({p[0].strip()}) - ({p[1].strip()})"

    s = re.sub(r"\bX\b", "x", s)
    s = s.replace("^", "**")
    s = re.sub(r"\bln\(", "log(", s, flags=re.IGNORECASE)
    s = re.sub(r"\bsen\(", "sin(", s, flags=re.IGNORECASE)
    s = s.replace("π", "pi")

    s = re.sub(r"(?P<a>[A-Za-z0-9_\)\.]+)\s*\*\*\s*\(\s*1\s*/\s*3\s*\)", r"sign(\g<a>)*abs(\g<a>)**(1/3)", s)
    s = re.sub(r"(?P<a>[A-Za-z0-9_\)\.]+)\s*\^\s*\(\s*1\s*/\s*3\s*\)", r"sign(\g<a>)*abs(\g<a>)**(1/3)", s)

    s = re.sub(r"cbrt\s*\(\s*([^\)]+)\s*\)", r"sign(\1)*abs(\1)**(1/3)", s, flags=re.IGNORECASE)

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
    def cbrt_sym(v):
        return sign(v) * Abs(v) ** Rational(1, 3)
    expr = parse_expr(
        s,
        transformations=(standard_transformations + (implicit_multiplication_application,)),
        local_dict={
            "x": X, "pi": pi, "e": E, "abs": Abs, "sign": sign, "cbrt": cbrt_sym,
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
    s = expr[:]
    s = re.sub(r"cbrt\s*\(\s*([^\)]+)\s*\)", r"∛(\1)", s, flags=re.IGNORECASE)
    s = re.sub(r"sqrt\s*\(\s*([^\)]+)\s*\)", r"√(\1)", s, flags=re.IGNORECASE)
    s = s.replace("√(", "√(")
    s = re.sub(r"\^\(([^)]+)\)", lambda m: "<sup>" + m.group(1) + "</sup>", s)
    s = re.sub(r"\^([\-+]?\d+(?:\.\d+)?)", lambda m: "<sup>" + m.group(1) + "</sup>", s)
    s = re.sub(r"\^([a-zA-Z])", lambda m: "<sup>" + m.group(1) + "</sup>", s)
    s = s.replace("*", "·")
    return "<span style='font-size:18px;'>f(x) = {}</span>".format(s)


# ----------------- Estructuras -----------------

@dataclass
class FilaSecante:
    i: int
    x_prev: float
    x_curr: float
    fx_curr: float
    error_pct: Optional[float]


@dataclass
class ResultadoSecante:
    raiz: Optional[float]
    iteraciones: int
    ultimo_error_pct: Optional[float]
    tabla: List[FilaSecante]
    mensaje: str
    pasos: List[str]


# ----------------- Gráfica (idéntica) -----------------

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


# ----------------- Interfaz y lógica Secante -----------------

class Tarjeta(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")


class VentanaSecante(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowFlag(Qt.Window, True)
        except Exception:
            pass
        self.setWindowTitle("Método de la Secante")
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

        titulo = QLabel("Método de la Secante")
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

        big_font = QFont("Segoe UI", 12, QFont.Weight.DemiBold)
        self.le_x0 = QLineEdit(""); self.le_x0.setFont(big_font); self.le_x0.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.le_x1 = QLineEdit(""); self.le_x1.setFont(big_font); self.le_x1.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.le_err_pct = QLineEdit("0.01"); self.le_err_pct.setFont(big_font); self.le_err_pct.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.sp_iter = QSpinBox(); self.sp_iter.setRange(1, 5000); self.sp_iter.setValue(50)

        grid.addWidget(self.etiqueta_negrita("Escribe la función"), r, 0, 1, 2); r += 1
        grid.addWidget(self.le_f, r, 0, 1, 2); r += 1
        grid.addWidget(self.etiqueta_suave("Vista previa"), r, 0, 1, 2); r += 1
        grid.addWidget(self.lbl_prev, r, 0, 1, 2); r += 1

        grid.addWidget(self.etiqueta_negrita("x0 (valor inicial)"), r, 0)
        grid.addWidget(self.etiqueta_negrita("x1 (valor inicial)"), r, 1); r += 1
        grid.addWidget(self.le_x0, r, 0); grid.addWidget(self.le_x1, r, 1); r += 1

        grid.addWidget(self.etiqueta_negrita("Error permitido (%)"), r, 0)
        grid.addWidget(self.etiqueta_negrita("Iteraciones máx."), r, 1); r += 1
        grid.addWidget(self.le_err_pct, r, 0); grid.addWidget(self.sp_iter, r, 1); r += 1

        self.chk_auto_guess = QCheckBox("Auto-detectar x0,x1 por primer intervalo con cambio de signo si están vacíos")
        self.chk_auto_guess.setChecked(True)
        grid.addWidget(self.chk_auto_guess, r, 0, 1, 2); r += 1

        L.addWidget(tarjeta_entrada)

        # KPIs
        kpi = Tarjeta(); K = QHBoxLayout(kpi)
        self.k_iter = self.crear_kpi("Iteraciones realizadas", "--")
        self.k_err = self.crear_kpi("Error relativo (%)", "--")
        self.k_root = self.crear_kpi("Raíz aproximada", "--")
        for w in (self.k_iter, self.k_err, self.k_root):
            lbl_val = w.findChild(QLabel, "KPI")
            if lbl_val:
                lbl_val.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
                lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        K.addWidget(self.k_iter, 1); K.addWidget(self.k_err, 1); K.addWidget(self.k_root, 1)
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

        # Teclado (misma implementación reducida)
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
        agregar_boton(2, 0, "7"); agregar_boton(2, 1, "8"); agregar_boton(2, 2, "9"); agregar_boton(2, 3, "*", "*"); agregar_boton(2, 4, "/", "/"); agregar_boton(2, 5, "=")
        agregar_boton(3, 0, "4"); agregar_boton(3, 1, "5"); agregar_boton(3, 2, "6"); agregar_boton(3, 3, "+", "+"); agregar_boton(3, 4, "-", "-"); agregar_boton(3, 5, "x", "x")
        agregar_boton(4, 0, "1"); agregar_boton(4, 1, "2"); agregar_boton(4, 2, "3"); agregar_boton(4, 3, "0", "0"); agregar_boton(4, 4, ".", "."); agregar_boton(4, 5, "←", "<BACK>")
        agregar_boton(5, 0, "⁰", "⁰"); agregar_boton(5, 1, "¹", "¹"); agregar_boton(5, 2, "²", "²"); agregar_boton(5, 3, "³", "³"); agregar_boton(5, 4, "⁴", "⁴"); agregar_boton(5, 5, "C", "<CLEAR>")
        agregar_boton(6, 0, "cbrt", "cbrt("); agregar_boton(6, 1, "⁵", "⁵"); agregar_boton(6, 2, "⁶", "⁶"); agregar_boton(6, 3, "⁷", "⁷"); agregar_boton(6, 4, "⁸", "⁸"); agregar_boton(6, 5, "⁹", "⁹")

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
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["i", "x_prev", "x_curr", "f(x_curr)", "Error (%)"])
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

        # Accesos rápidos
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

    # ---------- construir función ----------
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
                    "x": X, "pi": pi, "e": E, "abs": Abs, "sign": sign,
                    "asin": asin, "acos": acos, "atan": atan,
                    "sinh": sinh, "cosh": cosh, "tanh": tan,
                    "exp": exp, "sqrt": sqrt, "log": log, "sin": sin, "cos": cos, "tan": tan
                }
            )
        except Exception as e:
            hint = ("Revisa la sintaxis. Usa: sin(x), cos(x), exp(-x) en lugar de 'e-x', "
                    "y usa sqrt(x) o el botón '√' del teclado.")
            QMessageBox.critical(self, "Error al interpretar", "No pude interpretar la función.\n\nDetalle: {}\n\nSugerencia: {}".format(e, hint))
            return None

        try:
            modules = [
                {
                    "sign": np.sign,
                    "cbrt": lambda t: np.sign(t) * (np.abs(t) ** (1.0/3.0)),
                    "abs": np.abs
                },
                "numpy"
            ]
            f = lambdify(X, expr, modules=modules)
        except Exception:
            def f(x):
                try:
                    return float(expr.evalf(subs={X: x}))
                except Exception:
                    return float('nan')

        self._last_norm = normalizar_expresion_usuario(raw)

        def env_f(x: float) -> float:
            try:
                y = f(x)
            except Exception:
                y = np.nan
            try:
                return float(y)
            except Exception:
                return float('nan')

        return env_f

    # ---------------- algoritmo de la secante ----------------
    def secante(
        self,
        f: Callable[[float], float],
        x0: float,
        x1: float,
        error_rel_decimal: float = 1e-4,
        max_iter: int = 50,
        tol_f: float = 1e-12
    ) -> ResultadoSecante:
        tabla: List[FilaSecante] = []
        pasos: List[str] = []
        pasos.append(f"Iniciando método de la secante con x0 = {x0}, x1 = {x1}, tol_rel = {error_rel_decimal}, max_iter = {max_iter}")
        eps = 1e-16

        fx0 = None
        fx1 = None

        for i in range(1, max_iter + 1):
            try:
                fx0 = float(f(x0))
            except Exception:
                pasos.append(f"Iter {i}: no se pudo evaluar f({x0}) -> parada por dominio.")
                return ResultadoSecante(None, i-1, None, tabla, "Error al evaluar f en iteraciones.", pasos)
            try:
                fx1 = float(f(x1))
            except Exception:
                pasos.append(f"Iter {i}: no se pudo evaluar f({x1}) -> parada por dominio.")
                return ResultadoSecante(None, i-1, None, tabla, "Error al evaluar f en iteraciones.", pasos)

            pasos.append(f"Iter {i}: x_prev = {x0}, x_curr = {x1}, f(x_prev) = {fx0}, f(x_curr) = {fx1}")

            if not np.isfinite(fx0) or not np.isfinite(fx1):
                pasos.append("Valor no finito encontrado -> paro.")
                return ResultadoSecante(None, i-1, None, tabla, "Valor no finito durante la iteración.", pasos)

            denom = fx1 - fx0
            if abs(denom) < eps:
                pasos.append("Denominador cercano a cero (f(x1)-f(x0) ≈ 0) -> parada para evitar división por cero.")
                tabla.append(FilaSecante(i, x0, x1, fx1, None))
                return ResultadoSecante(None, i, None, tabla, f"División por cero numérica en iteración {i}.", pasos)

            x2 = x1 - fx1 * (x1 - x0) / denom
            if not np.isfinite(x2):
                pasos.append("x2 no finito -> paro.")
                return ResultadoSecante(None, i, None, tabla, "x2 no finito.", pasos)

            # error relativo
            if x2 != 0:
                err_rel = abs((x2 - x1) / x2)
            else:
                err_rel = abs(x2 - x1)
            err_pct = err_rel * 100.0

            tabla.append(FilaSecante(i, x0, x1, fx1, err_pct))
            pasos.append(f"Iter {i}: x_new = {x2}, error_rel = {err_rel}")

            # criterios de paro
            if abs(fx1) < tol_f:
                pasos.append("Convergencia por |f(x)| < tol_f.")
                return ResultadoSecante(x2, i, err_pct, tabla, "Convergencia por f(x) < tol_f.", pasos)
            if err_rel < error_rel_decimal:
                pasos.append("Convergencia por error relativo < tol.")
                return ResultadoSecante(x2, i, err_pct, tabla, "Convergencia por error relativo.", pasos)

            # desplazar
            x0, x1 = x1, x2

        pasos.append("Máximo de iteraciones alcanzado sin convergencia.")
        return ResultadoSecante(x1, max_iter, err_pct if 'err_pct' in locals() else None, tabla, "Máximo de iteraciones alcanzado.", pasos)

    # ---------------- acciones UI ----------------
    def resolver(self):
        f = self.construir_funcion()
        if f is None:
            return

        x0_text = self.le_x0.text().strip()
        x1_text = self.le_x1.text().strip()
        use_user_x0 = bool(x0_text)
        use_user_x1 = bool(x1_text)

        if use_user_x0 and use_user_x1:
            try:
                x0 = float(numero_desde_texto(x0_text))
                x1 = float(numero_desde_texto(x1_text))
            except Exception as e:
                QMessageBox.warning(self, "Valores iniciales inválidos", "No pude interpretar x0/x1: {}".format(e))
                return
        else:
            # intentar auto-detectar intervalo con cambio de signo
            a_search, b_search = -10.0, 10.0
            try:
                intervals = detectar_intervalos_cambio_signo(f, a_search, b_search, muestras=2000)
            except Exception:
                intervals = []
            if intervals and self.chk_auto_guess.isChecked():
                a, b = intervals[0]
                x0 = float(a)
                x1 = float(b)
            else:
                # si el usuario dio sólo x0 o sólo x1, setea razonables
                try:
                    if use_user_x0 and not use_user_x1:
                        x0 = float(numero_desde_texto(x0_text))
                        x1 = x0 + 1.0
                    elif use_user_x1 and not use_user_x0:
                        x1 = float(numero_desde_texto(x1_text))
                        x0 = x1 - 1.0
                    else:
                        x0 = 0.0; x1 = 1.0
                except Exception as e:
                    QMessageBox.warning(self, "Valores iniciales inválidos", "No pude interpretar x0/x1: {}".format(e))
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

        ok, bad_x, reason = comprobar_dominio(f, min(x0, x1) - 1.0, max(x0, x1) + 1.0, muestras=200)
        if not ok:
            QMessageBox.warning(self, "Posible problema de dominio", "La función parece no estar definida en torno a x0/x1 = {} / {}.\nMotivo: {}\nContinuando de todas formas.".format(x0, x1, reason))

        res = self.secante(f, x0, x1, error_rel_decimal=error_rel_decimal, max_iter=itmax, tol_f=1e-12)

        # Volcar tabla
        self.table.setRowCount(0)
        for r in res.tabla:
            row = self.table.rowCount(); self.table.insertRow(row)
            err_txt = "{:.6g}".format(r.error_pct) if (r.error_pct is not None) else ""
            values = [r.i, r.x_prev, r.x_curr, r.fx_curr, err_txt]
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
        self._set_kpi(self.k_iter, str(res.iteraciones), flash=True)

        # Actualizar gráfica
        try:
            if res.raiz is not None and np.isfinite(res.raiz):
                a = res.raiz - 5.0
                b = res.raiz + 5.0
                self.canvas.graficar_f(f, a, b, raiz=res.raiz)
                self._last_range = (a, b)
            else:
                self.canvas.graficar_f(f, -10.0, 10.0, raiz=None)
            self._fade_widget(self.canvas, 160)
            try:
                self._last_norm = normalizar_expresion_usuario(self.le_f.text().strip())
            except Exception:
                self._last_norm = None
        except Exception:
            pass

        msg = res.mensaje + ("\nRaíz ≈ {:.10f}".format(res.raiz) if res.raiz is not None else "")
        msg += "\nIteraciones realizadas: {} / {} máximas".format(res.iteraciones, itmax)
        QMessageBox.information(self, "Resultado", msg)

    def graficar(self):
        f = self.construir_funcion()
        if f is None:
            return

        a, b = -10.0, 10.0
        ok, bad_x, reason = comprobar_dominio(f, a, b, muestras=400)
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

        if intervals:
            s = ", ".join(["[{:.6g}, {:.6g}]".format(li, ri) for li, ri in intervals[:8]])
            QMessageBox.information(self, "Intervalos detectados", "Se detectaron {} intervalo(s) con cambio de signo:\n{}\n\n(Úsalos para obtener buenos x0,x1).".format(len(intervals), s))
        else:
            QMessageBox.information(self, "Sin cambios de signo", "No se detectaron intervalos con cambio de signo en el rango graficado.")

    def limpiar(self):
        self.le_f.clear(); self.lbl_prev.setText("<i>Escribe una función...</i>")
        self.le_x0.setText(""); self.le_x1.setText(""); self.le_err_pct.setText("0.01"); self.sp_iter.setValue(50)
        self.table.setRowCount(0); self._set_kpi(self.k_root, "--"); self._set_kpi(self.k_err, "--"); self._set_kpi(self.k_iter, "--")
        self.procedimiento_text.clear()
        self.canvas.ax.clear(); self.canvas.draw_idle()
        self._last_norm = None; self._last_range = None

    def exportar_excel(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Exportar Excel", "No hay datos para exportar."); return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "secante.xlsx", "Excel (*.xlsx)")
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

    # animaciones & util (idénticos a tu otro archivo)
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


# ----------------- Detección de intervalos por muestreo (idéntica) -----------------
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


# ----------------- Comprobación de dominio (idéntica) -----------------
def comprobar_dominio(f: Callable[[float], float], a: float, b: float, muestras: int = 200) -> Tuple[bool, Optional[float], Optional[str]]:
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


# ---------- lanzamiento ----------
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = VentanaSecante()
    w.show()
    sys.exit(app.exec())