import sys, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSizePolicy, QFrame, QStackedLayout,
    QSpacerItem, QWidget as QtWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsOpacityEffect

# ====== TUS MÓDULOS EXISTENTES ======
from Logica_simbolica_inferencial import LogicaSimbolicaTeclado
from Conjuntos import CalculadoraConjuntos
from Funciones import CalculadoraFunciones
from Limites import   CalculadoraLimites
from Matrices import  VentanaMatrices
from Dependencia_lineal import VerificarIndependencia
from Determinantes import VentanaDeterminantes
from Multiplicacion_escalar import VentanaMultiplicacionEscalar
# ====================================


# ---------- ÚNICO submenú flotante reutilizable ----------
class PopMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setObjectName("PopMenu")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.card = QFrame(self)
        self.card.setObjectName("PopCard")
        self.card.setContentsMargins(0, 0, 0, 0)

        self.v = QVBoxLayout(self.card)
        self.v.setContentsMargins(10, 10, 10, 10)
        self.v.setSpacing(6)

        self.opacity = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(self.opacity)

        self.anim_op  = QPropertyAnimation(self.opacity, b"opacity", self)
        self.anim_geo = QPropertyAnimation(self.card,   b"geometry", self)
        for a in (self.anim_op, self.anim_geo):
            a.setDuration(140)
            a.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim = QParallelAnimationGroup(self)
        self.anim.addAnimation(self.anim_op)
        self.anim.addAnimation(self.anim_geo)

        self._anchor_btn = None
        self._is_open = False

    def clear(self):
        for i in reversed(range(self.v.count())):
            w = self.v.itemAt(i).widget()
            if w: w.setParent(None)

    def set_actions(self, items):
        """items: list[(texto, callback)]"""
        self.clear()
        for text, fn in items:
            b = QPushButton(text, self.card)
            b.setObjectName("MenuItem")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setMinimumHeight(34)
            # No conectamos fn directo; lo hará la clase principal para envolver en try/except
            b.clicked.connect(fn)
            self.v.addWidget(b)

    def set_anchor(self, button: QPushButton):
        self._anchor_btn = button

    def open(self):
        if not self._anchor_btn: return
        try: self.anim.finished.disconnect(self.hide)
        except TypeError: pass

        self._is_open = True
        self.show(); self.raise_(); self.card.raise_()
        self._reposition()

        start = self.card.geometry()
        self.anim.stop()
        self.opacity.setOpacity(0.0)
        self.anim_op.setStartValue(0.0); self.anim_op.setEndValue(1.0)
        self.anim_geo.setStartValue(QRect(start.x(), start.y() - 6, start.width(), start.height()))
        self.anim_geo.setEndValue(start)
        self.anim.start()

    def closeMenu(self):
        if not self._is_open: return
        self._is_open = False
        rect = self.card.geometry()
        self.anim.stop()
        self.anim_op.setStartValue(1.0); self.anim_op.setEndValue(0.0)
        self.anim_geo.setStartValue(rect)
        self.anim_geo.setEndValue(QRect(rect.x(), rect.y() - 6, rect.width(), rect.height()))
        try: self.anim.finished.disconnect(self.hide)
        except TypeError: pass
        self.anim.finished.connect(self.hide)
        self.anim.start()

    def isOpen(self): return self._is_open

    def _reposition(self):
        self.card.adjustSize()
        card_w = self.card.sizeHint().width()
        card_h = self.card.sizeHint().height()
        btn = self._anchor_btn; parent = self.parentWidget()

        g_bl = btn.mapToGlobal(btn.rect().bottomLeft())
        bl = parent.mapFromGlobal(g_bl)

        margin = 8
        x = max(margin, min(bl.x(), parent.width() - card_w - margin))
        y = max(parent.topbar.height(), min(bl.y(), parent.height() - card_h - margin))

        self.setGeometry(0, 0, parent.width(), parent.height())
        self.card.setGeometry(x, y, card_w, card_h)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.isOpen(): self._reposition()


class MenuElegante(QWidget):
    BASE_DIR = os.path.dirname(__file__)
    TOPBAR_LOGO = os.path.join(BASE_DIR, "Imagenes", "FIA.png")
    LOGO_INICIAL = os.path.join(BASE_DIR, "Imagenes", "MaThproLogo.png")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú Principal · MathPro")
        self.resize(1200, 720)

        # Paleta (tema fijo claro)
        self.colors = {
            "bg":"#F6F8FC","fg":"#0F172A","muted":"#6B7280",
            "accent1":"#0EA5E9","accent2":"#0284C7",
            "card":"#FFFFFF","border":"#E5E7EB","shadow":"rgba(15,23,42,.08)"
        }

        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Topbar
        self.topbar = QFrame(objectName="TopBar"); self.topbar.setFixedHeight(56)
        tb = QHBoxLayout(self.topbar); tb.setContentsMargins(12,6,12,6); tb.setSpacing(8)

        # Izquierda: SOLO logo
        self.logo_top = QLabel(); self.logo_top.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._set_topbar_logo(self.TOPBAR_LOGO, 36)
        tb.addWidget(self.logo_top)

        # Centro: botones centrados
        tb.addItem(QSpacerItem(24, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.center_container = QtWidget(); center = QHBoxLayout(self.center_container)
        center.setContentsMargins(0,0,0,0); center.setSpacing(6)
        center.addStretch(1)

        self.btn_inicio = self._mkTopBtn("Inicio")
        self.btn_mb     = self._mkTopBtn("Matemática Básica")
        self.btn_calc   = self._mkTopBtn("Cálculo")
        self.btn_calc2  = self._mkTopBtn("Cálculo II")
        self.btn_alg    = self._mkTopBtn("Álgebra Lineal")
        for b in (self.btn_inicio, self.btn_mb, self.btn_calc, self.btn_calc2, self.btn_alg):
            center.addWidget(b)
        center.addStretch(1)
        tb.addWidget(self.center_container, 1)

        # Derecha: Config (sin submenú ni idioma)
        tb.addItem(QSpacerItem(24, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_config = QPushButton("Configuración", objectName="ConfigBtn")
        self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_config.setMinimumHeight(36)
        tb.addWidget(self.btn_config)
        root.addWidget(self.topbar)

        # Contenido (logo grande)
        content_wrap = QFrame(objectName="Content")
        self.stack = QStackedLayout(content_wrap)
        self.logo_page = QtWidget(); lp = QVBoxLayout(self.logo_page); lp.setContentsMargins(24,24,24,24); lp.setSpacing(12)
        self.logo_label = QLabel(); self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumSize(480,320); self.logo_label.setScaledContents(True)
        lp.addStretch(1); lp.addWidget(self.logo_label); lp.addStretch(2)
        self.stack.addWidget(self.logo_page); self.set_logo(self.LOGO_INICIAL)
        root.addWidget(content_wrap, 1)

        # ===== ÚNICO SUBMENÚ =====
        self.menu = PopMenu(self)

        # Acciones por categoría
        soon = self._coming_soon
        # Nota: cada item se envuelve en _safe_action para capturar excepciones del callback
        self.actions_map = {
            "mb": [
                ("Lógica simbólica y inferencial", self._safe_action(lambda: self._open_module(LogicaSimbolicaTeclado))),
                ("Conjuntos",                       self._safe_action(lambda: self._open_module(CalculadoraConjuntos))),
                ("Funciones",                       self._safe_action(lambda: self._open_module(CalculadoraFunciones))),
            ],
            "calc": [
                ("Límites",   self._safe_action(lambda: self._open_module(CalculadoraLimites))),
                ("Derivadas", self._safe_action(soon)),  # Próximamente
            ],
            "calc2": [
                ("Integrales indefinidas", self._safe_action(soon)),
                ("Integrales definidas",   self._safe_action(soon)),
            ],
            "alg": [
                ("Vectores",                   self._safe_action(soon)),
                ("Determinantes",              self._safe_action(lambda: self._open_module(VentanaDeterminantes))),
                ("Matrices",                   self._safe_action(lambda: self._open_module(VentanaMatrices))),
                ("Multiplicación por escalar", self._safe_action(lambda: self._open_module(VentanaMultiplicacionEscalar))),
                ("Dependencias lineales",      self._safe_action(lambda: self._open_module(VerificarIndependencia))),
            ]
        }

        # Clicks
        self.btn_inicio.clicked.connect(self.show_home)
        self.btn_mb.clicked.connect(lambda: self._toggle_menu(self.btn_mb,   self.actions_map["mb"]))
        self.btn_calc.clicked.connect(lambda: self._toggle_menu(self.btn_calc, self.actions_map["calc"]))
        self.btn_calc2.clicked.connect(lambda: self._toggle_menu(self.btn_calc2, self.actions_map["calc2"]))
        self.btn_alg.clicked.connect(lambda: self._toggle_menu(self.btn_alg,  self.actions_map["alg"]))

        # Cerrar submenú al click fuera
        self.installEventFilter(self)

        self._apply_styles()

    # ====== helpers UI ======
    def _mkTopBtn(self, text: str) -> QPushButton:
        b = QPushButton(text, objectName="TopBtn")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setMinimumHeight(36)
        b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return b

    def _toggle_menu(self, anchor_btn: QPushButton, items):
        # items ya vienen envueltos en funciones seguras (no crashean)
        self.menu.set_actions(items)
        self.menu.set_anchor(anchor_btn)
        if self.menu.isOpen(): self.menu.closeMenu()
        else: self.menu.open()

    def _safe_action(self, fn):
        """Devuelve un wrapper que captuta errores del callback y los muestra en pantalla."""
        def wrapper():
            try:
                if self.menu.isOpen(): self.menu.closeMenu()
                fn()
            except Exception as e:
                self._show_error_panel(e)
        return wrapper

    def _show_error_panel(self, exc: Exception):
        # Limpia y muestra un panel de error (sin cerrar la app)
        while self.stack.count() > 1:
            old = self.stack.widget(1); self.stack.removeWidget(old); old.setParent(None)
        err = QtWidget(); lay = QVBoxLayout(err)
        title = QLabel("⚠️ Error al ejecutar la acción"); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 800; margin-bottom: 8px;")
        detail = QTextEdit(); detail.setReadOnly(True); detail.setPlainText(str(exc))
        detail.setMinimumHeight(120)
        detail.setStyleSheet("border: 1px solid rgba(0,0,0,.12); border-radius: 8px; padding: 8px;")
        lay.addStretch(1); lay.addWidget(title); lay.addWidget(detail); lay.addStretch(2)
        self.stack.addWidget(err); self.stack.setCurrentIndex(1)
        self._apply_content_style(err)

    def eventFilter(self, obj, event):
        from PyQt6.QtGui import QMouseEvent
        if isinstance(event, QMouseEvent) and event.type() == QMouseEvent.Type.MouseButtonPress:
            if self.menu.isOpen():
                pos = event.globalPosition().toPoint()
                if not self.menu.card.geometry().contains(self.menu.mapFromGlobal(pos)):
                    self.menu.closeMenu()
        return False

    # ====== navegación segura ======
    def _open_module(self, WidgetClass):
        """Instancia segura: si algo falla, mostramos panel de error y NO crashea."""
        # Limpia el contenido actual
        while self.stack.count() > 1:
            old = self.stack.widget(1); self.stack.removeWidget(old); old.setParent(None)
        try:
            widget = None
            if isinstance(WidgetClass, type):
                widget = WidgetClass()
            elif callable(WidgetClass):
                widget = WidgetClass()
            else:
                widget = WidgetClass
            if not isinstance(widget, QWidget):
                raise TypeError(f"El módulo no devolvió un QWidget: {type(widget).__name__}")
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.stack.addWidget(widget); self.stack.setCurrentIndex(1)
            self._apply_content_style(widget)
        except Exception as e:
            self._show_error_panel(e)

    def _coming_soon(self):
        w = QtWidget(); lay = QVBoxLayout(w)
        lbl = QLabel("Módulo próximamente disponible…"); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        lay.addStretch(1); lay.addWidget(lbl); lay.addStretch(2)
        # Render por ruta segura
        self._open_module(lambda: w)

    def show_home(self):
        if self.menu.isOpen(): self.menu.closeMenu()
        while self.stack.count() > 1:
            old = self.stack.widget(1); self.stack.removeWidget(old); old.setParent(None)
        self.stack.setCurrentIndex(0)

    # ====== logo ======
    def _set_topbar_logo(self, path: str, height: int):
        pix = QPixmap(path)
        if pix.isNull():
            self.logo_top.clear(); self.logo_top.setFixedWidth(0); self.logo_top.setFixedHeight(height); self.logo_top.hide()
        else:
            scaled = pix.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
            self.logo_top.setPixmap(scaled); self.logo_top.setFixedHeight(height); self.logo_top.setFixedWidth(scaled.width()); self.logo_top.show()

    def set_logo(self, path: str):
        pix = QPixmap(path)
        if pix.isNull():
            self.logo_label.setText("#MATHPRO")
            self.logo_label.setStyleSheet("font: 900 48px 'Inter'; opacity:.15;")
        else:
            self.logo_label.setPixmap(pix)

    # ====== estilos ======
    def _apply_styles(self):
        pal = self.colors
        self.setStyleSheet(f"background:{pal['bg']}; color:{pal['fg']};")
        self.topbar.setStyleSheet(f"#TopBar{{background:{pal['card']}; border-bottom:1px solid {pal['border']};}}")
        self.topbar.setStyleSheet(
            self.topbar.styleSheet() +
            f"QPushButton#TopBtn{{background:transparent; border:none; padding:8px 10px; border-radius:8px; font-weight:700; color:{pal['fg']};}}"
            f"QPushButton#TopBtn:hover{{background:transparent;}}"
            f"QPushButton#TopBtn:pressed{{background:transparent;}}"
            f"QPushButton#TopBtn:focus{{outline:none;}}"
            f"QPushButton#ConfigBtn{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {pal['accent1']}, stop:1 {pal['accent2']});"
            f"color:#fff; font-weight:800; border-radius:10px; padding:8px 12px;}}"
            f"QPushButton#ConfigBtn:hover{{filter:brightness(1.06);}}"
        )
        pop_css = (
            f"#PopMenu{{background:transparent;}}"
            f"#PopCard{{background:{pal['card']}; border:1px solid {pal['border']}; border-radius:12px; "
            f"box-shadow: 0 10px 26px {pal['shadow']};}}"
            f"QPushButton#MenuItem{{background:transparent; border:none; text-align:left; padding:8px 10px; "
            f"border-radius:8px; color:{pal['fg']}; font-weight:600;}}"
            f"QPushButton#MenuItem:hover{{background:{pal['border']};}}"
        )
        self.menu.setStyleSheet(pop_css)

    def _apply_content_style(self, w: QtWidget):
        pal = self.colors
        w.setStyleSheet(f"background:{pal['bg']}; color:{pal['fg']};")
