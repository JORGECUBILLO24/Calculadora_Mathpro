# -*- coding: utf-8 -*-
import os, sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy,
    QFrame, QStackedLayout, QSpacerItem, QWidget as QtWidget, QTextEdit,
    QGraphicsOpacityEffect, QMenu
)
from PyQt6.QtCore import (
    Qt, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup,
    QAbstractAnimation, pyqtProperty, pyqtSignal, QTimer
)
# 👉 En PyQt6, QAction está en QtGui (NO en QtWidgets)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QAction


# ====== TUS MÓDULOS EXISTENTES ======
from Matrices import  VentanaMatrices
from Dependencia_lineal import VerificarIndependencia
from Determinantes import VentanaDeterminantes
from Multiplicacion_escalar import VentanaMultiplicacionEscalar
from Método_de_Biseccion import VentanaBiseccion
from Metodo_falsa_posicion import VentanaFalsaPosicion
from metodo_rhapson import VentanaNewtonRaphson
from secante import VentanaSecante
# ====================================


# ----------------- Botón con efecto Ripple (suave) -----------------
class RippleButton(QPushButton):
    rippleStarted = pyqtSignal()

    def __init__(self, text="", parent=None, ripple_color=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._ripple_color = ripple_color or QColor(96, 165, 250, 110)
        self._ripple_center = None
        self._progress = 0.0

        self._anim = QPropertyAnimation(self, b"rippleProgress", self)
        self._anim.setDuration(360)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def setRippleColor(self, c: QColor):
        self._ripple_color = c
        self.update()

    def mousePressEvent(self, e):
        self._ripple_center = e.position()
        self._anim.stop()
        self.rippleProgress = 0.0
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self.rippleStarted.emit()
        super().mousePressEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        if self._progress <= 0.0 or self._ripple_center is None:
            return
        w, h = self.width(), self.height()
        max_r = (w*w + h*h) ** 0.5
        r = max(0.0, min(1.0, self._progress)) * max_r
        alpha = max(0.0, 1.0 - self._progress)
        col = QColor(self._ripple_color)
        col.setAlphaF(0.22 * alpha)

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(col))
        center = self._ripple_center.toPoint()
        p.drawEllipse(center, int(r), int(r))
        p.end()

    @pyqtProperty(float)
    def rippleProgress(self):
        return self._progress

    @rippleProgress.setter
    def rippleProgress(self, v: float):
        self._progress = v
        self.update()


# =================== Ventana principal ===================
class MenuElegante(QWidget):
    BASE_DIR = os.path.dirname(__file__)
    TOPBAR_LOGO = os.path.join(BASE_DIR, "Imagenes", "FIA.png")
    LOGO_INICIAL = os.path.join(BASE_DIR, "Imagenes", "MaThproLogo.png")

    # Paletas: claro / gris elegante (NO se persiste)
    THEMES = {
        "light": {
            "bg": "#F6F8FC", "fg": "#0F172A", "muted": "#6B7280",
            "accent1": "#60A5FA", "accent2": "#3B82F6",
            "card": "#FFFFFF", "border": "#E5E7EB",
            "ripple": QColor(96, 165, 250, 120)
        },
        "gray": {  # gris elegante (no negro)
            "bg": "#2A2F36", "fg": "#E7EAF0", "muted": "#AAB2BF",
            "accent1": "#A1A1AA", "accent2": "#6B7280",
            "card": "#323844", "border": "rgba(255,255,255,.08)",
            "ripple": QColor(161, 161, 170, 150)
        }
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú Principal · MathPro")
        self.resize(1200, 720)

        self.theme_name = "light"

        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # Topbar (sin sombras, solo borde inferior)
        self.topbar = QFrame(); self.topbar.setObjectName("TopBar"); self.topbar.setFixedHeight(60)
        tb = QHBoxLayout(self.topbar); tb.setContentsMargins(14, 8, 14, 8); tb.setSpacing(10)

        # Izquierda: logo
        self.logo_top = QLabel(); self.logo_top.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._set_topbar_logo(self.TOPBAR_LOGO, 36)
        tb.addWidget(self.logo_top)

        # Centro: botones navegación
        tb.addItem(QSpacerItem(24, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.center_container = QtWidget()
        center = QHBoxLayout(self.center_container)
        center.setContentsMargins(0, 0, 0, 0); center.setSpacing(8)
        center.addStretch(1)

        self.btn_inicio = self._mkTopBtn("Inicio")
        self.btn_anum   = self._mkTopBtn("Análisis numérico")
        self.btn_alg    = self._mkTopBtn("Operaciones con matrices")
        for b in (self.btn_inicio, self.btn_anum, self.btn_alg):
            center.addWidget(b)
        center.addStretch(1)
        tb.addWidget(self.center_container, 1)

        # Derecha: Tema gris + Config
        tb.addItem(QSpacerItem(24, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_theme = RippleButton("☾  Modo gris"); self.btn_theme.setObjectName("ThemeBtn")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_theme.setMinimumHeight(36)
        self.btn_theme.clicked.connect(self.toggle_theme)
        tb.addWidget(self.btn_theme)

        self.btn_config = RippleButton("Configuración"); self.btn_config.setObjectName("ConfigBtn")
        self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_config.setMinimumHeight(36)
        tb.addWidget(self.btn_config)

        root.addWidget(self.topbar)

        # Contenido
        content_wrap = QFrame(); content_wrap.setObjectName("Content")
        self.stack = QStackedLayout(content_wrap)
        self.logo_page = QtWidget()
        lp = QVBoxLayout(self.logo_page); lp.setContentsMargins(24, 24, 24, 24); lp.setSpacing(12)
        self.logo_label = QLabel(); self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumSize(480, 320); self.logo_label.setScaledContents(True)
        lp.addStretch(1); lp.addWidget(self.logo_label); lp.addStretch(2)
        self.stack.addWidget(self.logo_page)
        self.set_logo(self.LOGO_INICIAL)
        root.addWidget(content_wrap, 1)

        # ===== MENÚS DESPLEGABLES (QMenu) =====
        self._build_menus()

        # Acciones de los botones: abrir menú con popup (siempre abre)
        self.btn_inicio.clicked.connect(self.show_home)
        self.btn_anum.clicked.connect(lambda: self._show_menu(self.btn_anum, self.menu_anum))
        self.btn_alg.clicked.connect(lambda: self._show_menu(self.btn_alg,  self.menu_alg))

        # Tema inicial
        self._apply_theme(self.theme_name)

    # ---------- Menús ----------
    def _build_menus(self):
        # Análisis numérico
        self.menu_anum = QMenu(self)
        self._style_menu(self.menu_anum)

        act_bis = QAction("Método de bisección", self.menu_anum)
        act_bis.triggered.connect(self._safe_action(lambda: self._open_module(VentanaBiseccion)))
        self.menu_anum.addAction(act_bis)
        
        act_fals = QAction("Método de falsa posición", self.menu_anum)
        act_fals.triggered.connect(self._safe_action(lambda: self._open_module(VentanaFalsaPosicion)))
        self.menu_anum.addAction(act_fals)

        act_newton = QAction("Método de Newton–Raphson", self.menu_anum)
        act_newton.triggered.connect(self._safe_action(lambda: self._open_module(VentanaNewtonRaphson)))
        self.menu_anum.addAction(act_newton)

        act_sec = QAction("Método de la secante", self.menu_anum)
        act_sec.triggered.connect(self._safe_action(lambda: self._open_module(VentanaSecante)))
        self.menu_anum.addAction(act_sec)

        # Operaciones con matrices (álgebra lineal)
        self.menu_alg = QMenu(self)
        self._style_menu(self.menu_alg)

        act_det = QAction("Determinantes", self.menu_alg)
        act_mat = QAction("Matrices", self.menu_alg)
        act_esc = QAction("Multiplicación por escalar", self.menu_alg)
        act_dep = QAction("Dependencias lineales", self.menu_alg)

        act_det.triggered.connect(self._safe_action(lambda: self._open_module(VentanaDeterminantes)))
        act_mat.triggered.connect(self._safe_action(lambda: self._open_module(VentanaMatrices)))
        act_esc.triggered.connect(self._safe_action(lambda: self._open_module(VentanaMultiplicacionEscalar)))
        act_dep.triggered.connect(self._safe_action(lambda: self._open_module(VerificarIndependencia)))

        self.menu_alg.addAction(act_det)
        self.menu_alg.addAction(act_mat)
        self.menu_alg.addAction(act_esc)
        self.menu_alg.addAction(act_dep)

    def _show_menu(self, btn: QPushButton, menu: QMenu):
        # Apertura diferida para evitar rebotes del mismo click
        QTimer.singleShot(0, lambda: menu.popup(btn.mapToGlobal(btn.rect().bottomLeft())))

    def _style_menu(self, menu: QMenu):
        pal = self.THEMES[getattr(self, "theme_name", "light")]
        menu.setStyleSheet(f"""
            QMenu {{
                background: {pal['card']};
                border: 1px solid {pal['border']};
                border-radius: 10px;
                padding: 6px 0px;
            }}
            QMenu::item {{
                padding: 8px 14px;
                color: {pal['fg']};
                background: transparent;
                font-weight: 600;
            }}
            QMenu::item:selected {{
                background: {self._alpha(pal['fg'], .08)};
            }}
            QMenu::separator {{
                height: 1px;
                background: {pal['border']};
                margin: 6px 8px;
            }}
        """)

    # ---------- helpers UI ----------
    def _mkTopBtn(self, text: str) -> RippleButton:
        b = RippleButton(text)
        b.setObjectName("TopBtn")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setMinimumHeight(38)
        b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return b

    def _safe_action(self, fn):
        def wrapper():
            try:
                fn()
            except Exception as e:
                self._show_error_panel(e)
        return wrapper

    def _show_error_panel(self, exc: Exception):
        self._clear_content()
        err = QtWidget(); lay = QVBoxLayout(err)
        title = QLabel("⚠️ Error al ejecutar la acción"); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("ErrorTitle")
        detail = QTextEdit(); detail.setReadOnly(True); detail.setPlainText(str(exc))
        detail.setMinimumHeight(140)
        detail.setObjectName("ErrorDetail")
        lay.addStretch(1); lay.addWidget(title); lay.addWidget(detail); lay.addStretch(2)
        self.stack.addWidget(err); self.stack.setCurrentIndex(1)
        self._apply_content_style(err)

    def _clear_content(self):
        while self.stack.count() > 1:
            old = self.stack.widget(1); self.stack.removeWidget(old); old.setParent(None)

    # ---------- navegación + animación ----------
    def _open_module(self, WidgetClass):
        self._clear_content()
        widget = WidgetClass() if isinstance(WidgetClass, type) else WidgetClass
        if not isinstance(widget, QWidget):
            raise TypeError(f"El módulo no devolvió un QWidget: {type(widget).__name__}")
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._transition_to(widget)

    def _transition_to(self, widget: QWidget):
        self.stack.addWidget(widget); self.stack.setCurrentIndex(1)
        self._apply_content_style(widget)
        eff = QGraphicsOpacityEffect(widget); widget.setGraphicsEffect(eff)
        anim_op = QPropertyAnimation(eff, b"opacity", widget)
        anim_op.setDuration(200)
        anim_op.setStartValue(0.0); anim_op.setEndValue(1.0)
        anim_op.setEasingCurve(QEasingCurve.Type.OutCubic)
        group = QParallelAnimationGroup(widget); group.addAnimation(anim_op)
        group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def show_home(self):
        self._clear_content()
        self.stack.setCurrentIndex(0)

    # ---------- tema (NO persistente) ----------
    def toggle_theme(self):
        self.theme_name = "gray" if self.theme_name == "light" else "light"
        self._apply_theme(self.theme_name)

    def _apply_theme(self, name: str):
        pal = self.THEMES[name]
        # Fondo y texto general
        self.setStyleSheet(f"background:{pal['bg']}; color:{pal['fg']};")

        # Actualiza ripple según tema
        for btn in self.findChildren(RippleButton):
            btn.setRippleColor(pal['ripple'])

        # Topbar y botones
        self.topbar.setStyleSheet(
            f"""
            #TopBar {{
                background:{pal['card']};
                border-bottom:1px solid {pal['border']};
            }}
            RippleButton#TopBtn {{
                background: transparent;
                border: none;
                padding: 8px 12px;
                border-radius: 10px;
                font-weight: 700;
                color:{pal['fg']};
            }}
            RippleButton#TopBtn:hover {{
                background: {self._alpha(pal['fg'], .06)};
            }}
            RippleButton#TopBtn:pressed {{
                background: {self._alpha(pal['fg'], .12)};
            }}
            RippleButton#ThemeBtn, RippleButton#ConfigBtn {{
                color:#fff; font-weight:800; border-radius: 12px; padding: 8px 14px;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {pal['accent1']}, stop:1 {pal['accent2']});
                border: none;
            }}
            RippleButton#ThemeBtn:hover, RippleButton#ConfigBtn:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {pal['accent2']}, stop:1 {pal['accent1']});
            }}
            """
        )
        self.btn_theme.setText("☀  Volver a claro" if name == "gray" else "☾  Modo gris")

        # Restyle menus al cambiar tema
        self._style_menu(self.menu_anum)
        self._style_menu(self.menu_alg)

        # Error panel
        self.setStyleSheet(self.styleSheet() + f"""
            #ErrorTitle {{
                font-size: 18px; font-weight: 800; margin-bottom: 8px; color:{pal['fg']};
            }}
            #ErrorDetail {{
                border: 1px solid {pal['border']};
                border-radius: 10px; padding: 10px;
                background: {pal['card']};
                color:{pal['fg']};
            }}
        """)

        self.set_logo(self.LOGO_INICIAL)

    def _alpha(self, hex_or_rgba: str, a: float) -> str:
        if hex_or_rgba.startswith("#") and len(hex_or_rgba) == 7:
            r = int(hex_or_rgba[1:3], 16)
            g = int(hex_or_rgba[3:5], 16)
            b = int(hex_or_rgba[5:7], 16)
            return f"rgba({r},{g},{b},{a})"
        if hex_or_rgba.startswith("rgba"):
            pre = hex_or_rgba.split(")")[0]
            parts = pre.split("(")[1].split(",")
            if len(parts) == 4:
                parts[-1] = f"{a}"
                return "rgba(" + ",".join(parts) + ")"
        return f"rgba(0,0,0,{a})"

    # ---------- logo ----------
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
            self.logo_label.setText("MATHPRO")
            self.logo_label.setStyleSheet("font: 900 48px 'Inter', 'Segoe UI', sans-serif; opacity:.15;")
        else:
            self.logo_label.setPixmap(pix)

    def _apply_content_style(self, w: QtWidget):
        pal = self.THEMES[self.theme_name]
        w.setStyleSheet(f"background:{pal['bg']}; color:{pal['fg']};")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MenuElegante()
    win.show()
    sys.exit(app.exec())
