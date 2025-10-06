import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QSpinBox, QSizePolicy, QHeaderView
)
from PyQt6.QtCore import Qt

class VerificarIndependencia(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Verificar independencia lineal")
        self.setGeometry(200, 200, 700, 450)

        # ======== CONTROLES SUPERIORES ========
        self.label_dim = QLabel("Número de vectores (columnas):")
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 10)
        self.spin_cols.setValue(3)

        self.label_dim2 = QLabel("Dimensión de los vectores (filas):")
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 10)
        self.spin_rows.setValue(3)

        self.btn_generar = QPushButton("Generar tabla")
        self.btn_generar.clicked.connect(self.generar_tabla)
        self.btn_generar.setMinimumHeight(34)

        layout_dim = QHBoxLayout()
        layout_dim.addWidget(self.label_dim)
        layout_dim.addWidget(self.spin_cols)
        layout_dim.addSpacing(10)
        layout_dim.addWidget(self.label_dim2)
        layout_dim.addWidget(self.spin_rows)
        layout_dim.addSpacing(10)
        layout_dim.addWidget(self.btn_generar)
        layout_dim.addStretch()

        # ======== TABLA ========
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        try:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        self.table.horizontalHeader().setStretchLastSection(True)

        # ======== BOTONES INFERIORES ========
        self.btn_verificar = QPushButton("Verificar independencia")
        self.btn_verificar.setMinimumHeight(36)
        self.btn_verificar.clicked.connect(self.verificar_independencia)

        self.btn_limpiar = QPushButton("Limpiar tabla")
        self.btn_limpiar.setMinimumHeight(36)
        self.btn_limpiar.clicked.connect(self.limpiar_tabla)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.btn_limpiar)
        bottom_layout.addWidget(self.btn_verificar)

        # ======== RESULTADO ========
        self.resultado = QLabel("Resultado: ")
        self.resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ======== LAYOUT PRINCIPAL ========
        layout = QVBoxLayout()
        layout.addLayout(layout_dim)
        layout.addWidget(self.table, 1)
        layout.addLayout(bottom_layout)
        layout.addWidget(self.resultado)

        self.setLayout(layout)

        # ======== ESTILO VISUAL ========
        self.setStyleSheet("""
            QWidget { background-color: #f7f9fc; font-size: 14px; }
            QPushButton {
                background-color: #0078d4; color: white;
                border-radius: 6px; padding: 6px 12px;
            }
            QPushButton:hover { background-color: #005a9e; }
            QLabel { font-weight: bold; }
        """)

        # ======== GENERAR TABLA INICIAL ========
        self.generar_tabla()

    def generar_tabla(self):
        """Genera una tabla según las dimensiones indicadas."""
        filas = self.spin_rows.value()
        cols = self.spin_cols.value()
        self.table.setRowCount(filas)
        self.table.setColumnCount(cols)

        for j in range(cols):
            self.table.setHorizontalHeaderItem(j, QTableWidgetItem(f"v{j+1}"))

        for i in range(filas):
            for j in range(cols):
                self.table.setItem(i, j, QTableWidgetItem("0"))

        self.resultado.setText("Resultado: ")

    def limpiar_tabla(self):
        """Limpia el contenido de la tabla."""
        self.table.clearContents()
        self.resultado.setText("Resultado: ")

    def verificar_independencia(self):
        """Verifica si los vectores son linealmente independientes."""
        filas = self.table.rowCount()
        cols = self.table.columnCount()

        if filas == 0 or cols == 0:
            QMessageBox.warning(self, "Advertencia", "Primero genera la tabla antes de verificar.")
            return

        try:
            # Construir matriz desde la tabla
            matriz = []
            for i in range(filas):
                fila = []
                for j in range(cols):
                    item = self.table.item(i, j)
                    valor = float(item.text()) if item and item.text().strip() else 0.0
                    fila.append(valor)
                matriz.append(fila)

            rango = self.calcular_rango(matriz)

            if rango == cols:
                self.resultado.setText(
                    f'<b style="color:green;">Los vectores son LINEALMENTE INDEPENDIENTES ✅ (rango = {rango})</b>'
                )
            else:
                self.resultado.setText(
                    f'<b style="color:red;">Los vectores son DEPENDIENTES ❌ (rango = {rango})</b>'
                )

        except ValueError:
            QMessageBox.critical(self, "Error", "Verifica que todos los valores sean numéricos.")
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))

    def calcular_rango(self, matriz):
        """Calcula el rango de una matriz mediante eliminación de Gauss."""
        A = [fila[:] for fila in matriz]  # copia
        filas = len(A)
        cols = len(A[0]) if filas > 0 else 0
        rango = 0

        for col in range(cols):
            # Buscar pivote no nulo
            pivote = None
            for f in range(rango, filas):
                if abs(A[f][col]) > 1e-12:
                    pivote = f
                    break

            if pivote is None:
                continue

            # Intercambiar filas
            A[rango], A[pivote] = A[pivote], A[rango]
            pivote_val = A[rango][col]

            if abs(pivote_val) < 1e-12:
                continue

            # Normalizar fila pivote
            A[rango] = [val / pivote_val for val in A[rango]]

            # Eliminar el resto de filas
            for f in range(filas):
                if f != rango:
                    factor = A[f][col]
                    A[f] = [A[f][c] - factor * A[rango][c] for c in range(cols)]

            rango += 1

        return rango


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VerificarIndependencia()
    ventana.show()
    sys.exit(app.exec())
