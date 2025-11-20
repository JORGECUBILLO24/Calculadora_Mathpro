# -*- coding: utf-8 -*-
from __future__ import annotations
import math
import re
import warnings
from dataclasses import dataclass
from typing import Callable, Optional, List

import numpy as np
import pandas
import openpyxl
from sympy import symbols, lambdify, exp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)

from PyQt6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup, QRect
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDoubleSpinBox, QSpinBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QSplitter, QSizePolicy,
    QGridLayout, QTabWidget, QFileDialog, QToolButton
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# ----------------- Ayudas de parseo -----------------

X = symbols("x")
SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_SIGNS  = "⁻⁺"
SUP_MAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")


def reemplazar_superindices_por_potencia(expr: str) -> str:
    """Convierte 10⁻⁴ -> 10**(-4), x² -> x**(2)"""
    patt = r"(?P<base>(?:\d+|\w+|[\)\]])+)(?P<sup>[{}{}]+)".format(SUP_DIGITS, SUP_SIGNS)
    def repl(m):
        base = m.group("base")
        sup  = m.group("sup").translate(SUP_MAP)
        return f"{base}**({sup})"
    return re.sub(patt, repl, expr)


def normalizar_expresion_usuario(user_expr: str) -> str:
    s = user_expr.strip()
    if not s:
        return s
    # Igualdad: LHS = RHS -> (LHS) - (RHS)
    if "=" in s:
        p = s.split("=")
        if len(p) != 2:
            raise ValueError("Sólo una igualdad con '='.")
        s = f"({p[0].strip()}) - ({p[1].strip()})"
    s = re.sub(r"\bX\b", "x", s)
    s = s.replace("^", "**")
    s = re.sub(r"\bln\(", "log(", s, flags=re.IGNORECASE)
    s = re.sub(r"\bsen\(", "sin(", s, flags=re.IGNORECASE)
    s = re.sub(r"√\s*\(", "sqrt(", s)      # √(x) -> sqrt(x)
    s = reemplazar_superindices_por_potencia(s) # superíndices reales
    return s


def numero_desde_texto(txt: str) -> float:
    s = normalizar_expresion_usuario(txt.strip())
    expr = parse_expr(
        s,
        transformations=(standard_transformations + (implicit_multiplication_application,)),
        local_dict={
            "x": X, "pi": math.pi, "e": math.e,
            "abs": abs, "asin": math.asin, "acos": math.acos, "atan": math.atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "exp": exp
        }
    )
    return float(expr.evalf())


def vista_previa_superindice(expr: str) -> str:
    s = re.sub(r"\^\(([^)]+)\)", lambda m: "<sup>" + m.group(1) + "</sup>", expr)
    s = re.sub(r"\^([\-+]?\d+(?:\.\d+)?)", lambda m: "<sup>" + m.group(1) + "</sup>", s)
    s = re.sub(r"\^([a-zA-Z])",           lambda m: "<sup>" + m.group(1) + "</sup>", s)
    return f"<span style='font-size:18px;'>f(x) = {s}</span>"


# ----------------- Núcleo de bisección -----------------

@dataclass
class FilaBiseccion:
    i: int; a: float; b: float; c: float; fa: float; fb: float; fc: float; ea: Optional[float]; subintervalo: str


@dataclass
class ResultadoBiseccion:
    raiz: Optional[float]; iteraciones: int; ultimo_error: Optional[float]
    tabla: List[FilaBiseccion]; mensaje: str


def biseccion(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-4,
    max_iter: int = 50,
) -> ResultadoBiseccion:
    """Bisección con tolerancia absoluta coherente: |b - a| / 2 < tol."""
    tabla: List[FilaBiseccion] = []
    fa, fb = f(a), f(b)
    if not np.isfinite(fa) or not np.isfinite(fb):
        return ResultadoBiseccion(None, 0, None, [], "f(a) o f(b) no es finito en el intervalo.")
    if fa * fb > 0:
        return ResultadoBiseccion(None, 0, None, [], "No hay cambio de signo en [a,b]. Elige otro intervalo.")

    c = (a + b) / 2.0
    fc = f(c)
    if not np.isfinite(fc):
        return ResultadoBiseccion(None, 0, None, [], "f(c) no es finito (posible asíntota o dominio inválido).")

    for i in range(1, max_iter + 1):
        # Error absoluto típico de bisección (longitud de intervalo a la mitad)
        ea = abs(b - a) / 2.0
        subintervalo = "[a,c]" if fa * fc < 0 else "[c,b]" if fc * fb < 0 else "raíz"
        tabla.append(FilaBiseccion(i, a, b, c, fa, fb, fc, ea, subintervalo))

        if fc == 0.0 or ea < tol:
            return ResultadoBiseccion(c, i, ea, tabla, "Convergencia alcanzada.")

        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc

        c = (a + b) / 2.0
        fc = f(c)
        if not np.isfinite(fc):
            return ResultadoBiseccion(None, i, ea, tabla, "f(c) dejó de ser finito (posible asíntota o dominio inválido).")

    return ResultadoBiseccion(c, max_iter, tabla[-1].ea if tabla else None, tabla, "Se alcanzó el máximo de iteraciones.")


def estimar_raices(f: Callable[[float], float], a: float, b: float, muestras: int = 400, eps: float = 1e-8) -> int:
    xs = np.linspace(a, b, muestras)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ys = np.array([f(x) for x in xs], dtype=float)
    signos = np.sign(ys * (np.abs(ys) > eps))
    return int(np.count_nonzero(np.diff(signos)))


# ----------------- UI -----------------

class LienzoGrafica(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 3), dpi=120)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.ax.grid(True, alpha=.35)

    def graficar_f(self, f, a, b, raiz=None):
        self.ax.clear(); self.ax.grid(True, alpha=.35); self.ax.set_title("f(x) en [a, b]")
        xs = np.linspace(a, b, 400)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ys = np.array([f(x) for x in xs], dtype=float)
        self.ax.plot(xs, ys, linewidth=2)
        self.ax.axhline(0, color="black", linewidth=1)
        if raiz is not None and np.isfinite(raiz):
            try:
                self.ax.scatter([raiz], [f(raiz)], s=60)
                self.ax.axvline(raiz, linestyle="--", linewidth=1)
            except Exception:
                pass
        self.draw_idle()


class Tarjeta(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")


class VentanaBiseccion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Método de Bisección — Compacto")
        self.resize(1180, 720)
        self.setMinimumSize(1020, 660)
        self._anim_refs = []  # evita que el GC mate animaciones en curso
        self.construir_ui()
        self.aplicar_estilos()
        self._animar_entrada()  # animación al abrir ventana

    # ---------- Construcción UI ----------
    def construir_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        titulo = QLabel("Método de Bisección")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        root.addWidget(titulo)

        split = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(split, 1)

        # ========== Panel Izquierdo ==========
        izquierdo = QWidget(); L = QVBoxLayout(izquierdo); L.setSpacing(10)
        izquierdo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        tarjeta_entrada = Tarjeta()
        grid = QGridLayout(tarjeta_entrada)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setContentsMargins(12, 12, 12, 12)

        # Campos
        self.le_f = QLineEdit(); self.le_f.setPlaceholderText("Ej.: cos(x) - x = 0   ó   x^2 - 2")
        self.le_f.textChanged.connect(self.actualizar_vista_previa)

        self.lbl_prev = QLabel("<i>Escribe una función...</i>")
        self.lbl_prev.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_prev.setWordWrap(True)

        self.sp_a = QDoubleSpinBox(); self.preparar_spin(self.sp_a, -1e9, 1e9, 0.0)
        self.sp_b = QDoubleSpinBox(); self.preparar_spin(self.sp_b, -1e9, 1e9, 1.0)

        self.le_tol = QLineEdit("1e-4"); self.le_tol.setPlaceholderText("Tolerancia (ABS): 1e-4, 10^-4, 10⁻⁴, 0.0001")
        self.sp_iter = QSpinBox(); self.sp_iter.setRange(1, 5000); self.sp_iter.setValue(50)

        # Distribución
        r = 0
        grid.addWidget(self.etiqueta_negrita("Escribe la función"), r, 0, 1, 2); r += 1
        grid.addWidget(self.le_f, r, 0, 1, 2); r += 1
        grid.addWidget(self.etiqueta_suave("Vista previa"), r, 0, 1, 2); r += 1
        grid.addWidget(self.lbl_prev, r, 0, 1, 2); r += 1

        grid.addWidget(self.etiqueta_negrita("a (límite inferior)"), r, 0)
        grid.addWidget(self.etiqueta_negrita("b (límite superior)"), r, 1); r += 1
        grid.addWidget(self.sp_a, r, 0)
        grid.addWidget(self.sp_b, r, 1); r += 1

        grid.addWidget(self.etiqueta_negrita("Tolerancia ABS (ε)"), r, 0)
        grid.addWidget(self.etiqueta_negrita("Iteraciones máx."), r, 1); r += 1
        grid.addWidget(self.le_tol, r, 0)
        grid.addWidget(self.sp_iter, r, 1); r += 1

        L.addWidget(tarjeta_entrada)

        # KPIs
        kpi = Tarjeta(); K = QHBoxLayout(kpi)
        self.k_roots = self.crear_kpi("Número de raíces (estimado)", "--")
        self.k_err   = self.crear_kpi("Error ABS (|b-a|/2)", "--")
        self.k_root  = self.crear_kpi("Raíz aproximada", "--")
        K.addWidget(self.k_roots, 1); K.addWidget(self.k_err, 1); K.addWidget(self.k_root, 1)
        L.addWidget(kpi)

        # Botones
        btns = QHBoxLayout(); btns.setSpacing(8)
        self.bt_run   = QPushButton("Resolver")
        self.bt_plot  = QPushButton("Graficar")
        self.bt_clear = QPushButton("Limpiar")
        self.bt_export= QPushButton("Exportar Excel")
        for b in (self.bt_run, self.bt_plot, self.bt_clear, self.bt_export):
            b.setMinimumHeight(36)
        self.bt_run.clicked.connect(self.resolver)
        self.bt_plot.clicked.connect(self.graficar)
        self.bt_clear.clicked.connect(self.limpiar)
        self.bt_export.clicked.connect(self.exportar_excel)
        btns.addWidget(self.bt_run, 3)
        btns.addWidget(self.bt_plot, 2)
        btns.addWidget(self.bt_clear, 1)
        btns.addWidget(self.bt_export, 2)
        L.addLayout(btns)

        # Teclado colapsable
        kb_tarjeta = Tarjeta(); kb_v = QVBoxLayout(kb_tarjeta); kb_v.setSpacing(8); kb_v.setContentsMargins(10, 8, 10, 10)
        encabezado = QHBoxLayout()
        self.toggle_kb = QToolButton(); self.toggle_kb.setText("Teclado matemático")
        self.toggle_kb.setCheckable(True); self.toggle_kb.setChecked(False)
        self.toggle_kb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        encabezado.addWidget(self.toggle_kb); encabezado.addStretch(1)
        kb_v.addLayout(encabezado)

        kb_contenedor = QWidget(); kb_grid = QGridLayout(kb_contenedor); kb_grid.setSpacing(6)
        for col in range(6):
            kb_grid.setColumnStretch(col, 1)

        def agregar_boton(r, c, texto, insertar=None):
            b = QPushButton(texto)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            b.setMinimumHeight(34)
            b.clicked.connect(lambda _=False, t=(texto if insertar is None else insertar): self.al_teclar(t))
            kb_grid.addWidget(b, r, c)

        # Fila 0
        agregar_boton(0,0,"sin","sin("); agregar_boton(0,1,"cos","cos("); agregar_boton(0,2,"tan","tan(")
        agregar_boton(0,3,"ln","ln(");   agregar_boton(0,4,"log","log(");  agregar_boton(0,5,"exp","exp(")
        # Fila 1
        agregar_boton(1,0,"√","sqrt(");  agregar_boton(1,1,"(","(");      agregar_boton(1,2,")",")")
        agregar_boton(1,3,"π","pi");     agregar_boton(1,4,"e","e");       agregar_boton(1,5,"^","^")
        # Fila 2
        agregar_boton(2,0,"7"); agregar_boton(2,1,"8"); agregar_boton(2,2,"9"); agregar_boton(2,3,"*","*"); agregar_boton(2,4,"/","/"); agregar_boton(2,5,"=","=")
        # Fila 3
        agregar_boton(3,0,"4"); agregar_boton(3,1,"5"); agregar_boton(3,2,"6"); agregar_boton(3,3,"+","+"); agregar_boton(3,4,"-","-"); agregar_boton(3,5,"x","x")
        # Fila 4
        agregar_boton(4,0,"1"); agregar_boton(4,1,"2"); agregar_boton(4,2,"3"); agregar_boton(4,3,"0","0"); agregar_boton(4,4,".","."); agregar_boton(4,5,"←","<BACK>")
        # Fila 5
        agregar_boton(5,0,"⁰","⁰"); agregar_boton(5,1,"¹","¹"); agregar_boton(5,2,"²","²"); agregar_boton(5,3,"³","³"); agregar_boton(5,4,"⁴","⁴"); agregar_boton(5,5,"C","<CLEAR>")
        # Fila 6
        agregar_boton(6,0,"⁵","⁵"); agregar_boton(6,1,"⁶","⁶"); agregar_boton(6,2,"⁷","⁷"); agregar_boton(6,3,"⁸","⁸"); agregar_boton(6,4,"⁹","⁹"); agregar_boton(6,5,"⁻","⁻")

        kb_v.addWidget(kb_contenedor)
        kb_contenedor.setVisible(False)
        self.toggle_kb.toggled.connect(kb_contenedor.setVisible)

        L.addWidget(kb_tarjeta)
        split.addWidget(izquierdo)

        # ========== Panel Derecho ==========
        derecho = QWidget(); R = QVBoxLayout(derecho); R.setSpacing(10)
        cab = QLabel("Procedimiento y gráfica")
        cab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cab.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        R.addWidget(cab)

        tabs = QTabWidget()
        # --- Tab gráfica ---
        tab_plot = QWidget(); tp = QVBoxLayout(tab_plot); tp.setContentsMargins(6,6,6,6)
        self.canvas = LienzoGrafica(); self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        tp.addWidget(self.toolbar)
        tp.addWidget(self.canvas, 1)
        tabs.addTab(tab_plot, "Gráfica")

        # --- Tab tabla ---
        tab_table = QWidget(); tt = QVBoxLayout(tab_table); tt.setContentsMargins(6,6,6,6)
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["i","a","b","c","f(a)","f(b)","f(c)","Ea (ABS)","subintervalo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tt.addWidget(self.table, 1)
        tabs.addTab(tab_table, "Tabla")

        R.addWidget(tabs, 1)
        split.addWidget(derecho)
        split.setSizes([520, 640])

        # Atajos
        from PyQt6.QtGui import QAction
        act_run   = QAction(self); act_run.setShortcut("Ctrl+R"); act_run.triggered.connect(self.resolver);       self.addAction(act_run)
        act_plot  = QAction(self); act_plot.setShortcut("Ctrl+G"); act_plot.triggered.connect(self.graficar);     self.addAction(act_plot)
        act_clear = QAction(self); act_clear.setShortcut("Ctrl+L"); act_clear.triggered.connect(self.limpiar);    self.addAction(act_clear)
        act_exp   = QAction(self); act_exp.setShortcut("Ctrl+S"); act_exp.triggered.connect(self.exportar_excel); self.addAction(act_exp)

    # ----- Estilos y utilidades -----
    def etiqueta_negrita(self, t: str) -> QLabel:
        l = QLabel(t); l.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold)); return l

    def etiqueta_suave(self, t: str) -> QLabel:
        l = QLabel(t); l.setStyleSheet("color:#5b6b7a;"); return l

    def crear_kpi(self, titulo: str, valor: str) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(6,6,6,6)
        t = QLabel(titulo); t.setStyleSheet("color:#6b7280; font-size:12px;")
        val = QLabel(valor); val.setObjectName("KPI"); val.setAlignment(Qt.AlignmentFlag.AlignLeft)
        v.addWidget(t); v.addWidget(val)
        return w

    def preparar_spin(self, sp: QDoubleSpinBox, mn: float, mx: float, val: float):
        sp.setRange(mn, mx)
        sp.setDecimals(8)
        sp.setSingleStep(0.1)
        sp.setValue(val)
        sp.setKeyboardTracking(False)
        sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def aplicar_estilos(self):
        self.setStyleSheet(
            """
            QWidget { background: #ffffff; color: #0f172a; font-family: 'Segoe UI', Arial; font-size: 11pt; }
            QFrame#Card {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            QLineEdit, QDoubleSpinBox, QSpinBox {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                padding: 8px 10px;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus { border-color: #2563eb; }
            QLabel#KPI { font-size: 20px; font-weight: 700; color: #0f172a; }
            QPushButton {
                background: #2563eb; color: white; border: none; border-radius: 10px; padding: 8px 10px; font-weight: 600;
            }
            QPushButton:hover { background: #1e40af; }
            QPushButton:disabled { background: #93c5fd; }
            QTableWidget { background: #ffffff; alternate-background-color: #f1f5f9; gridline-color: #e2e8f0; border: 1px solid #e2e8f0; border-radius: 12px; }
            QHeaderView::section { background: #e2e8f0; padding: 8px; border: none; border-right: 1px solid #cbd5e1; font-weight:600; }
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 10px; }
            QTabBar::tab { padding: 8px 14px; }
            """
        )

    # ---------- Lógica de inserción del teclado ----------
    def _editor_objetivo(self) -> QLineEdit:
        from PyQt6.QtWidgets import QApplication
        w = QApplication.focusWidget()
        return w if isinstance(w, QLineEdit) else self.le_f

    def al_teclar(self, t: str):
        edit = self._editor_objetivo()
        if t == "<BACK>":
            pos = edit.cursorPosition()
            if pos > 0:
                txt = edit.text()
                edit.setText(txt[:pos-1] + txt[pos:])
                edit.setCursorPosition(pos-1)
            return
        if t == "<CLEAR>":
            edit.clear(); return
        edit.insert(t); edit.setFocus()

    # ---------- Lógica principal ----------
    def construir_funcion(self) -> Optional[Callable[[float], float]]:
        raw = self.le_f.text().strip()
        if not raw:
            QMessageBox.warning(self, "Falta la función", "Por favor, escribe la función f(x) a analizar.")
            return None
        try:
            norm = normalizar_expresion_usuario(raw)
            expr = parse_expr(
                norm,
                transformations=(standard_transformations + (implicit_multiplication_application,)),
                local_dict={
                    "x": X, "pi": math.pi, "e": math.e,
                    "abs": abs, "asin": math.asin, "acos": math.acos, "atan": math.atan,
                    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
                    "exp": exp
                }
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al interpretar", f"No pude interpretar la función.\n\nDetalle: {e}")
            return None
        f = lambdify(X, expr, modules=["numpy", "math"])

        def envuelta(x: float) -> float:
            try:
                y = f(x)
            except Exception:
                y = np.nan
            return float(y)

        return envuelta

    def resolver(self):
        f = self.construir_funcion()
        if f is None:
            return
        a = self.sp_a.value(); b = self.sp_b.value()
        if a >= b:
            QMessageBox.warning(self, "Intervalo inválido", "Se requiere que a sea menor que b"); return
        try:
            tol = numero_desde_texto(self.le_tol.text())
            if tol <= 0:
                raise ValueError("La tolerancia debe ser positiva.")
        except Exception as e:
            QMessageBox.warning(self, "Tolerancia inválida", f"No pude interpretar la tolerancia.\nDetalle: {e}")
            return
        itmax = self.sp_iter.value()

        # KPI: estimación de raíces
        try:
            nr = estimar_raices(f, a, b)
            self._set_kpi(self.k_roots, str(nr))
        except Exception:
            self._set_kpi(self.k_roots, "—")

        res = biseccion(f, a, b, tol=tol, max_iter=itmax)

        # Volcar tabla
        self.table.setRowCount(0)
        for r in res.tabla:
            row = self.table.rowCount(); self.table.insertRow(row)
            values = [r.i, r.a, r.b, r.c, r.fa, r.fb, r.fc, r.ea, r.subintervalo]
            for c, val in enumerate(values):
                if isinstance(val, (int, float, np.floating)) and np.isfinite(val):
                    txt = f"{val:.10g}"
                elif val is None or (isinstance(val, float) and not np.isfinite(val)):
                    txt = ""
                else:
                    txt = str(val)
                item = QTableWidgetItem(txt)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, c, item)

        # KPIs (con animación)
        self._set_kpi(self.k_root, f"{res.raiz:.10f}" if res.raiz is not None else "—", flash=True)
        self._set_kpi(self.k_err,  "—" if res.ultimo_error is None or not np.isfinite(res.ultimo_error) else f"{res.ultimo_error:.6g}", flash=True)

        # Gráfica con suave fade
        try:
            self.canvas.graficar_f(f, a, b, raiz=res.raiz)
            self._fade_widget(self.canvas, 160)
        except Exception:
            pass

        # Mensaje
        msg = res.mensaje + (f"\nRaíz ≈ {res.raiz:.10f}\nIteraciones: {res.iteraciones}" if res.raiz is not None else "")
        QMessageBox.information(self, "Resultado", msg)

    def graficar(self):
        f = self.construir_funcion()
        if f is None:
            return
        a = self.sp_a.value(); b = self.sp_b.value()
        if a >= b:
            QMessageBox.warning(self, "Intervalo inválido", "Se requiere que a < b"); return
        self.canvas.graficar_f(f, a, b)
        self._fade_widget(self.canvas, 160)

    def limpiar(self):
        self.le_f.clear(); self.lbl_prev.setText("<i>Escribe una función...</i>")
        self.sp_a.setValue(0.0); self.sp_b.setValue(1.0); self.le_tol.setText("1e-4"); self.sp_iter.setValue(50)
        self.table.setRowCount(0)
        self._set_kpi(self.k_root, "--")
        self._set_kpi(self.k_err, "--")
        self._set_kpi(self.k_roots, "--")
        self.canvas.ax.clear(); self.canvas.draw_idle()

    def exportar_excel(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Exportar Excel", "No hay datos para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "biseccion.xlsx", "Excel (*.xlsx)")
        if not path:
            return
        try:
            # Encabezados
            encabezados = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            # Datos
            filas = []
            for r in range(self.table.rowCount()):
                fila = []
                for c in range(self.table.columnCount()):
                    item = self.table.item(r, c)
                    fila.append(item.text() if item else "")
                filas.append(fila)
            # Exportar con pandas -> Excel
            df = pandas.DataFrame(filas, columns=encabezados)
            df.to_excel(path, index=False, engine="openpyxl")
            QMessageBox.information(self, "Exportar Excel", f"Archivo guardado en:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Exportar Excel", f"Error al guardar:\n{e}")

    def actualizar_vista_previa(self, texto: str):
        if not texto.strip():
            self.lbl_prev.setText("<i>Escribe una función...</i>"); return
        try:
            self.lbl_prev.setText(vista_previa_superindice(texto))
        except Exception:
            self.lbl_prev.setText(texto)

    # ---------- Animaciones utilitarias ----------
    def _fade_widget(self, w: QWidget, dur_ms: int = 220):
        eff = QGraphicsOpacityEffect(w); w.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", w); anim.setDuration(dur_ms)
        anim.setStartValue(0.0); anim.setEndValue(1.0); anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim_refs.append(anim)

    def _flash(self, w: QWidget, dur_ms: int = 220):
        # pequeño parpadeo (0.35->1.0)
        eff = QGraphicsOpacityEffect(w); w.setGraphicsEffect(eff)
        a1 = QPropertyAnimation(eff, b"opacity", w); a1.setDuration(int(dur_ms * 0.5))
        a1.setStartValue(0.35); a1.setEndValue(1.0); a1.setEasingCurve(QEasingCurve.Type.OutCubic)
        a2 = QPropertyAnimation(eff, b"opacity", w); a2.setDuration(int(dur_ms * 0.5))
        a2.setStartValue(1.0); a2.setEndValue(1.0)
        group = QParallelAnimationGroup(w); group.addAnimation(a1); group.addAnimation(a2)
        group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim_refs.append(group)

    def _set_kpi(self, contenedor: QWidget, valor: str, flash: bool=False):
        lbl = contenedor.findChild(QLabel, "KPI")
        if lbl:
            lbl.setText(valor)
            if flash:
                self._flash(lbl, 220)

    def _animar_entrada(self):
        # animación inicial: contenedor completo
        eff = QGraphicsOpacityEffect(self); self.setGraphicsEffect(eff)
        anim_op = QPropertyAnimation(eff, b"opacity", self); anim_op.setDuration(260)
        anim_op.setStartValue(0.0); anim_op.setEndValue(1.0); anim_op.setEasingCurve(QEasingCurve.Type.OutCubic)

        start_geo = self.geometry()
        anim_geo = QPropertyAnimation(self, b"geometry", self); anim_geo.setDuration(260)
        anim_geo.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim_geo.setStartValue(QRect(start_geo.x(), start_geo.y() - 12, start_geo.width(), start_geo.height()))
        anim_geo.setEndValue(start_geo)

        group = QParallelAnimationGroup(self); group.addAnimation(anim_op); group.addAnimation(anim_geo)
        group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim_refs.append(group)
