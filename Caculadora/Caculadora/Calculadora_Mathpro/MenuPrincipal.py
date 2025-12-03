import sys
import os

# --- PARCHE PARA RENDIMIENTO ---
os.environ["QT_OPENGL"] = "software"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QGridLayout, QScrollArea, 
    QLineEdit, QGraphicsDropShadowEffect, QStackedWidget, QMessageBox, 
    QDialog, QSlider, QComboBox, QButtonGroup, QRadioButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# =============================================================================
#  TRADUCCIONES
# =============================================================================
TRANSLATIONS = {
    "ES": {
        "search_ph": "Buscar en YouTube...",
        "sec_num": "Análisis Numérico",
        "sec_math": "Matemáticas & Lógica",
        "sec_sys": "Sistema",
        "btn_open": "Abrir Herramienta",
        "btn_back": "← Volver al Menú",
        "settings_title": "Configuración Global",
        "lbl_zoom": "Zoom:",
        "lbl_lang": "Idioma:",
        "lbl_theme": "Tema:",
        "theme_light": "Claro (Light)",
        "theme_dark": "Oscuro (ChatGPT)",
        "btn_apply": "GUARDAR Y APLICAR",
        "devs_title": "Créditos",
        "devs_sub": "Ingeniería en Sistemas - UAM",
        "desc_bis": "Encuentra raíces dividiendo intervalos.",
        "desc_fal": "Método cerrado con interpolación lineal.",
        "desc_new": "Método abierto de convergencia rápida.",
        "desc_sec": "Alternativa a Newton sin derivadas.",
        "desc_mat": "Suma, resta y multiplicación.",
        "desc_det": "Cálculo recursivo por cofactores.",
        "desc_esc": "Producto de un número por matriz.",
        "desc_der": "Visualización gráfica paso a paso.",
        "desc_con": "Operaciones con diagramas de Venn.",
        "desc_log": "Tablas de verdad y proposiciones.",
        "desc_set": "Configurar zoom y tema.",
        "desc_dev": "Equipo de desarrollo."
    },
    "EN": {
        "search_ph": "Search on YouTube...",
        "sec_num": "Numerical Analysis",
        "sec_math": "Math & Logic",
        "sec_sys": "System",
        "btn_open": "Open Tool",
        "btn_back": "← Back to Menu",
        "settings_title": "Global Settings",
        "lbl_zoom": "Zoom:",
        "lbl_lang": "Language:",
        "lbl_theme": "Theme:",
        "theme_light": "Light",
        "theme_dark": "Dark (ChatGPT)",
        "btn_apply": "SAVE & APPLY",
        "devs_title": "Credits",
        "devs_sub": "Systems Engineering - UAM",
        "desc_bis": "Roots via closed intervals.",
        "desc_fal": "Improved closed method.",
        "desc_new": "Fast convergence.",
        "desc_sec": "Alternative without derivatives.",
        "desc_mat": "Fundamental operations.",
        "desc_det": "Recursive calculation.",
        "desc_esc": "Basic operation.",
        "desc_der": "Step-by-step graphs.",
        "desc_con": "Venn diagrams.",
        "desc_log": "Truth tables.",
        "desc_set": "App settings.",
        "desc_dev": "Development Team."
    }
}
CURRENT_LANG = "ES"

# =============================================================================
#  IMPORTACIÓN SEGURA
# =============================================================================
MODULES = {}

def safe_import():
    global MODULES
    try: 
        from Metodo_biseccion import VentanaBiseccion
        MODULES['Biseccion'] = VentanaBiseccion
    except: pass
    try: 
        from Metodo_newton_raphson import VentanaNewton
        MODULES['Newton'] = VentanaNewton
    except: pass
    try: 
        from Metodo_secante import VentanaSecante
        MODULES['Secante'] = VentanaSecante
    except: pass
    try: 
        from Metodo_Falsa_Posición import VentanaFalsaPosicion
        MODULES['Falsa'] = VentanaFalsaPosicion
    except: pass
    try: 
        from Matrices import VentanaMatrices
        MODULES['Matrices'] = VentanaMatrices
    except: pass
    try: 
        from Determinantes import VentanaDeterminantes
        MODULES['Determinantes'] = VentanaDeterminantes
    except: pass
    try: 
        from Multiplicacion_escalar import VentanaMultiplicacionEscalar
        MODULES['Escalar'] = VentanaMultiplicacionEscalar
    except: pass
    try: 
        from derivadas import ManimDerivadaApp
        MODULES['Derivadas'] = ManimDerivadaApp
    except: pass
    try: 
        from Conjuntos import CalculadoraConjuntos
        MODULES['Conjuntos'] = CalculadoraConjuntos
    except: pass
    try: 
        from Logica_simbolica_inferencial import VentanaLogica
        MODULES['Logica'] = VentanaLogica
    except: pass

safe_import()

# =============================================================================
#  ESTILOS CSS (SIN BORDES EN TEXTOS)
# =============================================================================

STYLES_LIGHT = """
/* FONDO GLOBAL */
QWidget { background-color: #F8FAFC; color: #1F2937; font-family: 'Segoe UI', sans-serif; }
QScrollArea { background-color: transparent; border: none; }

/* HEADER */
QFrame#Header { background-color: #FFFFFF; border-bottom: 1px solid #E5E7EB; }
QPushButton#LogoText { color: #111827; font-weight: 900; font-size: 32px; font-family: 'Arial Black'; border: none; background: transparent; }
QLabel#LogoBar { background-color: #3B82F6; border-radius: 3px; }

/* TARJETAS (SOLO CLASE .Card TIENE BORDE) */
QFrame.Card { 
    background-color: #FFFFFF; 
    border: 1px solid #E5E7EB; 
    border-radius: 16px; 
}
QFrame.Card QLabel { border: none; background: transparent; }

QFrame.SectionBox { background-color: #F3F4F6; border: 1px solid #E5E7EB; border-radius: 24px; }

/* HOVER */
QFrame.Card:hover { border: 1px solid #3B82F6; }

/* TEXTOS */
QLabel { color: #374151; border: none; }
QLabel.SectionTitle { color: #111827; font-weight: 800; font-size: 26px; }
QLabel.CardTitle { color: #111827; font-weight: 700; font-size: 18px; background: transparent; }
QLabel.CardDesc { color: #6B7280; font-size: 13px; font-weight: 400; background: transparent; }
QLabel.SettingLabel { font-size: 15px; font-weight: 600; color: #374151; }

/* INPUTS */
QLineEdit { 
    background-color: #F9FAFB; border: 2px solid #E5E7EB; border-radius: 12px; padding: 0 15px; color: #111827; font-size: 14px;
}
QLineEdit:focus { border: 2px solid #3B82F6; background-color: #FFFFFF; }

/* BOTONES */
QPushButton { background-color: #FFFFFF; border: 1px solid #D1D5DB; border-radius: 10px; padding: 8px; color: #4B5563; font-weight: 600; }
QPushButton:hover { background-color: #F3F4F6; color: #111827; }

/* BOTÓN TARJETA (AZUL SUAVE) */
QPushButton.CardBtn {
    background-color: #E8F0FE; 
    color: #1A73E8;            
    border: none;              
    border-radius: 8px; 
    font-weight: 700; 
    padding: 10px;
    font-size: 13px;
}
QPushButton.CardBtn:hover { background-color: #D2E3FC; color: #174EA6; }

/* ACCIONES */
QPushButton#YoutubeBtn { background-color: #EF4444; color: white; border: none; border-radius: 12px; font-size: 16px; }
QPushButton#BackBtn { background-color: #3B82F6; color: white; border: none; border-radius: 12px; font-weight: 700; padding: 0 20px; }
"""

STYLES_DARK = """
/* MODO OSCURO */
QWidget { background-color: #202123; color: #ECECF1; font-family: 'Segoe UI', sans-serif; }
QScrollArea { background-color: transparent; border: none; }
QFrame#Header { background-color: #202123; border-bottom: 1px solid #3F3F46; }
QPushButton#LogoText { color: #FFFFFF; font-weight: 900; font-size: 32px; font-family: 'Arial Black'; border: none; background: transparent; }
QLabel#LogoBar { background-color: #EF4444; border-radius: 3px; }

/* TARJETAS */
QFrame.Card { background-color: #2A2B32; border: 1px solid #3F3F46; border-radius: 16px; }
QFrame.Card QLabel { border: none; background: transparent; }
QFrame.SectionBox { background-color: #2A2B32; border: 1px solid #3F3F46; border-radius: 24px; }
QFrame.Card:hover { border: 1px solid #EF4444; }

/* TEXTOS */
QLabel { color: #ECECF1; border: none; }
QLabel.SectionTitle { color: #FFFFFF; font-weight: 800; font-size: 26px; }
QLabel.CardTitle { color: #FFFFFF; font-weight: 700; font-size: 18px; background: transparent; }
QLabel.CardDesc { color: #A1A1AA; font-size: 13px; font-weight: 400; background: transparent; }

/* INPUTS */
QLineEdit { background-color: #343541; border: 2px solid #565869; border-radius: 12px; padding: 0 15px; color: #FFF; }
QLineEdit:focus { border: 2px solid #EF4444; background-color: #40414F; }

/* BOTONES */
QPushButton { background-color: #343541; border: 1px solid #565869; border-radius: 10px; padding: 8px; color: #ECECF1; font-weight: 600; }
QPushButton:hover { background-color: #40414F; color: #FFF; }

/* BOTÓN TARJETA (ROJO SUAVE) */
QPushButton.CardBtn {
    background-color: #3A2E2E; color: #F87171; border: none; border-radius: 8px; font-weight: 700; padding: 10px; font-size: 13px;
}
QPushButton.CardBtn:hover { background-color: #453030; color: #EF4444; }

QPushButton#YoutubeBtn { background-color: #EF4444; color: white; border: none; border-radius: 12px; font-size: 16px; }
QPushButton#BackBtn { background-color: #EF4444; color: white; border: none; border-radius: 12px; font-weight: 700; padding: 0 20px; }
"""

# =============================================================================
#  CLASES
# =============================================================================
class YoutubeViewer(QDialog):
    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"YouTube: {query}")
        self.resize(1100, 650)
        l = QVBoxLayout(self); l.setContentsMargins(0,0,0,0)
        self.web = QWebEngineView()
        self.web.setUrl(QUrl(f"https://www.youtube.com/results?search_query={query}"))
        l.addWidget(self.web)

class ModuleCard(QFrame):
    def __init__(self, title_key, desc_key, icon, action_key, main_window, is_int=False):
        super().__init__()
        self.main = main_window; self.key = action_key; self.is_int = is_int
        self.t_key = title_key; self.d_key = desc_key
        
        self.setProperty("class", "Card")
        self.setFixedSize(260, 180) 
        
        l = QVBoxLayout(self); l.setContentsMargins(20,20,20,20); l.setSpacing(4)

        h = QHBoxLayout()
        ico = QLabel(icon); ico.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        h.addWidget(ico); h.addStretch()
        l.addLayout(h)
        l.addSpacing(5)

        self.lbl_t = QLabel(TRANSLATIONS[CURRENT_LANG].get(title_key, title_key))
        self.lbl_t.setProperty("class", "CardTitle")
        l.addWidget(self.lbl_t)

        self.lbl_d = QLabel(TRANSLATIONS[CURRENT_LANG].get(desc_key, desc_key))
        self.lbl_d.setProperty("class", "CardDesc")
        self.lbl_d.setWordWrap(True)
        self.lbl_d.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.lbl_d.setMinimumHeight(35) 
        l.addWidget(self.lbl_d)

        l.addStretch()

        self.btn = QPushButton(TRANSLATIONS[CURRENT_LANG]["btn_open"])
        self.btn.setProperty("class", "CardBtn")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self.act)
        l.addWidget(self.btn)

    def act(self):
        if self.is_int:
            if self.key == "settings": self.main.switch_page(2)
            elif self.key == "devs": self.main.switch_page(3)
        else: self.main.switch_page(1, mod_key=self.key)

    def refresh(self):
        self.lbl_t.setText(TRANSLATIONS[CURRENT_LANG].get(self.t_key, self.t_key))
        self.lbl_d.setText(TRANSLATIONS[CURRENT_LANG].get(self.d_key, self.d_key))
        self.btn.setText(TRANSLATIONS[CURRENT_LANG]["btn_open"])

# =============================================================================
#  PÁGINAS
# =============================================================================
class DashboardPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main; self.cards = []
        l = QVBoxLayout(self); l.setContentsMargins(0,0,0,0)
        
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); content.setObjectName("DashboardContent")
        cl = QVBoxLayout(content); cl.setContentsMargins(60, 30, 60, 60); cl.setSpacing(40)

        # 1. Numérico
        self.t1 = QLabel(TRANSLATIONS[CURRENT_LANG]["sec_num"]); self.t1.setProperty("class", "SectionTitle")
        self.t1.setAlignment(Qt.AlignmentFlag.AlignCenter); cl.addWidget(self.t1)
        
        box1 = QFrame(); box1.setProperty("class", "SectionBox")
        bl1 = QVBoxLayout(box1); bl1.setContentsMargins(30, 30, 30, 30)
        g1 = QGridLayout(); g1.setSpacing(20)
        d1 = [("Bisección", "desc_bis", "✂️", "Biseccion"), ("Falsa Posición", "desc_fal", "🎯", "Falsa"),
              ("Newton-Raphson", "desc_new", "🚀", "Newton"), ("Secante", "desc_sec", "📉", "Secante")]
        
        # CAMBIO AQUI: cols=2 para matriz 2x2
        self._grid(g1, d1, 2) 
        bl1.addLayout(g1); cl.addWidget(box1)

        # 2. Math
        self.t2 = QLabel(TRANSLATIONS[CURRENT_LANG]["sec_math"]); self.t2.setProperty("class", "SectionTitle")
        self.t2.setAlignment(Qt.AlignmentFlag.AlignCenter); cl.addWidget(self.t2)
        
        box2 = QFrame(); box2.setProperty("class", "SectionBox")
        bl2 = QVBoxLayout(box2); bl2.setContentsMargins(30, 30, 30, 30)
        g2 = QGridLayout(); g2.setSpacing(20)
        d2 = [("Matrices", "desc_mat", "🔢", "Matrices"), ("Determinantes", "desc_det", "📐", "Determinantes"),
              ("Mult. Escalar", "desc_esc", "✖️", "Escalar"), ("Derivadas", "desc_der", "🎬", "Derivadas"),
              ("Conjuntos", "desc_con", "⭕", "Conjuntos"), ("Lógica", "desc_log", "🧠", "Logica")]
        
        # CAMBIO AQUI: cols=2 para matriz 2 columnas (se verán 3 filas)
        self._grid(g2, d2, 2)
        bl2.addLayout(g2); cl.addWidget(box2)

        # 3. System
        self.t3 = QLabel(TRANSLATIONS[CURRENT_LANG]["sec_sys"]); self.t3.setProperty("class", "SectionTitle")
        self.t3.setAlignment(Qt.AlignmentFlag.AlignCenter); cl.addWidget(self.t3)
        
        box3 = QFrame(); box3.setProperty("class", "SectionBox")
        bl3 = QVBoxLayout(box3); bl3.setContentsMargins(30, 30, 30, 30)
        g3 = QGridLayout(); g3.setSpacing(20)
        d3 = [("Ajustes", "desc_set", "⚙️", "settings"), ("Equipo", "desc_dev", "👥", "devs")]
        
        # CAMBIO AQUI: cols=2
        self._grid(g3, d3, 2, True)
        bl3.addLayout(g3); cl.addWidget(box3)

        cl.addStretch()
        scroll.setWidget(content); l.addWidget(scroll)

    def _grid(self, g, data, cols, is_int=False):
        r, c = 0, 0
        for ti, de, ic, k in data:
            card = ModuleCard(ti, de, ic, k, self.main, is_int)
            self.cards.append(card); g.addWidget(card, r, c); c+=1
            if c>=cols: c=0; r+=1
    
    def refresh(self):
        self.t1.setText(TRANSLATIONS[CURRENT_LANG]["sec_num"])
        self.t2.setText(TRANSLATIONS[CURRENT_LANG]["sec_math"])
        self.t3.setText(TRANSLATIONS[CURRENT_LANG]["sec_sys"])
        for c in self.cards: c.refresh()

class SettingsPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        l = QVBoxLayout(self); l.setContentsMargins(150, 50, 150, 50); l.setSpacing(20)
        
        self.tit = QLabel(TRANSLATIONS[CURRENT_LANG]["settings_title"]); self.tit.setProperty("class", "SectionTitle")
        l.addWidget(self.tit)

        card = QFrame(); card.setProperty("class", "Card"); 
        cl = QVBoxLayout(card); cl.setContentsMargins(40,40,40,40); cl.setSpacing(30)
        
        # ZOOM
        self.l_z = QLabel(TRANSLATIONS[CURRENT_LANG]["lbl_zoom"]); self.l_z.setProperty("class", "SettingLabel")
        self.sl_z = QSlider(Qt.Orientation.Horizontal); self.sl_z.setRange(8, 20); self.sl_z.setValue(10)
        self.v_z = QLabel("10 pt"); self.v_z.setProperty("class", "SettingLabel")
        self.sl_z.valueChanged.connect(lambda v: self.v_z.setText(f"{v} pt"))
        h1 = QHBoxLayout(); h1.addWidget(self.l_z); h1.addStretch(); h1.addWidget(self.sl_z); h1.addWidget(self.v_z)
        cl.addLayout(h1)

        # IDIOMA
        self.l_la = QLabel(TRANSLATIONS[CURRENT_LANG]["lbl_lang"]); self.l_la.setProperty("class", "SettingLabel")
        self.cb_la = QComboBox(); self.cb_la.addItems(["Español", "English"])
        h2 = QHBoxLayout(); h2.addWidget(self.l_la); h2.addStretch(); h2.addWidget(self.cb_la)
        cl.addLayout(h2)

        # TEMA
        self.l_th = QLabel(TRANSLATIONS[CURRENT_LANG]["lbl_theme"]); self.l_th.setProperty("class", "SettingLabel")
        self.rb_l = QRadioButton(TRANSLATIONS[CURRENT_LANG]["theme_light"]); self.rb_l.setChecked(True)
        self.rb_d = QRadioButton(TRANSLATIONS[CURRENT_LANG]["theme_dark"])
        self.bg = QButtonGroup(); self.bg.addButton(self.rb_l); self.bg.addButton(self.rb_d)
        h3 = QHBoxLayout(); h3.addWidget(self.l_th); h3.addStretch(); h3.addWidget(self.rb_l); h3.addWidget(self.rb_d)
        cl.addLayout(h3)

        l.addWidget(card)

        self.btn = QPushButton(TRANSLATIONS[CURRENT_LANG]["btn_apply"])
        self.btn.setStyleSheet("background-color: #2563EB; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold;")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self.apply)
        hb = QHBoxLayout(); hb.addStretch(); hb.addWidget(self.btn); hb.addStretch()
        l.addLayout(hb); l.addStretch()

    def apply(self):
        font = QApplication.font(); font.setPointSize(self.sl_z.value()); QApplication.setFont(font)
        global CURRENT_LANG; CURRENT_LANG = "ES" if self.cb_la.currentIndex() == 0 else "EN"
        self.main.set_theme(self.rb_d.isChecked())
        self.main.refresh_ui()
        QMessageBox.information(self, "OK", "Configuración Aplicada")

    def refresh(self):
        self.tit.setText(TRANSLATIONS[CURRENT_LANG]["settings_title"])
        self.l_z.setText(TRANSLATIONS[CURRENT_LANG]["lbl_zoom"])
        self.l_la.setText(TRANSLATIONS[CURRENT_LANG]["lbl_lang"])
        self.l_th.setText(TRANSLATIONS[CURRENT_LANG]["lbl_theme"])
        self.rb_l.setText(TRANSLATIONS[CURRENT_LANG]["theme_light"])
        self.rb_d.setText(TRANSLATIONS[CURRENT_LANG]["theme_dark"])
        self.btn.setText(TRANSLATIONS[CURRENT_LANG]["btn_apply"])

class DevelopersPage(QWidget):
    def __init__(self):
        super().__init__()
        l = QVBoxLayout(self); l.setContentsMargins(0,0,0,0)
        top = QWidget(); tl = QVBoxLayout(top); tl.setSpacing(10); tl.setContentsMargins(0,60,0,40)
        self.t = QLabel(TRANSLATIONS[CURRENT_LANG]["devs_title"]); self.t.setProperty("class", "SectionTitle"); self.t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.s = QLabel(TRANSLATIONS[CURRENT_LANG]["devs_sub"]); self.s.setStyleSheet("color: #6B7280; font-size: 16px;")
        self.s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tl.addWidget(self.t); tl.addWidget(self.s); l.addWidget(top)

        g = QWidget(); gl = QGridLayout(g); gl.setSpacing(30); gl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        def mk_card(n, r, c):
            f = QFrame(); f.setFixedSize(220, 140)
            f.setProperty("class", "Card")
            f.setStyleSheet(f"border-top: 4px solid {c};") 
            v = QVBoxLayout(f); v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nm = QLabel(n); nm.setProperty("class", "CardTitle")
            rl = QLabel(r); rl.setProperty("class", "CardDesc")
            v.addWidget(nm); v.addWidget(rl)
            return f

        devs = [("Jorge Cubillo", "Líder & Backend", "#2563EB"), ("Ervin Perez", "UI/UX Design", "#F59E0B"),
                ("Isaac Mora", "Lógica Matemática", "#10B981"), ("Diego Luquez", "QA & Testing", "#8B5CF6")]
        pos = [(0,0), (0,1), (1,0), (1,1)]
        for (n,r,c), p in zip(devs, pos): gl.addWidget(mk_card(n,r,c), *p)
        l.addWidget(g); l.addStretch()

    def refresh(self):
        self.t.setText(TRANSLATIONS[CURRENT_LANG]["devs_title"])
        self.s.setText(TRANSLATIONS[CURRENT_LANG]["devs_sub"])

# =============================================================================
#  MAIN WINDOW
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathPro - Ultimate Suite")
        self.resize(1280, 850)

        self.central = QWidget(); self.setCentralWidget(self.central)
        self.central.setObjectName("MainContainer")
        self.layout = QVBoxLayout(self.central); self.layout.setContentsMargins(0,0,0,0); self.layout.setSpacing(0)

        self._init_header()
        
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.p_dash = DashboardPage(self)
        self.p_mod = QWidget(); self.ml = QVBoxLayout(self.p_mod); self.ml.setContentsMargins(0,0,0,0)
        self.p_set = SettingsPage(self)
        self.p_dev = DevelopersPage()

        self.stack.addWidget(self.p_dash)
        self.stack.addWidget(self.p_mod)
        self.stack.addWidget(self.p_set)
        self.stack.addWidget(self.p_dev)

        self.set_theme(False)

    def _init_header(self):
        h = QFrame(); h.setObjectName("Header"); h.setFixedHeight(85)
        hl = QHBoxLayout(h); hl.setContentsMargins(30,0,30,0); hl.setSpacing(15)

        logo_c = QWidget(); lc = QHBoxLayout(logo_c); lc.setContentsMargins(0,0,0,0); lc.setSpacing(10)
        bar = QLabel(); bar.setFixedSize(6, 35); bar.setObjectName("LogoBar")
        txt = QPushButton("MATHPRO"); txt.setObjectName("LogoText"); txt.setFlat(True); txt.setCursor(Qt.CursorShape.PointingHandCursor)
        txt.clicked.connect(lambda: self.switch_page(0))
        lc.addWidget(bar); lc.addWidget(txt)
        hl.addWidget(logo_c); hl.addStretch()

        self.yt_i = QLineEdit(); self.yt_i.setPlaceholderText(TRANSLATIONS[CURRENT_LANG]["search_ph"])
        self.yt_i.setObjectName("YoutubeInput"); self.yt_i.setFixedSize(650, 42)
        self.yt_i.returnPressed.connect(self.search)
        self.yt_b = QPushButton("▶"); self.yt_b.setObjectName("YoutubeBtn"); self.yt_b.setFixedSize(45, 42)
        self.yt_b.setCursor(Qt.CursorShape.PointingHandCursor); self.yt_b.clicked.connect(self.search)
        hl.addWidget(self.yt_i); hl.addWidget(self.yt_b); hl.addStretch()

        self.btn_b = QPushButton(TRANSLATIONS[CURRENT_LANG]["btn_back"]); self.btn_b.setObjectName("BackBtn")
        self.btn_b.setFixedHeight(42)
        self.btn_b.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_b.setVisible(False)
        self.btn_b.clicked.connect(lambda: self.switch_page(0))
        hl.addWidget(self.btn_b)

        self.layout.addWidget(h)

    def switch_page(self, idx, mod_key=None):
        if idx == 1 and mod_key: self.load_module(mod_key)
        self.stack.setCurrentIndex(idx)
        self.btn_b.setVisible(idx != 0)

    def load_module(self, key):
        if self.ml.count(): 
            widget = self.ml.takeAt(0).widget()
            if widget: widget.deleteLater()

        C = MODULES.get(key)
        if C:
            try:
                w = C()
                if isinstance(w, QMainWindow):
                    w.setWindowFlags(Qt.WindowType.Widget)
                    cw = QWidget(); cv = QVBoxLayout(cw); cv.setContentsMargins(0,0,0,0); cv.addWidget(w)
                    self.ml.addWidget(cw)
                else:
                    self.ml.addWidget(w)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar '{key}':\n{str(e)}")
        else:
            QMessageBox.warning(self, "No Encontrado", f"Módulo '{key}' no encontrado.")

    def search(self):
        if self.yt_i.text(): YoutubeViewer(self.yt_i.text(), self).exec()

    def set_theme(self, is_dark):
        app = QApplication.instance()
        app.setStyleSheet(STYLES_DARK if is_dark else STYLES_LIGHT)

    def refresh_ui(self):
        self.yt_i.setPlaceholderText(TRANSLATIONS[CURRENT_LANG]["search_ph"])
        self.btn_b.setText(TRANSLATIONS[CURRENT_LANG]["btn_back"])
        self.p_dash.refresh()
        self.p_set.refresh()
        self.p_dev.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10); font.setWeight(QFont.Weight.Medium); app.setFont(font)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())