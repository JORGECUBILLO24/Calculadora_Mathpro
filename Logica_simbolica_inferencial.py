<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Logica_MathPro_Ultimate_Safe.py
Diseño Premium + Compatibilidad T460s (Sin GPU)
"""
import sys
import re
import itertools
import os

# --- CONFIGURACIÓN DE SEGURIDAD GRÁFICA (Vital para tu PC) ---
os.environ["QT_OPENGL"] = "software"

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont, QColor, QIcon, QCursor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QLineEdit, QPushButton, QFrame, QGridLayout, 
    QTextBrowser, QMessageBox, QGraphicsDropShadowEffect
)

# =============================================================================
#  MOTOR LÓGICO (CEREBRO MATEMÁTICO)
# =============================================================================
class MotorLogico:
    @staticmethod
    def obtener_variables(texto):
        t = texto
        for op in ["→", "↔", "∧", "∨", "⊕", "¬", "(", ")"]:
            t = t.replace(op, " ")
        posibles = set(re.findall(r"\b[a-zA-Z]\w*\b", t))
        reservadas = {'not', 'or', 'and', 'True', 'False'}
        return sorted(list(posibles - reservadas))

    @staticmethod
    def traducir_a_python(expr):
        e = expr
        e = e.replace("↔", " == ")
        e = e.replace("→", " <= ") # Implicación binaria
        e = e.replace("∧", " and ")
        e = e.replace("∨", " or ")
        e = e.replace("¬", " not ")
        e = e.replace("⊕", " ^ ")
        return e

    @staticmethod
    def evaluar(expr_python, valores_dict):
        try:
            vals_bool = {k: bool(v) for k, v in valores_dict.items()}
            resultado_bool = eval(expr_python, {"__builtins__": None}, vals_bool)
            return 1 if resultado_bool else 0
        except:
            return -1

# =============================================================================
#  HOJA DE ESTILOS (CSS PROFESIONAL)
# =============================================================================
STYLESHEET = """
    QMainWindow, QWidget { 
        background-color: #F4F7F6; 
        font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #333; 
    }
    
    /* Paneles (Tarjetas) */
    QFrame#Card { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        border: 1px solid #E0E0E0;
    }
    
    /* Títulos */
    QLabel#Header { 
        color: #2C3E50; font-size: 18px; font-weight: 700; margin-bottom: 5px;
    }
    QLabel#LabelInput {
        color: #546E7A; font-weight: 600; font-size: 13px;
    }

    /* Campos de Texto */
    QTextEdit, QLineEdit { 
        background-color: #FAFAFA; border: 2px solid #ECEFF1; border-radius: 8px; 
        padding: 10px; font-family: 'Consolas', monospace; font-size: 14px; color: #263238;
    }
    QTextEdit:focus, QLineEdit:focus { 
        border: 2px solid #29B6F6; background-color: #FFF; 
    }

    /* Botones de Símbolos */
    QPushButton.SymBtn { 
        background-color: #E1F5FE; color: #0288D1; border: none; border-radius: 6px; 
        font-weight: bold; font-size: 16px; padding: 5px;
    }
    QPushButton.SymBtn:hover { background-color: #B3E5FC; color: #01579B; }
    QPushButton.SymBtn:pressed { background-color: #81D4FA; }

    /* Botón Principal */
    QPushButton#BtnRun {
        background-color: #0288D1; color: white; font-weight: bold; border-radius: 8px; 
        padding: 12px; font-size: 14px; letter-spacing: 1px;
    }
    QPushButton#BtnRun:hover { background-color: #0277BD; }
    QPushButton#BtnRun:pressed { background-color: #01579B; }

    /* Botón Limpiar */
    QPushButton#BtnClear {
        background-color: #ECEFF1; color: #607D8B; border: 1px solid #CFD8DC; border-radius: 8px; padding: 10px;
    }
    QPushButton#BtnClear:hover { background-color: #CFD8DC; color: #455A64; }

    /* Visor de Resultados */
    QTextBrowser { border: none; background-color: transparent; }
"""

# =============================================================================
#  CLASE PRINCIPAL
# =============================================================================
class VentanaLogica(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lógica Inferencial - MathPro Ultimate")
        self.resize(1280, 760)
        self.setStyleSheet(STYLESHEET)
        self.ultimo_foco = None 
        self._init_ui()
        self.txt_premisas.setFocus()
        self.ultimo_foco = self.txt_premisas

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)

        # ==================== PANEL IZQUIERDO (CONTROLES) ====================
        left_card = QFrame(); left_card.setObjectName("Card")
        # Sombra para efecto de elevación
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,20)); shadow.setOffset(0,4)
        left_card.setGraphicsEffect(shadow)
        left_card.setFixedWidth(420)
        
        l_lay = QVBoxLayout(left_card); l_lay.setContentsMargins(20,25,20,25); l_lay.setSpacing(15)

        l_lay.addWidget(QLabel("Entrada de Datos", objectName="Header"))

        l_lay.addWidget(QLabel("Premisas (una por línea):", objectName="LabelInput"))
        self.txt_premisas = QTextEdit()
        self.txt_premisas.setPlaceholderText("p → q\n¬q")
        self.txt_premisas.setFixedHeight(120)
        self.txt_premisas.installEventFilter(self)
        l_lay.addWidget(self.txt_premisas)

        l_lay.addWidget(QLabel("Conclusión:", objectName="LabelInput"))
        self.txt_concl = QLineEdit()
        self.txt_concl.setPlaceholderText("¬p")
        self.txt_concl.installEventFilter(self)
        l_lay.addWidget(self.txt_concl)

        l_lay.addWidget(QLabel("Teclado Lógico:", objectName="LabelInput"))
        grid = QGridLayout(); grid.setSpacing(8)
        simbolos = [
            ('¬', 'Negación'), ('∧', 'Y'), ('∨', 'O'), ('⊕', 'XOR'),
            ('→', 'Si..entonces'), ('↔', 'Si y solo si'), ('(', 'Abrir'), (')', 'Cerrar')
        ]
        
        r, c = 0, 0
        for char, tooltip in simbolos:
            btn = QPushButton(char)
            btn.setProperty("class", "SymBtn")
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(45, 45)
            btn.clicked.connect(lambda _, x=char: self.insertar_simbolo(x))
            grid.addWidget(btn, r, c)
            c += 1
            if c > 3: c=0; r+=1
        l_lay.addLayout(grid)

        l_lay.addStretch()
        
        btn_run = QPushButton("ANALIZAR ARGUMENTO"); btn_run.setObjectName("BtnRun")
        btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_run.clicked.connect(self.resolver)
        l_lay.addWidget(btn_run)

        btn_clr = QPushButton("Limpiar Todo"); btn_clr.setObjectName("BtnClear")
        btn_clr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clr.clicked.connect(self.limpiar)
        l_lay.addWidget(btn_clr)

        # ==================== PANEL DERECHO (RESULTADOS) ====================
        right_card = QFrame(); right_card.setObjectName("Card")
        shadow2 = QGraphicsDropShadowEffect(); shadow2.setBlurRadius(20); shadow2.setColor(QColor(0,0,0,20)); shadow2.setOffset(0,4)
        right_card.setGraphicsEffect(shadow2)
        
        r_lay = QVBoxLayout(right_card); r_lay.setContentsMargins(0,0,0,0)
        
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(False)
        r_lay.addWidget(self.viewer)

        main_layout.addWidget(left_card)
        main_layout.addWidget(right_card, 1)
        
        self.mostrar_bienvenida()

    # --- MANEJO DE FOCO ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            if obj == self.txt_premisas or obj == self.txt_concl:
                self.ultimo_foco = obj
        return super().eventFilter(obj, event)

    def insertar_simbolo(self, char):
        target = self.ultimo_foco if self.ultimo_foco else self.txt_premisas
        if isinstance(target, QLineEdit): target.insert(char)
        else: target.insertPlainText(char)
        target.setFocus()

    def limpiar(self):
        self.txt_premisas.clear(); self.txt_concl.clear()
        self.ultimo_foco = self.txt_premisas
        self.mostrar_bienvenida()

    def mostrar_bienvenida(self):
        self.viewer.setHtml("""
        <div style='padding:40px; text-align:center; font-family:"Segoe UI";'>
            <h1 style='color:#0288D1; font-size:32px; margin-bottom:10px;'>Módulo de Lógica Inferencial</h1>
            <p style='color:#78909C; font-size:16px;'>
                Ingresa las premisas y la conclusión para generar automáticamente la<br>
                <b>Tabla de Verdad</b> y validar el argumento.
            </p>
            <div style='margin-top:30px; padding:20px; background:#F1F8E9; border:1px solid #C5E1A5; border-radius:8px; display:inline-block; text-align:left;'>
                <b style='color:#2E7D32;'>💡 Tip:</b><br>
                Puedes usar el teclado virtual o escribir directamente.<br>
                El sistema soporta tautologías, contradicciones y contingencias.
            </div>
        </div>
        """)

    # --- CÁLCULO ---
    def resolver(self):
        raw_prems = [l.strip() for l in self.txt_premisas.toPlainText().splitlines() if l.strip()]
        raw_conc = self.txt_concl.text().strip()

        if not raw_prems or not raw_conc:
            QMessageBox.warning(self, "Faltan Datos", "Ingresa premisas y conclusión.")
            return

        txt_total = " ".join(raw_prems) + " " + raw_conc
        vars_list = MotorLogico.obtener_variables(txt_total)
        
        if not vars_list:
            QMessageBox.warning(self, "Error", "No se encontraron variables (letras).")
            return

        # Traducir
        try:
            py_prems = [MotorLogico.traducir_a_python(p) for p in raw_prems]
            py_conc = MotorLogico.traducir_a_python(raw_conc)
        except:
            QMessageBox.critical(self, "Error", "Error traduciendo fórmulas.")
            return

        n = len(vars_list)
        combs = list(itertools.product([1, 0], repeat=n))
        
        # HTML Construction (Estilo Tabla de Excel Bonita)
        html = """
        <style>
            body { font-family: 'Segoe UI'; margin:0; padding: 20px; }
            table { border-collapse: collapse; width: 100%; font-size: 13px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            th { background-color: #0277BD; color: white; padding: 12px; border: 1px solid #01579B; }
            td { padding: 8px; text-align: center; border: 1px solid #CFD8DC; color: #37474F; }
            tr:nth-child(even) { background-color: #F5F5F5; }
            
            .crit { background-color: #E1F5FE !important; font-weight: bold; color: #01579B; border: 2px solid #0288D1; }
            .fail { background-color: #FFEBEE !important; font-weight: bold; color: #C62828; border: 2px solid #E53935; }
            
            .box { padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; border: 1px solid; }
            .valid { background-color: #E8F5E9; color: #2E7D32; border-color: #A5D6A7; }
            .invalid { background-color: #FFEBEE; color: #C62828; border-color: #EF9A9A; }
            
            .formula-list { background: #FFF; border: 1px solid #E0E0E0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .mono { font-family: Consolas; color: #0277BD; font-weight: bold; }
        </style>
        """
        
        # Header Tabla
        html += "<table><tr>"
        for v in vars_list: html += f"<th>{v}</th>"
        for i in range(len(raw_prems)): html += f"<th>P{i+1}</th>"
        html += "<th>Conclusión</th></tr>"

        valid = True
        contra = None

        for vals in combs:
            env = dict(zip(vars_list, vals))
            try:
                rps = [MotorLogico.evaluar(p, env) for p in py_prems]
                rc = MotorLogico.evaluar(py_conc, env)
            except:
                self.viewer.setHtml("<h3 style='color:red'>Error de sintaxis en fórmulas</h3>")
                return

            all_p = all(r==1 for r in rps)
            
            cls = ""
            if all_p:
                if rc == 1: cls = "class='crit'" # Fila crítica válida
                else:
                    cls = "class='fail'" # Contraejemplo
                    valid = False
                    contra = env
            
            html += f"<tr {cls}>"
            for v in vars_list: html += f"<td>{'V' if env[v] else 'F'}</td>"
            for r in rps: html += f"<td>{'V' if r else 'F'}</td>"
            html += f"<td>{'V' if rc else 'F'}</td></tr>"

        html += "</table><br><br>"

        # Resultado final
        if valid:
            res = """
            <div class='box valid'>
                <h2 style='margin:0'>✅ ARGUMENTO VÁLIDO</h2>
                <small>(Es una Tautología)</small>
            </div>
            """
        else:
            txt_c = ", ".join([f"{k}={'V' if v else 'F'}" for k,v in contra.items()])
            res = f"""
            <div class='box invalid'>
                <h2 style='margin:0'>❌ ARGUMENTO INVÁLIDO</h2>
                <p>Falla cuando: <b>{txt_c}</b></p>
            </div>
            """

        # Resumen fórmulas
        f_list = "<div class='formula-list'><b>Estructura Lógica:</b><ul style='margin-top:5px;'>"
        for i, p in enumerate(raw_prems): f_list += f"<li>P{i+1}: <span class='mono'>{p}</span></li>"
        f_list += f"<li>C: <span class='mono'>{raw_conc}</span></li></ul></div>"

        # Ensamblar
        self.viewer.setHtml(res + f_list + html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VentanaLogica()
    w.show()
=======
# -*- coding: utf-8 -*-
"""
Logica_MathPro_Ultimate_Safe.py
Diseño Premium + Compatibilidad T460s (Sin GPU)
"""
import sys
import re
import itertools
import os

# --- CONFIGURACIÓN DE SEGURIDAD GRÁFICA (Vital para tu PC) ---
os.environ["QT_OPENGL"] = "software"

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont, QColor, QIcon, QCursor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QLineEdit, QPushButton, QFrame, QGridLayout, 
    QTextBrowser, QMessageBox, QGraphicsDropShadowEffect
)

# =============================================================================
#  MOTOR LÓGICO (CEREBRO MATEMÁTICO)
# =============================================================================
class MotorLogico:
    @staticmethod
    def obtener_variables(texto):
        t = texto
        for op in ["→", "↔", "∧", "∨", "⊕", "¬", "(", ")"]:
            t = t.replace(op, " ")
        posibles = set(re.findall(r"\b[a-zA-Z]\w*\b", t))
        reservadas = {'not', 'or', 'and', 'True', 'False'}
        return sorted(list(posibles - reservadas))

    @staticmethod
    def traducir_a_python(expr):
        e = expr
        e = e.replace("↔", " == ")
        e = e.replace("→", " <= ") # Implicación binaria
        e = e.replace("∧", " and ")
        e = e.replace("∨", " or ")
        e = e.replace("¬", " not ")
        e = e.replace("⊕", " ^ ")
        return e

    @staticmethod
    def evaluar(expr_python, valores_dict):
        try:
            vals_bool = {k: bool(v) for k, v in valores_dict.items()}
            resultado_bool = eval(expr_python, {"__builtins__": None}, vals_bool)
            return 1 if resultado_bool else 0
        except:
            return -1

# =============================================================================
#  HOJA DE ESTILOS (CSS PROFESIONAL)
# =============================================================================
STYLESHEET = """
    QMainWindow, QWidget { 
        background-color: #F4F7F6; 
        font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #333; 
    }
    
    /* Paneles (Tarjetas) */
    QFrame#Card { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        border: 1px solid #E0E0E0;
    }
    
    /* Títulos */
    QLabel#Header { 
        color: #2C3E50; font-size: 18px; font-weight: 700; margin-bottom: 5px;
    }
    QLabel#LabelInput {
        color: #546E7A; font-weight: 600; font-size: 13px;
    }

    /* Campos de Texto */
    QTextEdit, QLineEdit { 
        background-color: #FAFAFA; border: 2px solid #ECEFF1; border-radius: 8px; 
        padding: 10px; font-family: 'Consolas', monospace; font-size: 14px; color: #263238;
    }
    QTextEdit:focus, QLineEdit:focus { 
        border: 2px solid #29B6F6; background-color: #FFF; 
    }

    /* Botones de Símbolos */
    QPushButton.SymBtn { 
        background-color: #E1F5FE; color: #0288D1; border: none; border-radius: 6px; 
        font-weight: bold; font-size: 16px; padding: 5px;
    }
    QPushButton.SymBtn:hover { background-color: #B3E5FC; color: #01579B; }
    QPushButton.SymBtn:pressed { background-color: #81D4FA; }

    /* Botón Principal */
    QPushButton#BtnRun {
        background-color: #0288D1; color: white; font-weight: bold; border-radius: 8px; 
        padding: 12px; font-size: 14px; letter-spacing: 1px;
    }
    QPushButton#BtnRun:hover { background-color: #0277BD; }
    QPushButton#BtnRun:pressed { background-color: #01579B; }

    /* Botón Limpiar */
    QPushButton#BtnClear {
        background-color: #ECEFF1; color: #607D8B; border: 1px solid #CFD8DC; border-radius: 8px; padding: 10px;
    }
    QPushButton#BtnClear:hover { background-color: #CFD8DC; color: #455A64; }

    /* Visor de Resultados */
    QTextBrowser { border: none; background-color: transparent; }
"""

# =============================================================================
#  CLASE PRINCIPAL
# =============================================================================
class VentanaLogica(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lógica Inferencial - MathPro Ultimate")
        self.resize(1280, 760)
        self.setStyleSheet(STYLESHEET)
        self.ultimo_foco = None 
        self._init_ui()
        self.txt_premisas.setFocus()
        self.ultimo_foco = self.txt_premisas

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)

        # ==================== PANEL IZQUIERDO (CONTROLES) ====================
        left_card = QFrame(); left_card.setObjectName("Card")
        # Sombra para efecto de elevación
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,20)); shadow.setOffset(0,4)
        left_card.setGraphicsEffect(shadow)
        left_card.setFixedWidth(420)
        
        l_lay = QVBoxLayout(left_card); l_lay.setContentsMargins(20,25,20,25); l_lay.setSpacing(15)

        l_lay.addWidget(QLabel("Entrada de Datos", objectName="Header"))

        l_lay.addWidget(QLabel("Premisas (una por línea):", objectName="LabelInput"))
        self.txt_premisas = QTextEdit()
        self.txt_premisas.setPlaceholderText("p → q\n¬q")
        self.txt_premisas.setFixedHeight(120)
        self.txt_premisas.installEventFilter(self)
        l_lay.addWidget(self.txt_premisas)

        l_lay.addWidget(QLabel("Conclusión:", objectName="LabelInput"))
        self.txt_concl = QLineEdit()
        self.txt_concl.setPlaceholderText("¬p")
        self.txt_concl.installEventFilter(self)
        l_lay.addWidget(self.txt_concl)

        l_lay.addWidget(QLabel("Teclado Lógico:", objectName="LabelInput"))
        grid = QGridLayout(); grid.setSpacing(8)
        simbolos = [
            ('¬', 'Negación'), ('∧', 'Y'), ('∨', 'O'), ('⊕', 'XOR'),
            ('→', 'Si..entonces'), ('↔', 'Si y solo si'), ('(', 'Abrir'), (')', 'Cerrar')
        ]
        
        r, c = 0, 0
        for char, tooltip in simbolos:
            btn = QPushButton(char)
            btn.setProperty("class", "SymBtn")
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(45, 45)
            btn.clicked.connect(lambda _, x=char: self.insertar_simbolo(x))
            grid.addWidget(btn, r, c)
            c += 1
            if c > 3: c=0; r+=1
        l_lay.addLayout(grid)

        l_lay.addStretch()
        
        btn_run = QPushButton("ANALIZAR ARGUMENTO"); btn_run.setObjectName("BtnRun")
        btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_run.clicked.connect(self.resolver)
        l_lay.addWidget(btn_run)

        btn_clr = QPushButton("Limpiar Todo"); btn_clr.setObjectName("BtnClear")
        btn_clr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clr.clicked.connect(self.limpiar)
        l_lay.addWidget(btn_clr)

        # ==================== PANEL DERECHO (RESULTADOS) ====================
        right_card = QFrame(); right_card.setObjectName("Card")
        shadow2 = QGraphicsDropShadowEffect(); shadow2.setBlurRadius(20); shadow2.setColor(QColor(0,0,0,20)); shadow2.setOffset(0,4)
        right_card.setGraphicsEffect(shadow2)
        
        r_lay = QVBoxLayout(right_card); r_lay.setContentsMargins(0,0,0,0)
        
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(False)
        r_lay.addWidget(self.viewer)

        main_layout.addWidget(left_card)
        main_layout.addWidget(right_card, 1)
        
        self.mostrar_bienvenida()

    # --- MANEJO DE FOCO ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            if obj == self.txt_premisas or obj == self.txt_concl:
                self.ultimo_foco = obj
        return super().eventFilter(obj, event)

    def insertar_simbolo(self, char):
        target = self.ultimo_foco if self.ultimo_foco else self.txt_premisas
        if isinstance(target, QLineEdit): target.insert(char)
        else: target.insertPlainText(char)
        target.setFocus()

    def limpiar(self):
        self.txt_premisas.clear(); self.txt_concl.clear()
        self.ultimo_foco = self.txt_premisas
        self.mostrar_bienvenida()

    def mostrar_bienvenida(self):
        self.viewer.setHtml("""
        <div style='padding:40px; text-align:center; font-family:"Segoe UI";'>
            <h1 style='color:#0288D1; font-size:32px; margin-bottom:10px;'>Módulo de Lógica Inferencial</h1>
            <p style='color:#78909C; font-size:16px;'>
                Ingresa las premisas y la conclusión para generar automáticamente la<br>
                <b>Tabla de Verdad</b> y validar el argumento.
            </p>
            <div style='margin-top:30px; padding:20px; background:#F1F8E9; border:1px solid #C5E1A5; border-radius:8px; display:inline-block; text-align:left;'>
                <b style='color:#2E7D32;'>💡 Tip:</b><br>
                Puedes usar el teclado virtual o escribir directamente.<br>
                El sistema soporta tautologías, contradicciones y contingencias.
            </div>
        </div>
        """)

    # --- CÁLCULO ---
    def resolver(self):
        raw_prems = [l.strip() for l in self.txt_premisas.toPlainText().splitlines() if l.strip()]
        raw_conc = self.txt_concl.text().strip()

        if not raw_prems or not raw_conc:
            QMessageBox.warning(self, "Faltan Datos", "Ingresa premisas y conclusión.")
            return

        txt_total = " ".join(raw_prems) + " " + raw_conc
        vars_list = MotorLogico.obtener_variables(txt_total)
        
        if not vars_list:
            QMessageBox.warning(self, "Error", "No se encontraron variables (letras).")
            return

        # Traducir
        try:
            py_prems = [MotorLogico.traducir_a_python(p) for p in raw_prems]
            py_conc = MotorLogico.traducir_a_python(raw_conc)
        except:
            QMessageBox.critical(self, "Error", "Error traduciendo fórmulas.")
            return

        n = len(vars_list)
        combs = list(itertools.product([1, 0], repeat=n))
        
        # HTML Construction (Estilo Tabla de Excel Bonita)
        html = """
        <style>
            body { font-family: 'Segoe UI'; margin:0; padding: 20px; }
            table { border-collapse: collapse; width: 100%; font-size: 13px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            th { background-color: #0277BD; color: white; padding: 12px; border: 1px solid #01579B; }
            td { padding: 8px; text-align: center; border: 1px solid #CFD8DC; color: #37474F; }
            tr:nth-child(even) { background-color: #F5F5F5; }
            
            .crit { background-color: #E1F5FE !important; font-weight: bold; color: #01579B; border: 2px solid #0288D1; }
            .fail { background-color: #FFEBEE !important; font-weight: bold; color: #C62828; border: 2px solid #E53935; }
            
            .box { padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; border: 1px solid; }
            .valid { background-color: #E8F5E9; color: #2E7D32; border-color: #A5D6A7; }
            .invalid { background-color: #FFEBEE; color: #C62828; border-color: #EF9A9A; }
            
            .formula-list { background: #FFF; border: 1px solid #E0E0E0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .mono { font-family: Consolas; color: #0277BD; font-weight: bold; }
        </style>
        """
        
        # Header Tabla
        html += "<table><tr>"
        for v in vars_list: html += f"<th>{v}</th>"
        for i in range(len(raw_prems)): html += f"<th>P{i+1}</th>"
        html += "<th>Conclusión</th></tr>"

        valid = True
        contra = None

        for vals in combs:
            env = dict(zip(vars_list, vals))
            try:
                rps = [MotorLogico.evaluar(p, env) for p in py_prems]
                rc = MotorLogico.evaluar(py_conc, env)
            except:
                self.viewer.setHtml("<h3 style='color:red'>Error de sintaxis en fórmulas</h3>")
                return

            all_p = all(r==1 for r in rps)
            
            cls = ""
            if all_p:
                if rc == 1: cls = "class='crit'" # Fila crítica válida
                else:
                    cls = "class='fail'" # Contraejemplo
                    valid = False
                    contra = env
            
            html += f"<tr {cls}>"
            for v in vars_list: html += f"<td>{'V' if env[v] else 'F'}</td>"
            for r in rps: html += f"<td>{'V' if r else 'F'}</td>"
            html += f"<td>{'V' if rc else 'F'}</td></tr>"

        html += "</table><br><br>"

        # Resultado final
        if valid:
            res = """
            <div class='box valid'>
                <h2 style='margin:0'>✅ ARGUMENTO VÁLIDO</h2>
                <small>(Es una Tautología)</small>
            </div>
            """
        else:
            txt_c = ", ".join([f"{k}={'V' if v else 'F'}" for k,v in contra.items()])
            res = f"""
            <div class='box invalid'>
                <h2 style='margin:0'>❌ ARGUMENTO INVÁLIDO</h2>
                <p>Falla cuando: <b>{txt_c}</b></p>
            </div>
            """

        # Resumen fórmulas
        f_list = "<div class='formula-list'><b>Estructura Lógica:</b><ul style='margin-top:5px;'>"
        for i, p in enumerate(raw_prems): f_list += f"<li>P{i+1}: <span class='mono'>{p}</span></li>"
        f_list += f"<li>C: <span class='mono'>{raw_conc}</span></li></ul></div>"

        # Ensamblar
        self.viewer.setHtml(res + f_list + html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VentanaLogica()
    w.show()
>>>>>>> ef984993824d81b7fabae7af610d92334376c7ab
    sys.exit(app.exec())