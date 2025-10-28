import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMenu, QSizePolicy,
    QFrame, QStackedLayout, QSpacerItem, QSizePolicy as QSzPolicy,
    QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QPixmap

# ---- Importa tus módulos existentes ----
from Logica_simbolica_inferencial import LogicaSimbolicaTeclado
from Conjuntos import CalculadoraConjuntos
from Funciones import CalculadoraFunciones
from Limites import CalculadoraLimites
from Matrices import VentanaMatrices
from Dependencia_lineal import VerificarIndependencia
from Determinantes import VentanaDeterminantes
from Multiplicacion_escalar import VentanaMultiplicacionEscalar


class MenuElegante(QWidget):
  
    # ================== 🔧 ZONA DE CONFIGURACIÓN RÁPIDA ==================
    # (1) RUTAS DE IMAGEN (relativas al directorio del proyecto)
    BASE_DIR = os.path.dirname(__file__)
    TOPBAR_LOGO = os.path.join(BASE_DIR, "Imagenes", "FIA.png")  # ← logo largo (barra superior)
    LOGO_INICIAL = os.path.join(BASE_DIR, "Imagenes", "MaThproLogo.png")  # ← logo central de inicio

    IMG_VIDEOS   = os.path.join(BASE_DIR, "Imagenes", "Videos.png")
    IMG_UAM      = os.path.join(BASE_DIR, "Imagenes", "uam.jpg")
    IMG_BARCA    = os.path.join(BASE_DIR, "Imagenes", "Barca.jpg")

    # (2) TAMAÑOS POR DEFECTO
    TOPBAR_LOGO_HEIGHT = 36          # altura del logo largo en la barra superior
    IMG_ROW_HEIGHT_DEFAULT = 85    # alto del contenedor de cada imagen del menú (igual a botón)
    IMG_PIX_HEIGHT_DEFAULT = 79    # alto al que se escala la imagen (mantiene proporción)
    # =====================================================================

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú Principal · MathPro")
        self.resize(1200, 720)
        self.tema = "claro"
        self.idioma = "Español"
        self.logo_path = None

        # Variables RUNTIME (cambiables en vivo desde Configuración)
        self.img_row_height = self.IMG_ROW_HEIGHT_DEFAULT
        self.img_pix_height = self.IMG_PIX_HEIGHT_DEFAULT

        # Paleta de colores
        self.colors = {
            "claro": {"bg": "#F5F7FB","fg": "#0F172A","accent1": "#00A8CC","accent2": "#007B8A","card": "#FFFFFF","border": "#D7DFE9"},
            "oscuro": {"bg": "#0F172A","fg": "#E5E7EB","accent1": "#22D3EE","accent2": "#0891B2","card": "#111827","border": "#374151"}
        }

        # ------------------- Layout raíz -------------------
        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(0, 0, 0, 0)
        self.layout_root.setSpacing(0)

        # ============= Barra superior (con logo largo) =============
        self.topbar = QFrame()
        self.topbar.setObjectName("TopBar")
        self.topbar.setFixedHeight(56)
        self.topbar_layout = QHBoxLayout(self.topbar)
        self.topbar_layout.setContentsMargins(16, 8, 16, 8)
        self.topbar_layout.setSpacing(12)

        # Logo largo (reemplaza el texto "MathPro")
        self.logo_top = QLabel()
        self.logo_top.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._set_topbar_logo(self.TOPBAR_LOGO, self.TOPBAR_LOGO_HEIGHT)

        self.topbar_spacer = QSpacerItem(40, 20, QSzPolicy.Policy.Expanding, QSzPolicy.Policy.Minimum)

        self.btn_config = QPushButton("⚙️  Configuración")
        self.btn_config.setObjectName("PrimaryBtn")
        self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_config.setMinimumHeight(40)
        self._attach_config_menu()

        self.topbar_layout.addWidget(self.logo_top)
        self.topbar_layout.addItem(self.topbar_spacer)
        self.topbar_layout.addWidget(self.btn_config)

        # ============= Contenedor principal =============
        self.main_frame = QFrame()
        self.main_layout = QHBoxLayout(self.main_frame)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Barra de navegación
        self.navbar = QFrame()
        self.navbar.setObjectName("NavBar")
        self.nav_layout = QVBoxLayout(self.navbar)
        self.nav_layout.setContentsMargins(8, 8, 8, 8)
        self.nav_layout.setSpacing(8)

        # Botones principales
        self.sections = [
            ("📘  Matemática Básica", [
                ("Logica simbolica y inferencial", self.mostrar_logica),
                ("Conjuntos", self.mostrar_conjuntos),
                ("Funciones", self.mostrar_funciones)
            ]),
            ("📗  Cálculo", [
                ("Límites", self.mostrar_limites),
                ("Derivadas", self._por_ahora_no_disponible)
            ]),
            ("📙  Cálculo II", [
                ("Integrales indefinidas", self._por_ahora_no_disponible),
                ("Integrales definidas", self._por_ahora_no_disponible)
            ]),
            ("📐  Álgebra Lineal", [
                ("Vectores", self._por_ahora_no_disponible),
                ("Determinantes", self.mostrar_determinantes),
                ("Matrices", self.mostrar_matrices),
                ("Multiplicacion por escalar", self.mostrar_multiplicacion_escalar),
                ("Dependencias lineales", self.mostrar_dependencias)
            ]),
        ]
        self._build_nav_buttons()

        # Área de contenido
        self.content_container = QFrame()
        self.content_container.setObjectName("Content")
        self.content_layout = QStackedLayout(self.content_container)

        # Página inicial (logo centrado)
        self.logo_page = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_page)
        self.logo_layout.setContentsMargins(24, 24, 24, 24)
        self.logo_layout.setSpacing(12)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("Logo")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumSize(400, 300)
        self.logo_label.setScaledContents(True)

        self.logo_layout.addStretch(1)
        self.logo_layout.addWidget(self.logo_label)
        self.logo_layout.addStretch(2)

        self.content_layout.addWidget(self.logo_page)

        # Logo por defecto en inicio
        self.set_logo(self.LOGO_INICIAL)

        # Ensamblar layouts
        self.main_layout.addWidget(self.navbar, 0)
        self.main_layout.addWidget(self.content_container, 1)
        self.layout_root.addWidget(self.topbar)
        self.layout_root.addWidget(self.main_frame)

        # Aplicar tema
        self._apply_theme()

    # ============= Utilidad: coloca logo en la barra superior =============
    def _set_topbar_logo(self, path: str, height: int):
        pix = QPixmap(path)
        if pix.isNull():
            print(f"[MenuPrincipal] Logo no encontrado en ruta: {path}")
            self.logo_top.setText("Logo no encontrado")
            return
        scaled = pix.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
        self.logo_top.setPixmap(scaled)
        self.logo_top.setFixedHeight(height)

    # ------------------- Construcción de navegación -------------------
    def _build_nav_buttons(self):
        # Limpieza
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            if w := item.widget():
                w.setParent(None)

        # Botón Inicio
        btn_home = QPushButton("🏠  Inicio")
        btn_home.setObjectName("NavBtn")
        btn_home.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_home.setMinimumHeight(44)
        btn_home.setSizePolicy(QSizePolicy.Policy.Expanding, QSzPolicy.Policy.Fixed)
        btn_home.clicked.connect(self.show_home)
        self.nav_layout.addWidget(btn_home)

        # Botones con menús
        for title, actions in self.sections:
            btn = QPushButton(title)
            btn.setObjectName("NavBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(44)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSzPolicy.Policy.Fixed)
            menu = QMenu(btn)
            menu.setObjectName("NavMenu")
            for text, slot in actions:
                act = menu.addAction(text)
                act.triggered.connect(slot)
            btn.setMenu(menu)
            self.nav_layout.addWidget(btn)

        # ------ Bloque de 3 imágenes (entre botones y reloj) ------
        self._img_labels = []  # guardaremos (label, path) para reescalar luego

        self.nav_images_frame = QFrame()
        imgs_layout = QVBoxLayout(self.nav_images_frame)
        imgs_layout.setContentsMargins(0, 6, 0, 6)
        imgs_layout.setSpacing(8)

        def make_img_label(path: str) -> QLabel:
            lbl = QLabel()
            lbl.setFixedHeight(self.img_row_height)  # alto de la fila (igual a botón)
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSzPolicy.Policy.Fixed)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("border-radius: 6px; background: transparent;")
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaledToHeight(self.img_pix_height, Qt.TransformationMode.SmoothTransformation)
                lbl.setPixmap(scaled)
            else:
                print(f"[MenuPrincipal] Imagen no encontrada: {path}")
                lbl.setText("Imagen no encontrada")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._img_labels.append((lbl, path))
            return lbl

        # Orden: UAM (arriba), Barcelona (medio), Videos (abajo)
        self.img_uam = make_img_label(self.IMG_UAM)
        self.img_barca = make_img_label(self.IMG_BARCA)
        self.img_videos = make_img_label(self.IMG_VIDEOS)

        imgs_layout.addWidget(self.img_uam)
        imgs_layout.addWidget(self.img_barca)
        imgs_layout.addWidget(self.img_videos)
        self.nav_layout.addWidget(self.nav_images_frame)

        # Stretch para empujar el reloj al fondo
        self.nav_layout.addStretch(1)

        # ---- Reloj al fondo ----
        self.clock_frame = QFrame()
        clock_layout = QVBoxLayout(self.clock_frame)
        clock_layout.setContentsMargins(8, 12, 8, 8)
        clock_layout.setSpacing(2)
        self.clock_title = QLabel("Hora")
        self.clock_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_value = QLabel(QTime.currentTime().toString("hh:mm:ss AP"))
        self.clock_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clock_layout.addWidget(self.clock_title)
        clock_layout.addWidget(self.clock_value)
        self.nav_layout.addWidget(self.clock_frame)

        # Timer del reloj
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._tick_clock)
        self._clock_timer.start(1000)

    def _tick_clock(self):
        self.clock_value.setText(QTime.currentTime().toString("hh:mm:ss AP"))

    def _attach_config_menu(self):
        menu = QMenu(self.btn_config)
        menu.addAction("Cambiar idioma", self.toggle_idioma)
        menu.addAction("Cambiar tema", self.toggle_tema)
        menu.addSeparator()
        menu.addAction("Ajustar tamaños de imágenes…", self.ajustar_tamano_imagenes)
        self.btn_config.setMenu(menu)

    # ------------------- Ajuste de tamaños de imágenes -------------------
    def ajustar_tamano_imagenes(self):
        """Diálogo para modificar alturas de fila e imagen con números."""
        row_h, ok1 = QInputDialog.getInt(
            self, "Tamaño de fila", "Alto de cada fila (px):",
            value=self.img_row_height, min=24, max=256, step=2
        )
        if not ok1:
            return
        pix_h, ok2 = QInputDialog.getInt(
            self, "Tamaño de imagen", "Alto de la imagen (px):",
            value=self.img_pix_height, min=16, max=row_h, step=2
        )
        if not ok2:
            return

        self.img_row_height = row_h
        self.img_pix_height = pix_h
        self._apply_image_sizes()

    def _apply_image_sizes(self):
        """Reaplica alto de fila y escala de pixmap según self.img_row_height / self.img_pix_height."""
        for lbl, path in getattr(self, "_img_labels", []):
            lbl.setFixedHeight(self.img_row_height)
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaledToHeight(self.img_pix_height, Qt.TransformationMode.SmoothTransformation)
                lbl.setPixmap(scaled)

    # ------------------- Acciones de menú -------------------
    def mostrar_logica(self): self._set_central_widget(LogicaSimbolicaTeclado())
    def mostrar_conjuntos(self): self._set_central_widget(CalculadoraConjuntos())
    def mostrar_funciones(self): self._set_central_widget(CalculadoraFunciones())
    def mostrar_limites(self): self._set_central_widget(CalculadoraLimites())
    def mostrar_matrices(self): self._set_central_widget(VentanaMatrices())
    def mostrar_dependencias(self): self._set_central_widget(VerificarIndependencia())
    def mostrar_determinantes(self): self._set_central_widget(VentanaDeterminantes())
    def mostrar_multiplicacion_escalar(self): self._set_central_widget(VentanaMultiplicacionEscalar())

    def _por_ahora_no_disponible(self):
        w = QWidget(); lay = QVBoxLayout(w)
        msg = QLabel("Módulo próximamente disponible…"); msg.setAlignment(Qt.AlignmentFlag.AlignCenter); msg.setStyleSheet("font-size: 18px; font-weight: 600;")
        lay.addStretch(1); lay.addWidget(msg); lay.addStretch(2)
        self._set_central_widget(w)

    # ------------------- Contenido central -------------------
    def show_home(self):
        while self.content_layout.count() > 1:
            old = self.content_layout.widget(1)
            self.content_layout.removeWidget(old)
            old.setParent(None)
        self.content_layout.setCurrentIndex(0)

    def _set_central_widget(self, widget: QWidget):
        while self.content_layout.count() > 1:
            old = self.content_layout.widget(1)
            self.content_layout.removeWidget(old)
            old.setParent(None)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_layout.addWidget(widget)
        self.content_layout.setCurrentIndex(1)
        self._apply_theme_to_widget(widget)

    # ------------------- Logo de inicio -------------------
    def set_logo(self, path: str):
        """Carga el logo en la página de inicio."""
        self.logo_path = path
        pix = QPixmap(path)
        if not pix.isNull():
            self.logo_label.setPixmap(pix)
            self.content_layout.setCurrentIndex(0)
        else:
            self.logo_label.setText("No se pudo cargar el logo.\nVerifica la ruta en LOGO_INICIAL.")
            self.logo_label.setStyleSheet("font-size: 14px; color: #aa0000;")

    # ------------------- Tema / Idioma -------------------
    def toggle_tema(self):
        self.tema = "oscuro" if self.tema == "claro" else "claro"
        self._apply_theme()

    def toggle_idioma(self):
        self.idioma = "Inglés" if self.idioma == "Español" else "Español"

    # ------------------- Estilos -------------------
    def _apply_theme(self):
        pal = self.colors[self.tema]
        self.setStyleSheet(f"background-color: {pal['bg']}; color: {pal['fg']};")
        self.topbar.setStyleSheet(
            f"#TopBar {{ background: {pal['card']}; border-bottom: 1px solid {pal['border']}; }}"
        )
        self.btn_config.setStyleSheet(self._button_style(primary=True))
        self.navbar.setStyleSheet(f"#NavBar {{ background: {pal['card']}; border-right: 1px solid {pal['border']}; }}")

        # Reloj
        if hasattr(self, "clock_title"):
            self.clock_title.setStyleSheet(f"color: {pal['fg']}; font-size: 11px; opacity: 0.7; font-weight: 600;")
            self.clock_value.setStyleSheet(f"color: {pal['fg']}; font-size: 18px; font-weight: 700; letter-spacing: 1px;")

        # Imágenes (borde suave)
        if hasattr(self, "nav_images_frame"):
            self.nav_images_frame.setStyleSheet(f"QLabel {{ border: 1px solid {pal['border']}; border-radius: 6px; }}")

        # Logo label contraste
        self.logo_label.setStyleSheet(f"color: {pal['fg']};")

    def _apply_theme_to_widget(self, widget: QWidget):
        pal = self.colors[self.tema]
        widget.setStyleSheet(f"background-color: {pal['bg']}; color: {pal['fg']};")

    def _button_style(self, primary: bool = False) -> str:
        pal = self.colors[self.tema]
        start, end, text = pal['accent1'], pal['accent2'], '#FFFFFF'
        return (
            f"QPushButton#PrimaryBtn, QPushButton#NavBtn {{"
            f"  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {start}, stop:1 {end});"
            f"  color: {text}; font-weight: 600; border-radius: 10px; padding: 10px 14px; text-align: left;"
            f"}}"
            f"QPushButton#PrimaryBtn:hover, QPushButton#NavBtn:hover {{ filter: brightness(1.05); }}"
            f"QPushButton#PrimaryBtn:pressed, QPushButton#NavBtn:pressed {{ transform: scale(0.99); }}"
        )

