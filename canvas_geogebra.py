# -*- coding: utf-8 -*-
"""
canvas_geogebra.py
Gráfica estilo GeoGebra para los métodos numéricos
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class GeoGebraCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots(figsize=(6,4), dpi=110)
        super().__init__(fig)
        self.setParent(parent)
        self._config()

    def _config(self):
        self.ax.axhline(0, color="#000000", linewidth=1)
        self.ax.axvline(0, color="#000000", linewidth=1)
        self.ax.grid(True, linestyle="--", alpha=0.35)

    def plot_function(self, f, a=-10, b=10, root=None):
        self.ax.clear()
        self._config()

        xs = np.linspace(a, b, 600)
        ys = np.array([f(x) for x in xs], dtype=float)

        self.ax.plot(xs, ys, color="#2563eb", linewidth=2)

        if root is not None:
            try:
                y = f(root)
                self.ax.scatter([root], [y], s=80, color="#d00000")
            except:
                pass

        self.draw_idle()
