"""Medidas para DATOS NO AGRUPADOS (datos sueltos).

Convenciones:
  - Cuantiles por posición L = k·(n + 1) / partes, con interpolación lineal
    entre los datos ordenados (método usual en cursos de Estadística I).
  - Varianza muestral con divisor n − 1 (también se reporta la poblacional).
"""

import math
from collections import Counter

from .utilidades import (
    fmt, paso, r, interpretar_cv, interpretar_asimetria, interpretar_curtosis_exceso,
)


def _cuantil(ordenados, k, partes, simbolo):
    n = len(ordenados)
    pos = k * (n + 1) / partes
    pasos = [paso(
        f"Posición de {simbolo}",
        f"L = {k}·(n + 1) / {partes}",
        f"L = {k}·({n} + 1) / {partes}",
        f"L = {fmt(pos)}",
    )]
    if pos <= 1:
        valor = ordenados[0]
        pasos.append(paso("Valor", "L ≤ 1 → se toma el primer dato", "", f"{simbolo} = {fmt(valor)}"))
    elif pos >= n:
        valor = ordenados[-1]
        pasos.append(paso("Valor", f"L ≥ n → se toma el último dato", "", f"{simbolo} = {fmt(valor)}"))
    else:
        entero = int(math.floor(pos))
        frac = r(pos - entero)
        x_inf, x_sup = ordenados[entero - 1], ordenados[entero]
        valor = x_inf + frac * (x_sup - x_inf)
        pasos.append(paso(
            "Interpolación",
            f"{simbolo} = x({entero}) + {fmt(frac)}·(x({entero + 1}) − x({entero}))",
            f"{simbolo} = {fmt(x_inf)} + {fmt(frac)}·({fmt(x_sup)} − {fmt(x_inf)})",
            f"{simbolo} = {fmt(valor)}",
        ))
    return {"k": k, "valor": r(valor), "posicion": r(pos), "pasos": pasos}


def tabla_simple(datos):
    """Tabla de frecuencias por valor (útil para datos discretos)."""
    n = len(datos)
    conteo = sorted(Counter(datos).items())
    filas, Fi = [], 0
    for valor, fi in conteo:
        Fi += fi
        filas.append({
            "valor": valor, "fi": fi, "Fi": Fi,
            "fr": r(fi / n), "Fr": r(Fi / n),
            "pct": r(fi / n * 100), "Pct": r(Fi / n * 100),
        })
    return filas


def analizar_no_agrupados(datos, percentiles=None, deciles=None):
    n = len(datos)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 datos.")
    x = sorted(datos)
    suma = sum(x)
    media = suma / n
    minimo, maximo = x[0], x[-1]
    rango = r(maximo - minimo)

    # --- Tendencia central ---
    if n % 2 == 1:
        mediana = x[n // 2]
        pasos_me = [paso("Mediana (n impar)", "Me = x((n + 1)/2)",
                         f"Me = x(({n} + 1)/2) = x({(n + 1) // 2})", f"Me = {fmt(mediana)}")]
    else:
        a, b = x[n // 2 - 1], x[n // 2]
        mediana = (a + b) / 2
        pasos_me = [paso("Mediana (n par)", "Me = (x(n/2) + x(n/2 + 1)) / 2",
                         f"Me = (x({n // 2}) + x({n // 2 + 1})) / 2 = ({fmt(a)} + {fmt(b)}) / 2",
                         f"Me = {fmt(mediana)}")]

    conteo = Counter(x)
    fmax = max(conteo.values())
    if fmax == 1:
        modas, tipo_moda = [], "amodal"
        pasos_mo = [paso("Moda", "Valor que más se repite", "Ningún valor se repite", "No hay moda (amodal)")]
    else:
        modas = sorted(v for v, c in conteo.items() if c == fmax)
        tipo_moda = "unimodal" if len(modas) == 1 else ("bimodal" if len(modas) == 2 else "multimodal")
        pasos_mo = [paso("Moda", "Valor(es) con mayor frecuencia",
                         f"Frecuencia máxima = {fmax}", f"Mo = {', '.join(fmt(m) for m in modas)} ({tipo_moda})")]

    geometrica = armonica = None
    if all(v > 0 for v in x):
        geometrica = math.exp(sum(math.log(v) for v in x) / n)
        armonica = n / sum(1 / v for v in x)

    # --- Dispersión ---
    sc = sum((v - media) ** 2 for v in x)
    var_m = sc / (n - 1)
    var_p = sc / n
    s = math.sqrt(var_m)
    sigma = math.sqrt(var_p)
    cv = (s / abs(media) * 100) if media != 0 else None
    dm = sum(abs(v - media) for v in x) / n
    error_est = s / math.sqrt(n)

    # --- Posición ---
    cuartiles = [_cuantil(x, k, 4, f"Q{k}") for k in (1, 2, 3)]
    deciles_res = [_cuantil(x, k, 10, f"D{k}") for k in (deciles or []) if 0 < k < 10]
    percentiles_res = [_cuantil(x, k, 100, f"P{k}") for k in (percentiles or []) if 0 < k < 100]
    q1, q3 = cuartiles[0]["valor"], cuartiles[2]["valor"]
    ric = q3 - q1
    lim_inf, lim_sup = q1 - 1.5 * ric, q3 + 1.5 * ric
    atipicos = [v for v in x if v < lim_inf or v > lim_sup]

    # --- Forma ---
    sk_pearson = 3 * (media - mediana) / s if s > 0 else 0
    m3 = sum((v - media) ** 3 for v in x) / n
    m4 = sum((v - media) ** 4 for v in x) / n
    g1 = m3 / sigma ** 3 if sigma > 0 else 0
    g2 = m4 / sigma ** 4 - 3 if sigma > 0 else 0

    return {
        "tipo": "no_agrupados",
        "resumen": {
            "n": n, "suma": r(suma), "minimo": minimo, "maximo": maximo, "rango": rango,
            "ordenados": x,
        },
        "tabla_simple": tabla_simple(x),
        "tendencia_central": {
            "media": {"valor": r(media), "pasos": [paso("Media aritmética", "x̄ = Σxi / n",
                                                       f"x̄ = {fmt(suma)} / {n}", f"x̄ = {fmt(media)}")]},
            "mediana": {"valor": r(mediana), "pasos": pasos_me},
            "moda": {"valores": modas, "tipo": tipo_moda, "pasos": pasos_mo},
            "media_geometrica": {"valor": r(geometrica) if geometrica else None, "pasos": [paso(
                "Media geométrica", "G = (x1·x2·…·xn)^(1/n)",
                "Calculada con logaritmos: G = e^(Σln xi / n)" if geometrica else "Requiere datos > 0",
                f"G = {fmt(geometrica)}")]},
            "media_armonica": {"valor": r(armonica) if armonica else None, "pasos": [paso(
                "Media armónica", "H = n / Σ(1/xi)",
                f"H = {n} / {fmt(n / armonica) if armonica else 'N/D'}", f"H = {fmt(armonica)}")]},
        },
        "dispersion": {
            "rango": {"valor": rango, "pasos": [paso("Rango", "R = Xmax − Xmin",
                                                     f"R = {fmt(maximo)} − {fmt(minimo)}", f"R = {fmt(rango)}")]},
            "varianza": {"valor": r(var_m), "poblacional": r(var_p), "pasos": [
                paso("Suma de cuadrados", "SC = Σ(xi − x̄)²", "", f"SC = {fmt(sc)}"),
                paso("Varianza muestral", "s² = SC / (n − 1)", f"s² = {fmt(sc)} / {n - 1}", f"s² = {fmt(var_m)}"),
                paso("Varianza poblacional", "σ² = SC / n", f"σ² = {fmt(sc)} / {n}", f"σ² = {fmt(var_p)}"),
            ]},
            "desviacion": {"valor": r(s), "poblacional": r(sigma), "pasos": [
                paso("Desviación estándar", "s = √s²", f"s = √{fmt(var_m)}", f"s = {fmt(s)}")]},
            "coeficiente_variacion": {"valor": r(cv) if cv is not None else None,
                                      "interpretacion": interpretar_cv(cv), "pasos": [
                paso("Coeficiente de variación", "CV = (s / x̄)·100",
                     f"CV = ({fmt(s)} / {fmt(media)})·100", f"CV = {fmt(cv, 2)} %")]},
            "desviacion_media": {"valor": r(dm), "pasos": [
                paso("Desviación media", "DM = Σ|xi − x̄| / n", "", f"DM = {fmt(dm)}")]},
            "error_estandar": {"valor": r(error_est), "pasos": [
                paso("Error estándar de la media", "EE = s / √n", f"EE = {fmt(s)} / √{n}", f"EE = {fmt(error_est)}")]},
            "rango_intercuartil": {"valor": r(ric), "pasos": [
                paso("Rango intercuartil", "RIC = Q3 − Q1", f"RIC = {fmt(q3)} − {fmt(q1)}", f"RIC = {fmt(ric)}")]},
        },
        "posicion": {"cuartiles": cuartiles, "deciles": deciles_res, "percentiles": percentiles_res},
        "forma": {
            "asimetria_pearson": {"valor": r(sk_pearson), "interpretacion": interpretar_asimetria(sk_pearson), "pasos": [
                paso("Asimetría de Pearson", "Sk = 3(x̄ − Me) / s",
                     f"Sk = 3({fmt(media)} − {fmt(mediana)}) / {fmt(s)}", f"Sk = {fmt(sk_pearson)}")]},
            "asimetria_fisher": {"valor": r(g1), "interpretacion": interpretar_asimetria(g1), "pasos": [
                paso("Asimetría de Fisher", "g1 = m3 / σ³, con m3 = Σ(xi − x̄)³ / n",
                     f"g1 = {fmt(m3)} / {fmt(sigma)}³", f"g1 = {fmt(g1)}")]},
            "curtosis": {"valor": r(g2), "interpretacion": interpretar_curtosis_exceso(g2), "pasos": [
                paso("Curtosis (exceso)", "g2 = m4 / σ⁴ − 3, con m4 = Σ(xi − x̄)⁴ / n",
                     f"g2 = {fmt(m4)} / {fmt(sigma)}⁴ − 3", f"g2 = {fmt(g2)}")]},
        },
        "caja": {
            "minimo": minimo, "q1": q1, "mediana": r(mediana), "q3": q3, "maximo": maximo,
            "limite_inferior": r(lim_inf), "limite_superior": r(lim_sup), "atipicos": atipicos,
        },
    }
