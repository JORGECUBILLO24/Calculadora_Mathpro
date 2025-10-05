import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QSpinBox, QSizePolicy, QHeaderView
)

class VerificarIndependencia(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Verificar independencia lineal")
        self.setGeometry(200, 200, 600, 400)

        # Selector de dimensiones
        self.label_dim = QLabel("Número de vectores (columnas):")
        self.spin_cols = QSpinBox()
        self.spin_cols.setValue(3)
        self.spin_cols.setMinimum(1)
        self.spin_cols.setMaximum(10)

        self.label_dim2 = QLabel("Dimensión de los vectores (filas):")
        self.spin_rows = QSpinBox()
        self.spin_rows.setValue(3)
        self.spin_rows.setMinimum(1)
        self.spin_rows.setMaximum(10)

        self.btn_generar = QPushButton("Generar tabla")
        self.btn_generar.clicked.connect(self.generar_tabla)
        self.btn_generar.setMinimumHeight(34)
        self.btn_generar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Tabla para los vectores
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Hacer que las columnas se estiren para ocupar el espacio disponible
        self.table.horizontalHeader().setStretchLastSection(True)
        try:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            # En versiones antiguas la API puede ser diferente; ignoramos si falla
            pass

        # Botón para verificar independencia
        self.btn_verificar = QPushButton("Verificar independencia")
        self.btn_verificar.clicked.connect(self.verificar_independencia)
        self.btn_verificar.setMinimumHeight(36)
        self.btn_verificar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Etiqueta resultado
        self.resultado = QLabel("Resultado: ")

        # Layout principal
        layout = QVBoxLayout()
        layout_dim = QHBoxLayout()

        # Ajustar tamaños y stretches para mejor distribución
        self.spin_cols.setFixedWidth(80)
        self.spin_rows.setFixedWidth(80)
        layout_dim.addWidget(self.label_dim)
        layout_dim.addWidget(self.spin_cols)
        layout_dim.addSpacing(10)
        layout_dim.addWidget(self.label_dim2)
        layout_dim.addWidget(self.spin_rows)
        layout_dim.addSpacing(10)
        layout_dim.addWidget(self.btn_generar)
        layout_dim.addStretch(1)

        layout.addLayout(layout_dim)
        # Dar prioridad de expansión a la tabla
        layout.addWidget(self.table, 1)

        # Botones y resultado alineados a la derecha
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.btn_verificar)
        layout.addLayout(bottom_layout)
        layout.addWidget(self.resultado)

        self.setLayout(layout)

        # Generar tabla inicial
        self.generar_tabla()

    def generar_tabla(self):
        filas = self.spin_rows.value()
        cols = self.spin_cols.value()
        self.table.setRowCount(filas)
        self.table.setColumnCount(cols)

        # Nombres de columnas
        for j in range(cols):
            self.table.setHorizontalHeaderItem(j, QTableWidgetItem(f"v{j+1}"))

        # Inicializar con ceros
        for i in range(filas):
            for j in range(cols):
                self.table.setItem(i, j, QTableWidgetItem("0"))

    def verificar_independencia(self):
        filas = self.table.rowCount()
        cols = self.table.columnCount()

        try:
            # Construir la matriz a partir de la tabla
            matriz = []
            for i in range(filas):
                fila = []
                for j in range(cols):
                    item = self.table.item(i, j)
                    fila.append(float(item.text()) if item else 0.0)
                matriz.append(fila)

            rango = self.calcular_rango(matriz)

            if rango == cols:
                self.resultado.setText("Resultado: Los vectores son LINEALMENTE INDEPENDIENTES ✅")
            else:
                self.resultado.setText("Resultado: Los vectores son DEPENDIENTES ❌")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al leer la tabla: {e}")

    def calcular_rango(self, matriz):
        """ Calcula el rango de una matriz usando eliminación de Gauss sin librerías externas """
        A = [fila[:] for fila in matriz]  # copia
        filas = len(A)
        cols = len(A[0]) if filas > 0 else 0
        rango = 0

        for col in range(cols):
            # Buscar fila con pivote distinto de 0
            pivote = None
            for f in range(rango, filas):
                if abs(A[f][col]) > 1e-10:
                    pivote = f
                    break

            if pivote is None:
                continue

            # Intercambiar filas
            A[rango], A[pivote] = A[pivote], A[rango]

            # Normalizar fila pivote
            pivote_val = A[rango][col]
            A[rango] = [val / pivote_val for val in A[rango]]

            # Eliminar en otras filas
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
