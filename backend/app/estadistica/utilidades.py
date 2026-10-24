"""Funciones de apoyo para el motor estadístico."""

import math
from decimal import Decimal

EPS = 1e-9


def r(x: float, d: int = 10) -> float:
    """Redondeo seguro para evitar errores como 0.1 + 0.2 = 0.30000000000000004."""
    if x is None:
        return None
    return round(x + 0.0, d)


def fmt(x, d: int = 4) -> str:
    """Formatea un número para mostrarlo en el procedimiento."""
    if x is None:
        return "N/D"
    if isinstance(x, int) or (isinstance(x, float) and float(x).is_integer()):
        return str(int(x))
    texto = f"{x:.{d}f}".rstrip("0").rstrip(".")
    return texto if texto != "-0" else "0"


def decimales_de(x: float) -> int:
    """Cantidad de decimales que trae un dato (1.25 -> 2, 40 -> 0)."""
    exp = Decimal(str(x)).normalize().as_tuple().exponent
    return max(0, -exp)


def techo_a(x: float, unidad: float) -> float:
    """Redondea hacia arriba al múltiplo de `unidad` (1, 0.1, 0.01...)."""
    return r(math.ceil(r(x / unidad, 9) - EPS) * unidad)


def paso(titulo: str, formula: str, sustitucion: str = "", resultado: str = "") -> dict:
    """Un paso del procedimiento: lo que se muestra al alumno."""
    return {"titulo": titulo, "formula": formula, "sustitucion": sustitucion, "resultado": resultado}


def interpretar_cv(cv):
    if cv is None:
        return "No definido (media = 0)"
    if cv < 15:
        return "Datos homogéneos (baja variabilidad)"
    if cv < 30:
        return "Variabilidad moderada"
    return "Datos heterogéneos (alta variabilidad)"


def interpretar_asimetria(sk):
    if abs(sk) < 0.1:
        return "Aproximadamente simétrica"
    return "Asimétrica positiva (sesgo a la derecha)" if sk > 0 else "Asimétrica negativa (sesgo a la izquierda)"


def interpretar_curtosis_exceso(g2):
    if abs(g2) < 0.1:
        return "Mesocúrtica (similar a la normal)"
    return "Leptocúrtica (más apuntada que la normal)" if g2 > 0 else "Platicúrtica (más achatada que la normal)"
