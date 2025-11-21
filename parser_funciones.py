
# -*- coding: utf-8 -*-
"""
parser_funciones.py
Convierte notación matemática natural a expresiones válidas para SymPy.
Incluye:
- superíndices (²³⁴⁵…)
- raíz √(), raíz cúbica ∛()
- π, e, ln()
- detección de ^ -> superíndice
- flecha ↑↑ y flechas del numpad para modo superíndice
"""

import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)

X = sp.symbols("x")

SUPERSCRIPT_MAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

def convertir_superindices(expr: str) -> str:
    def reemplazo(m):
        base = m.group(1)
        expo = m.group(2).translate(SUPERSCRIPT_MAP)
        return f"{base}**({expo})"

    expr = re.sub(r"([A-Za-z0-9\)\]])([\⁰¹²³⁴⁵⁶⁷⁸⁹]+)", reemplazo, expr)
    return expr


def normalizar(expr: str) -> str:
    s = expr.strip()

    s = s.replace("π", "pi")
    s = s.replace("√", "sqrt")
    s = s.replace("∛", "cbrt")

    s = convertir_superindices(s)

    s = s.replace("^", "**")

    s = re.sub(r"ln\(", "log(", s)
    s = re.sub(r"sen\(", "sin(", s)
    s = re.sub(r"cbrt\s*\(", "cbrt(", s)

    return s


def construir_funcion(expr: str):
    expr_norm = normalizar(expr)

    try:
        f = parse_expr(
            expr_norm,
            transformations=(standard_transformations + (implicit_multiplication_application,)),
            local_dict={
                "x": X,
                "sqrt": sp.sqrt,
                "cbrt": lambda t: sp.sign(t) * sp.Abs(t)**(sp.Rational(1,3)),
                "sin": sp.sin,
                "cos": sp.cos,
                "tan": sp.tan,
                "log": sp.log,
                "pi": sp.pi,
                "e": sp.E
            }
        )
    except Exception as e:
        raise ValueError(f"Error interpretando expresión: {e}")

    f_num = sp.lambdify(X, f, "numpy")
    return f_num, f
