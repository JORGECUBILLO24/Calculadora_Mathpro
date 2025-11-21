# -*- coding: utf-8 -*-
"""
MenuPrincipal_MathPro_Final_Fixed_v2.py
Corrección: Error de argumentos en AuthorCard solucionado.
"""
import os
import sys

# --- PARCHE GPU (VITAL) ---
os.environ["QT_OPENGL"] = "software"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty, QTimer
from PyQt6.QtGui import QFont, QColor, QAction, QPainter, QBrush, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QStackedWidget, QSizePolicy, QGraphicsOpacityEffect, 
    QMenu, QGridLayout, QMessageBox, QScrollArea
)

# =============================================================================
#  IMPORTACIONES SEGURAS
# =============================================================================
MODULES = {}
def safe_import():
    global MODULES
    try: from Metodo_biseccion import VentanaBiseccion; MODULES['Biseccion'] = VentanaBiseccion
    except: pass
    try: from Metodo_newton_raphson import VentanaNewton; MODULES['Newton'] = VentanaNewton
    except: pass
    try: from Metodo_secante import VentanaSecante; MODULES['Secante'] = VentanaSecante
    except: pass
    try: from Metodo_Falsa_Posición import VentanaFalsaPosicion; MODULES['Falsa'] = VentanaFalsaPosicion
    except: pass
    try: from Matrices import VentanaMatrices; MODULES['Matrices'] = VentanaMatrices
    except: pass
    try: from Determinantes import VentanaDeterminantes; MODULES['Determinantes'] = VentanaDeterminantes
    except: pass
    try: from Multiplicacion_escalar import VentanaMultiplicacionEscalar; MODULES['Escalar'] = VentanaMultiplicacionEscalar
    except: pass
    try: from derivadas import ManimDerivadaApp; MODULES['Derivadas'] = ManimDerivadaApp
    except: pass
    try: from Conjuntos import CalculadoraConjuntos; MODULES['Conjuntos'] = CalculadoraConjuntos
    except: pass
    try: from Logica_simbolica_inferencial import VentanaLogica; MODULES['Logica'] = VentanaLogica
    except: pass

safe_import()

# =============================================================================
#  TEMAS
# =============================================================================

# TEMA DARK PRO
THEME_DARK = """
QMainWindow, QWidget#MainWidget { background-color: #1E1E2E; }
QFrame#SideMenu { background-color: #181825; border-right: 1px solid #11111b; }
QLabel#AppTitle { color: #FFFFFF; font-weight: 900; font-size: 24px; letter-spacing: 1px; }
QLabel#Version { color: #6C7086; font-size: 12px; font-style: italic; margin-bottom: 20px; }
QPushButton.MenuBtn { background-color: transparent; border: none; color: #A6ADC8; text-align: left; padding: 15px 20px; font-size: 15px; border-radius: 8px; font-weight: 600; }
QPushButton.MenuBtn:hover { background-color: #313244; color: #FFFFFF; }
QPushButton.MenuBtn:checked { background-color: #313244; color: #89B4FA; font-weight: bold; border-left: 5px solid #89B4FA; }
QLabel#LogoCenter { color: #FFFFFF; font-weight: 900; font-size: 110px; opacity: 0.8; }
QStackedWidget#MainStack { background-color: #1E1E2E; border-radius: 0px; }
QMenu { background-color: #181825; border: 1px solid #313244; border-radius: 8px; padding: 5px 0; }
QMenu::item { padding: 8px 25px; font-size: 14px; color: #CDD6F4; }
QMenu::item:selected { background-color: #89B4FA; color: #1E1E2E; font-weight: bold; }
QScrollArea { background: transparent; border: none; }
QWidget#ScrollContents { background: transparent; }
"""

# TEMA LIGHT PREMIUM
THEME_LIGHT = """
QMainWindow, QWidget#MainWidget { background-color: #F5F5F0; }
QFrame#SideMenu { background-color: #FFFFFF; border-right: 1px solid #D7CCC8; box-shadow: 2px 0 10px rgba(0,0,0,0.05); }
QLabel#AppTitle { color: #37474F; font-weight: 900; font-size: 24px; letter-spacing: 1px; }
QLabel#Version { color: #78909C; font-size: 12px; font-style: italic; margin-bottom: 20px; }
QPushButton.MenuBtn { background-color: transparent; border: none; color: #546E7A; text-align: left; padding: 15px 20px; font-size: 15px; border-radius: 8px; font-weight: 600; }
QPushButton.MenuBtn:hover { background-color: #ECEFF1; color: #263238; }
QPushButton.MenuBtn:checked { background-color: #E0E0E0; color: #000000; font-weight: bold; border-left: 5px solid #37474F; }
QLabel#LogoCenter { color: #546E7A; font-weight: 900; font-size: 110px; opacity: 0.3; }
QStackedWidget#MainStack { background-color: #F5F5F0; border-radius: 0px; }
QMenu { background-color: #FFFFFF; border: 1px solid #B0BEC5; border-radius: 8px; padding: 5px 0; }
QMenu::item { padding: 8px 25px; font-size: 14px; color: #37474F; }
QMenu::item:selected { background-color: #37474F; color: white; font-weight: bold; }
QScrollArea { background: transparent; border: none; }
QWidget#ScrollContents { background: transparent; }
"""

# =============================================================================
#  COMPONENTES UI
# =============================================================================
class RippleButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._ripple_col = QColor(255, 255, 255, 40)
        self._rad = 0; self._center = None
        self._anim = QPropertyAnimation(self, b"radius", self)
        self._anim.setDuration(400); self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._anim.finished.connect(self.update)
    @pyqtProperty(int)
    def radius(self): return self._rad
    @radius.setter
    def radius(self, r): self._rad = r; self.update()
    def mousePressEvent(self, e):
        self._center = e.position(); self._rad = 0
        self._anim.setStartValue(0); self._anim.setEndValue(max(self.width(), self.height()) * 1.5)
        self._anim.start(); super().mousePressEvent(e)
    def paintEvent(self, e):
        super().paintEvent(e)
        if self._rad > 0 and self._center:
            p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QBrush(self._ripple_col)); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(self._center, self._rad, self._rad)

class AuthorCard(QFrame):
    # CORRECCIÓN: Se asegura de recibir 3 argumentos
    def __init__(self, name, role, delay):
        super().__init__()
        self.setFixedSize(260, 160)
        self.setStyleSheet("""
            QFrame { 
                background-color: rgba(255, 255, 255, 0.95); 
                border-radius: 15px; 
                border: 1px solid rgba(128, 128, 128, 0.2); 
                border-bottom: 4px solid #448AFF;
            }
            QFrame:hover { margin-top: -5px; border-bottom-color: #2979FF; background-color: #FFFFFF; }
        """)
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av = QLabel(name[0:2].upper()); av.setFixedSize(50,50); av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet("background:#448AFF; color:white; border-radius:25px; font-size:20px; font-weight:bold;")
        n = QLabel(name); n.setStyleSheet("font-size:17px; font-weight:bold; color:#1e293b; margin-top:8px; border:none; background:transparent;")
        r = QLabel(role); r.setStyleSheet("font-size:12px; color:#64748b; font-style:italic; border:none; background:transparent;")
        l.addWidget(av, 0, Qt.AlignmentFlag.AlignCenter)
        l.addWidget(n, 0, Qt.AlignmentFlag.AlignCenter)
        l.addWidget(r, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.eff = QGraphicsOpacityEffect(self); self.setGraphicsEffect(self.eff)
        self.anim = QPropertyAnimation(self.eff, b"opacity"); self.anim.setDuration(800); self.anim.setStartValue(0); self.anim.setEndValue(1)
        QTimer.singleShot(delay, self.anim.start)

class AuthorsPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0,0,0,0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content_widget = QWidget(); content_widget.setObjectName("ScrollContents")
        
        l = QVBoxLayout(content_widget); l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        t = QLabel("Créditos y Desarrollo"); t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet("font-size:36px; font-weight:900; color:#448AFF; margin-top:30px; background:transparent;")
        
        st = QLabel("Proyecto MathPro - Ingeniería en Sistemas"); st.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.setStyleSheet("font-size:16px; color:#607D8B; margin-bottom:40px; background:transparent;")
        
        l.addWidget(t); l.addWidget(st)
        
        grid_w = QWidget(); grid_w.setStyleSheet("background:transparent;")
        grid = QGridLayout(grid_w); grid.setSpacing(30); grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # CORRECCIÓN: Datos completos (Nombre, Rol, Delay)
        team = [
            ("Jorge Cubillo", "Líder & Backend", 0), 
            ("Ervin Perez", "UI/UX Design", 150),
            ("Isaac Mora", "Lógica Matemática", 300), 
            ("Diego Luquez", "QA & Testing", 450)
        ]
        pos = [(0,0), (0,1), (1,0), (1,1)]
        
        # CORRECCIÓN: Desempaquetado correcto (name, role, delay)
        for (nm, rl, d), p in zip(team, pos): 
            grid.addWidget(AuthorCard(nm, rl, d), *p)
        
        l.addWidget(grid_w); l.addStretch()
        scroll.setWidget(content_widget); main_layout.addWidget(scroll)

class VentanaFuncionesExtras(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.main = parent_main
        l = QVBoxLayout(self); l.setAlignment(Qt.AlignmentFlag.AlignCenter); l.setSpacing(30)
        
        t = QLabel("Herramientas Adicionales"); t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet("font-size: 32px; font-weight: bold; color: #1565C0;")
        l.addWidget(t)

        grid = QGridLayout(); grid.setSpacing(20)
        opts = [("Calculadora Derivadas", "Derivadas", "#1E88E5", "⚡"),
                ("Teoría Conjuntos", "Conjuntos", "#43A047", "⚪"),
                ("Lógica Simbólica", "Logica", "#FB8C00", "🧠")]
        
        for i, (txt, key, col, icon) in enumerate(opts):
            btn = QPushButton(f"{icon}\n{txt}")
            btn.setFixedSize(220, 150); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: white; color: {col}; border: 2px solid {col}; border-radius: 15px; font-size: 18px; font-weight: bold; }} 
                QPushButton:hover {{ background-color: {col}; color: white; }}
            """)
            btn.clicked.connect(lambda _, k=key: self.main.load_module(MODULES.get(k)))
            grid.addWidget(btn, 0, i)
        l.addLayout(grid)

# =============================================================================
#  VENTANA PRINCIPAL
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathPro Suite - Ultimate Edition")
        self.resize(1150, 720) 
        self.is_dark = True
        
        main_widget = QWidget(); main_widget.setObjectName("MainWidget")
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        
        # SIDEBAR
        sidebar = QFrame(); sidebar.setObjectName("SideMenu"); sidebar.setFixedWidth(260)
        sl = QVBoxLayout(sidebar); sl.setContentsMargins(15,40,15,20); sl.setSpacing(8)
        
        self.lbl_title = QLabel("MATHPRO", objectName="AppTitle")
        sl.addWidget(self.lbl_title)
        sl.addWidget(QLabel("v5.4 Final", objectName="Version")); sl.addSpacing(15)
        
        self.btn_home = RippleButton("🏠  Inicio")
        self.btn_anum = RippleButton("📈  Análisis Numérico")
        self.btn_alg  = RippleButton("🔢  Álgebra Lineal")
        self.btn_extr = RippleButton("🚀  Funciones Extras")
        self.btn_auth = RippleButton("👥  Autores")
        
        for b in [self.btn_home, self.btn_anum, self.btn_alg, self.btn_extr, self.btn_auth]:
            b.setProperty("class", "MenuBtn"); b.setCheckable(True); sl.addWidget(b)
        
        sl.addStretch()
        self.btn_theme = QPushButton("☀️  Modo Claro"); self.btn_theme.setObjectName("ThemeBtn")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_theme.setFixedHeight(40)
        self.btn_theme.clicked.connect(self.toggle_theme)
        sl.addWidget(self.btn_theme)
        
        layout.addWidget(sidebar)
        
        # CONTENIDO
        self.stack = QStackedWidget(); self.stack.setObjectName("MainStack")
        
        # P0: Home
        p_home = QWidget(); hl = QVBoxLayout(p_home); hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QLabel("MATHPRO"); logo.setObjectName("LogoCenter"); logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(logo); self.stack.addWidget(p_home)
        
        # P1: Autores
        self.stack.addWidget(AuthorsPage())

        # P2: Funciones Extras
        self.stack.addWidget(VentanaFuncionesExtras(self))

        # P3: Contenedor de Módulos
        self.container = QWidget(); self.stack.addWidget(self.container)
        
        layout.addWidget(self.stack)
        
        # Conexiones
        self.btn_home.clicked.connect(self.go_home)
        self.btn_auth.clicked.connect(self.go_authors)
        self.btn_extr.clicked.connect(self.go_extras)
        
        self.menu_anum = self._mk_menu([("Bisección", 'Biseccion'), ("Newton-Raphson", 'Newton'), ("Secante", 'Secante'), ("Falsa Posición", 'Falsa')])
        self.btn_anum.clicked.connect(lambda: self._show_menu(self.btn_anum, self.menu_anum))
        
        self.menu_alg = self._mk_menu([("Matrices", 'Matrices'), ("Determinantes", 'Determinantes'), ("Mult. Escalar", 'Escalar')])
        self.btn_alg.clicked.connect(lambda: self._show_menu(self.btn_alg, self.menu_alg))
        
        # Aplicar tema inicial
        self.setStyleSheet(THEME_DARK)
        self.go_home()

    def _mk_menu(self, items):
        m = QMenu(self)
        for name, key in items:
            if key in MODULES: m.addAction(name, lambda checked=False, k=key: self.load_module(MODULES[k]))
        return m

    def _show_menu(self, btn, menu):
        self._reset_btns(); btn.setChecked(True)
        menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def load_module(self, WidgetClass):
        if not WidgetClass: return
        try:
            widget = WidgetClass()
            if isinstance(widget, QMainWindow):
                widget.setWindowFlags(Qt.WindowType.Widget)
                wrapper = QWidget(); wl = QVBoxLayout(wrapper); wl.setContentsMargins(0,0,0,0)
                wl.addWidget(widget); widget = wrapper
            
            old = self.stack.widget(3); self.stack.removeWidget(old)
            if old: old.deleteLater()
            
            self.stack.insertWidget(3, widget); self.stack.setCurrentIndex(3)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar módulo:\n{e}")

    def toggle_theme(self):
        if self.is_dark:
            self.setStyleSheet(THEME_LIGHT)
            self.btn_theme.setText("🌙  Modo Oscuro")
            self.btn_theme.setStyleSheet("background-color: #263238; color: white;")
            self.is_dark = False
        else:
            self.setStyleSheet(THEME_DARK)
            self.btn_theme.setText("☀️  Modo Claro")
            self.btn_theme.setStyleSheet("background-color: #ef233c; color: white;")
            self.is_dark = True

    def go_home(self): self._reset_btns(); self.btn_home.setChecked(True); self.stack.setCurrentIndex(0)
    def go_authors(self): self._reset_btns(); self.btn_auth.setChecked(True); self.stack.setCurrentIndex(1)
    def go_extras(self): self._reset_btns(); self.btn_extr.setChecked(True); self.stack.setCurrentIndex(2)
    def _reset_btns(self):
        for b in [self.btn_home, self.btn_anum, self.btn_alg, self.btn_extr, self.btn_auth]: b.setChecked(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())