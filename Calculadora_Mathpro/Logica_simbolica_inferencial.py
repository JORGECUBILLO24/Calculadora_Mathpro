from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QScrollArea, QMessageBox
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt
import sys
import itertools
import re

# -------------------------
# Funciones lógicas
# -------------------------
def corregir_expresion(expr):
    expr = expr.replace(" ", "")
    open_par = expr.count("(")
    close_par = expr.count(")")
    if open_par > close_par:
        expr += ")" * (open_par - close_par)
    elif close_par > open_par:
        expr = "(" * (close_par - open_par) + expr
    expr = re.sub(r"[∧∨→↔⊕]{2,}", lambda m: m.group(0)[-1], expr)
    expr = re.sub(r"¬{2,}", "¬", expr)
    expr = expr.strip("∧∨→↔⊕")
    return expr

def evaluar_expresion(expr, valores):
    expr_eval = expr
    for var, val in valores.items():
        expr_eval = re.sub(rf"\b{var}\b", str(int(val)), expr_eval)

    def implica(p, q): return max(1 - p, q)
    def equiv(p, q): return int(p == q)

    expr_eval = expr_eval.replace("¬", "1-")
    expr_eval = expr_eval.replace("∧", "*")
    expr_eval = expr_eval.replace("∨", "max")
    expr_eval = expr_eval.replace("⊕", "^")

    while "→" in expr_eval:
        match = re.search(r'(\d+|\([^\(\)]+\))→(\d+|\([^\(\)]+\))', expr_eval)
        if match:
            expr_eval = expr_eval.replace(match.group(0), f"implica({match.group(1)},{match.group(2)})")
        else:
            break
    while "↔" in expr_eval:
        match = re.search(r'(\d+|\([^\(\)]+\))↔(\d+|\([^\(\)]+\))', expr_eval)
        if match:
            expr_eval = expr_eval.replace(match.group(0), f"equiv({match.group(1)},{match.group(2)})")
        else:
            break

    try:
        resultado = eval(expr_eval, {"max": max, "implica": implica, "equiv": equiv})
        return 1 if resultado else 0
    except:
        return 0

def evaluar_argumento(premisas, conclusion):
    todas_vars = sorted({c for expr in premisas+[conclusion] for c in expr if c.isalpha()})
    tablas = []
    valido = True
    for valores in itertools.product([0,1], repeat=len(todas_vars)):
        env = dict(zip(todas_vars, valores))
        resultados_premisas = [evaluar_expresion(p, env) for p in premisas]
        resultado_conclusion = evaluar_expresion(conclusion, env)
        tablas.append((env, resultados_premisas, resultado_conclusion))
        if all(r==1 for r in resultados_premisas) and resultado_conclusion != 1:
            valido = False
    return tablas, "VÁLIDO" if valido else "INVÁLIDO", todas_vars

def formatear_tabla_legible(tablas, todas_vars, premisas):
    col_widths = {v: max(len(v), 1) for v in todas_vars}
    for i, p in enumerate(premisas):
        col_widths[f"P{i+1}"] = max(len(f"P{i+1}"), 1)
    col_widths["Conclusión"] = max(len("Conclusión"), 1)

    for fila in tablas:
        env, res_prem, res_concl = fila
        for v in todas_vars:
            col_widths[v] = max(col_widths[v], len(str(env[v])))
        for i, r in enumerate(res_prem):
            col_widths[f"P{i+1}"] = max(col_widths[f"P{i+1}"], len(str(r)))
        col_widths["Conclusión"] = max(col_widths["Conclusión"], len(str(res_concl)))

    header = " | ".join(f"{v:^{col_widths[v]}}" for v in todas_vars)
    header += " | " + " | ".join(f"{'P'+str(i+1):^{col_widths['P'+str(i+1)]}}" for i in range(len(premisas)))
    header += " | " + f"{'Conclusión':^{col_widths['Conclusión']}}"
    line = "-+-".join('-'*col_widths[v] for v in todas_vars)
    line += "-+-" + "-+-".join('-'*col_widths['P'+str(i+1)] for i in range(len(premisas)))
    line += "-+-" + '-'*col_widths['Conclusión']

    filas_str = [header, line]
    for fila in tablas:
        env, res_prem, res_concl = fila
        fila_str = " | ".join(f"{str(env[v]):^{col_widths[v]}}" for v in todas_vars)
        fila_str += " | " + " | ".join(f"{str(r):^{col_widths['P'+str(i+1)]}}" for i, r in enumerate(res_prem))
        fila_str += " | " + f"{str(res_concl):^{col_widths['Conclusión']}}"
        filas_str.append(fila_str)

    return "\n".join(filas_str)

# -------------------------
# Interfaz PyQt6
# -------------------------
class LogicaSimbolicaTeclado(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lógica Simbólica e Inferencial")
        self.setGeometry(100, 50, 1000, 700)
        self.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.premisas_edit = QTextEdit()
        self.premisas_edit.setFont(QFont("Consolas", 14))
        self.premisas_edit.setPlaceholderText("Escribe las premisas, una por línea")
        layout.addWidget(QLabel("Premisas:"))
        layout.addWidget(self.premisas_edit)

        self.conclusion_edit = QTextEdit()
        self.conclusion_edit.setFont(QFont("Consolas", 14))
        self.conclusion_edit.setPlaceholderText("Escribe la conclusión")
        layout.addWidget(QLabel("Conclusión:"))
        layout.addWidget(self.conclusion_edit)

        simbolos = ['¬', '∧', '∨', '→', '↔', '⊕', '(', ')']
        teclado_layout = QHBoxLayout()
        for s in simbolos:
            btn = QPushButton(s)
            btn.setFont(QFont("Arial", 16))
            btn.setStyleSheet("background-color: #4dabf5; color: #fff; padding:6px; border-radius:6px;")
            btn.clicked.connect(lambda checked, ch=s: self.insertar_simbolo(ch))
            teclado_layout.addWidget(btn)
        layout.addLayout(teclado_layout)

        eval_btn = QPushButton("Evaluar Argumento")
        eval_btn.setFont(QFont("Arial", 16))
        eval_btn.setStyleSheet("background-color: #457b9d; color: #ffffff; padding: 12px; border-radius:8px;")
        eval_btn.clicked.connect(self.evaluar)
        layout.addWidget(eval_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Consolas", 12))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.result_label.setStyleSheet("background-color: #ffffff; padding: 8px; border: 1px solid #ccc;")
        scroll.setWidget(self.result_label)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def insertar_simbolo(self, ch):
        if self.premisas_edit.hasFocus():
            cursor = self.premisas_edit.textCursor()
            cursor.insertText(ch)
            self.premisas_edit.setTextCursor(cursor)
        elif self.conclusion_edit.hasFocus():
            cursor = self.conclusion_edit.textCursor()
            cursor.insertText(ch)
            self.conclusion_edit.setTextCursor(cursor)
        else:
            cursor = self.premisas_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(ch)
            self.premisas_edit.setTextCursor(cursor)

    def evaluar(self):
        premisas = [corregir_expresion(p) for p in self.premisas_edit.toPlainText().splitlines() if p.strip()]
        conclusion = corregir_expresion(self.conclusion_edit.toPlainText())
        if not premisas or not conclusion:
            QMessageBox.warning(self, "Error", "Debes ingresar al menos una premisa y la conclusión")
            return

        tablas, estado, todas_vars = evaluar_argumento(premisas, conclusion)
        texto = f"El argumento es {estado}\n\n"
        texto += formatear_tabla_legible(tablas, todas_vars, premisas)
        self.result_label.setText(texto)


