import re
import sympy as sp
import math

# Mapeo de superíndices
SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_SIGNS = "⁻⁺"
NORMAL_DIGITS = "0123456789"
NORMAL_SIGNS = "-+"
DIGIT_TO_SUP = str.maketrans(NORMAL_DIGITS + "-", SUP_DIGITS + "⁻")
SUP_TO_NORMAL = str.maketrans(SUP_DIGITS + SUP_SIGNS, NORMAL_DIGITS + NORMAL_SIGNS)

def normalizar_expresion(expr: str) -> str:
    """Convierte una expresión de usuario 'bonita' a sintaxis Python válida."""
    s = expr.strip()
    if not s: return ""

    # 1. Reemplazos básicos
    s = s.replace("√", "sqrt").replace("∛", "cbrt")
    s = s.replace("π", "pi").replace("e", "E") # E de SymPy
    
    # 2. Superíndices a formato **
    def repl_sup(m):
        base = m.group(1)
        sup = m.group(2).translate(SUP_TO_NORMAL)
        return f"{base}**({sup})"
    s = re.sub(r"([a-zA-Z0-9\)\]])([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)", repl_sup, s)
    s = s.replace("^", "**")

    # 3. Multiplicación Implícita (El "fix" que tenías en Newton)
    # 2x -> 2*x, )x -> )*x
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)
    s = re.sub(r'(\))([a-zA-Z0-9(])', r'\1*\2', s)

    # 4. Funciones específicas
    s = re.sub(r"\bln\(", "log(", s)
    s = re.sub(r"\bsen\(", "sin(", s)
    
    return s

def obtener_funcion(expr_str: str):
    """
    Recibe un string de usuario y devuelve:
    1. Función compilada para cálculo numérico (rápida, usa numpy/math)
    2. Expresión simbólica de SymPy (para derivadas, etc.)
    """
    s_norm = normalizar_expresion(expr_str)
    
    # Contexto para SymPy
    x = sp.Symbol('x')
    local_dict = {
        "sqrt": sp.sqrt, 
        "cbrt": lambda t: sp.sign(t) * sp.Abs(t)**(sp.Rational(1,3)), # Raíz cúbica real
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, 
        "log": sp.log, "pi": sp.pi, "E": sp.E
    }
    
    # Parsear a SymPy
    expr_sym = sp.parse_expr(s_norm, local_dict=local_dict)
    
    # Crear función numérica (lambdify es más rápido y seguro que eval)
    # Usamos 'numpy' para que soporte arrays si graficamos
    f_num = sp.lambdify(x, expr_sym, modules=['numpy', 'math'])
    
    return f_num, expr_sym