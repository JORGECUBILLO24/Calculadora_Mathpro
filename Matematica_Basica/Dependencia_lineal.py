import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QSpinBox, QSizePolicy, QHeaderView,
    QTextEdit
)
from PyQt6.QtGui import QFont
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

        # Área para mostrar el paso a paso
        self.pasos_text = QTextEdit()
        self.pasos_text.setReadOnly(True)
        self.pasos_text.setFont(QFont("Consolas", 11))
        self.pasos_text.setMinimumHeight(180)
        self.pasos_text.setPlaceholderText("Aquí se mostrará el procedimiento paso a paso...")

        # ======== LAYOUT PRINCIPAL ========
        layout = QVBoxLayout()
        layout.addLayout(layout_dim)
        layout.addWidget(self.table, 1)
        layout.addLayout(bottom_layout)
        layout.addWidget(self.resultado)
        layout.addWidget(self.pasos_text, 1)

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

            rango, pasos = self.calcular_rango(matriz)

            # Mostrar pasos en el área correspondiente
            try:
                self.pasos_text.setPlainText("\n\n".join(pasos) if pasos else "No hay pasos para mostrar.")
            except Exception:
                self.pasos_text.setPlainText("")

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
        """Calcula el rango de una matriz mediante eliminación de Gauss.

        Además devuelve una lista de pasos descriptivos (strings) que explican
        las operaciones realizadas: intercambios, normalizaciones y eliminaciones.
        """
        pasos = []
        A = [fila[:] for fila in matriz]  # copia
        filas = len(A)
        cols = len(A[0]) if filas > 0 else 0
        rango = 0

        def formatear_fila(row):
            return "[ " + "  ".join(f"{v:.6g}" for v in row) + " ]"

        pasos.append("Matriz inicial:")
        for r in A:
            pasos.append(formatear_fila(r))

        for col in range(cols):
            # Buscar pivote no nulo
            pivote = None
            for f in range(rango, filas):
                if abs(A[f][col]) > 1e-12:
                    pivote = f
                    break

            if pivote is None:
                pasos.append(f"Columna {col+1}: no se encontró pivote (toda columna nula en las filas restantes).")
                continue

            # Intercambiar filas si es necesario
            if pivote != rango:
                pasos.append(f"Intercambiar fila {rango+1} con fila {pivote+1} -> antes:")
                pasos.append(formatear_fila(A[rango]))
                pasos.append(formatear_fila(A[pivote]))
                A[rango], A[pivote] = A[pivote], A[rango]
                pasos.append("Después del intercambio:")
                for r in A:
                    pasos.append(formatear_fila(r))

            pivote_val = A[rango][col]

            if abs(pivote_val) < 1e-12:
                pasos.append(f"Pivote en fila {rango+1} cerca de cero; se omite.")
                continue

            # Normalizar fila pivote
            pasos.append(f"Normalizar fila {rango+1} dividiendo por {pivote_val:.6g} -> antes:")
            pasos.append(formatear_fila(A[rango]))
            A[rango] = [val / pivote_val for val in A[rango]]
            pasos.append("Después de normalizar:")
            pasos.append(formatear_fila(A[rango]))

            # Eliminar el resto de filas
            for f in range(filas):
                if f != rango:
                    factor = A[f][col]
                    if abs(factor) < 1e-12:
                        continue
                    pasos.append(f"F{f+1} -> F{f+1} - ({factor:.6g})·F{rango+1} -> antes:")
                    pasos.append(formatear_fila(A[f]))
                    A[f] = [A[f][c] - factor * A[rango][c] for c in range(cols)]
                    pasos.append("Después:")
                    pasos.append(formatear_fila(A[f]))

            rango += 1

            # Mostrar matriz actual tras procesar la columna
            pasos.append(f"Matriz tras procesar columna {col+1}:")
            for r in A:
                pasos.append(formatear_fila(r))

        pasos.append(f"Rango calculado: {rango}")
        return rango, pasos


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VerificarIndependencia()
    ventana.show()
    sys.exit(app.exec())
