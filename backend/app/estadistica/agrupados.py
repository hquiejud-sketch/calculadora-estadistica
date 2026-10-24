"""Medidas para DATOS AGRUPADOS (tabla de distribución de frecuencias).

Dos formas de entrada:
  1. Datos en bruto -> se construye la tabla (Sturges, raíz de n o k manual).
  2. Tabla ya dada (intervalos + frecuencias), como viene en muchos ejercicios.

Convenciones:
  - k por Sturges: k = 1 + 3.322·log10(n), redondeado al entero más cercano.
  - Amplitud A = R / k redondeada SIEMPRE hacia arriba a la precisión de los datos.
  - Modo "continuo": [Li, Ls) y la última clase cerrada.
  - Modo "discreto": límites aparentes (20–24) y límites reales (19.5–24.5).
  - Cuantiles por interpolación: Q = LRi + ((k·n/partes − Fi₋₁) / fi)·A.
"""

import math

from .utilidades import (
    EPS, fmt, paso, r, decimales_de, techo_a,
    interpretar_cv, interpretar_asimetria, interpretar_curtosis_exceso,
)


# --------------------------------------------------------------------------
# Construcción de la tabla
# --------------------------------------------------------------------------

def _completar_filas(filas, n):
    """Agrega columnas derivadas a cada fila (xi, Fi, fr, etc.)."""
    Fi = 0
    for i, f in enumerate(filas):
        Fi += f["fi"]
        f["clase"] = i + 1
        f["A"] = r(f["lrs"] - f["lri"])
        f["xi"] = r((f["lri"] + f["lrs"]) / 2)
        f["Fi"] = Fi
        f["fr"] = r(f["fi"] / n)
        f["Fr"] = r(Fi / n)
        f["pct"] = r(f["fi"] / n * 100)
        f["Pct"] = r(Fi / n * 100)
        f["xi_fi"] = r(f["xi"] * f["fi"])
        f["xi2_fi"] = r(f["xi"] ** 2 * f["fi"])
    # Frecuencia acumulada "o más" (descendente), útil para la ojiva mayor que.
    acumulada = n
    for f in filas:
        f["Fi_desc"] = acumulada
        acumulada -= f["fi"]
    return filas


def tabla_desde_datos(datos, metodo_k="sturges", k_manual=None, amplitud_manual=None,
                      limite_inicial=None, modo="continuo"):
    n = len(datos)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 datos.")
    x = sorted(datos)
    minimo, maximo = x[0], x[-1]
    rango = r(maximo - minimo)
    precision = max(decimales_de(v) for v in x)
    unidad = r(10 ** -precision)
    modo = "discreto" if modo == "discreto" else "continuo"
    pasos = [paso("Rango", "R = Xmax − Xmin", f"R = {fmt(maximo)} − {fmt(minimo)}", f"R = {fmt(rango)}")]

    if metodo_k == "manual" and k_manual:
        k = max(1, int(k_manual))
        pasos.append(paso("Número de clases", "k definido por el usuario", "", f"k = {k}"))
    elif metodo_k == "raiz":
        bruto = math.sqrt(n)
        k = max(1, round(bruto))
        pasos.append(paso("Número de clases (raíz)", "k = √n", f"k = √{n} = {fmt(bruto)}", f"k ≈ {k}"))
    else:
        bruto = 1 + 3.322 * math.log10(n)
        k = max(1, round(bruto))
        pasos.append(paso("Número de clases (Sturges)", "k = 1 + 3.322·log₁₀(n)",
                          f"k = 1 + 3.322·log₁₀({n}) = {fmt(bruto)}", f"k ≈ {k}"))

    a_cubrir = r(rango + unidad) if modo == "discreto" else rango
    if amplitud_manual:
        A = float(amplitud_manual)
        pasos.append(paso("Amplitud", "A definida por el usuario", "", f"A = {fmt(A)}"))
    else:
        bruta = a_cubrir / k if a_cubrir > 0 else unidad
        A = techo_a(bruta, unidad)
        formula = "A = (R + u) / k" if modo == "discreto" else "A = R / k"
        sust = (f"A = ({fmt(rango)} + {fmt(unidad)}) / {k}" if modo == "discreto"
                else f"A = {fmt(rango)} / {k}") + f" = {fmt(bruta)}"
        pasos.append(paso("Amplitud", formula, sust,
                          f"A = {fmt(A)} (redondeada hacia arriba a {fmt(unidad)})"))

    li0 = float(limite_inicial) if limite_inicial is not None else minimo
    ajuste = unidad if modo == "discreto" else 0
    while li0 + k * A - ajuste < maximo - EPS:
        k += 1  # si no se cubre Xmax se agrega una clase

    filas = []
    for i in range(k):
        li = r(li0 + i * A)
        ls_real = r(li + A)
        ultima = i == k - 1
        if modo == "discreto":
            ls = r(ls_real - unidad)
            lri, lrs = r(li - unidad / 2), r(ls + unidad / 2)
            fi = sum(1 for v in x if li - EPS <= v <= ls + EPS)
            intervalo = f"{fmt(li)} – {fmt(ls)}"
        else:
            ls = ls_real
            lri, lrs = li, ls_real
            if ultima:
                fi = sum(1 for v in x if li - EPS <= v <= ls + EPS)
            else:
                fi = sum(1 for v in x if li - EPS <= v < ls - EPS)
            intervalo = f"[{fmt(li)}, {fmt(ls)}{']' if ultima else ')'}"
        filas.append({"li": li, "ls": ls, "lri": lri, "lrs": lrs, "intervalo": intervalo, "fi": fi})

    _completar_filas(filas, n)
    parametros = {
        "n": n, "minimo": minimo, "maximo": maximo, "rango": rango, "k": k, "amplitud": A,
        "precision": precision, "unidad": unidad, "modo": modo, "limite_inicial": li0,
        "origen": "datos",
    }
    return {"parametros": parametros, "filas": filas, "pasos_construccion": pasos, "ordenados": x}


def tabla_desde_intervalos(intervalos):
    """intervalos: lista de {li, ls, fi} tal como vienen en el ejercicio."""
    if len(intervalos) < 2:
        raise ValueError("Ingresa al menos 2 intervalos.")
    ints = sorted(({"li": float(i["li"]), "ls": float(i["ls"]), "fi": int(i["fi"])} for i in intervalos),
                  key=lambda i: i["li"])
    for i in ints:
        if i["ls"] <= i["li"]:
            raise ValueError(f"Intervalo inválido: {fmt(i['li'])} – {fmt(i['ls'])}")
        if i["fi"] < 0:
            raise ValueError("Las frecuencias no pueden ser negativas.")
    n = sum(i["fi"] for i in ints)
    if n == 0:
        raise ValueError("La suma de frecuencias debe ser mayor que 0.")

    hueco = r(ints[1]["li"] - ints[0]["ls"])
    modo = "discreto" if hueco > EPS else "continuo"
    filas = []
    for idx, i in enumerate(ints):
        if modo == "discreto":
            lri, lrs = r(i["li"] - hueco / 2), r(i["ls"] + hueco / 2)
            intervalo = f"{fmt(i['li'])} – {fmt(i['ls'])}"
        else:
            lri, lrs = i["li"], i["ls"]
            intervalo = f"[{fmt(i['li'])}, {fmt(i['ls'])}{']' if idx == len(ints) - 1 else ')'}"
        filas.append({"li": i["li"], "ls": i["ls"], "lri": lri, "lrs": lrs, "intervalo": intervalo, "fi": i["fi"]})

    _completar_filas(filas, n)
    pasos = [paso("Tabla ingresada", "Intervalos y frecuencias dados por el ejercicio",
                  f"{len(filas)} clases, modo {modo}" + (f" (límites reales a ±{fmt(hueco / 2)})" if modo == "discreto" else ""),
                  f"n = Σfi = {n}")]
    parametros = {
        "n": n, "minimo": filas[0]["li"], "maximo": filas[-1]["ls"],
        "rango": r(filas[-1]["ls"] - filas[0]["li"]), "k": len(filas),
        "amplitud": filas[0]["A"], "modo": modo, "origen": "intervalos",
    }
    return {"parametros": parametros, "filas": filas, "pasos_construccion": pasos, "ordenados": None}


# --------------------------------------------------------------------------
# Medidas
# --------------------------------------------------------------------------

def _cuantil(filas, n, k, partes, simbolo):
    pos = k * n / partes
    idx = next((i for i, f in enumerate(filas) if f["Fi"] >= pos - EPS and f["fi"] > 0), len(filas) - 1)
    f = filas[idx]
    F_ant = filas[idx - 1]["Fi"] if idx > 0 else 0
    valor = f["lri"] + ((pos - F_ant) / f["fi"]) * f["A"]
    return {
        "k": k, "valor": r(valor), "posicion": r(pos), "clase": f["clase"],
        "pasos": [
            paso(f"Posición de {simbolo}", f"pos = {k}·n / {partes}", f"pos = {k}·{n} / {partes}",
                 f"pos = {fmt(pos)} → clase {f['clase']} ({f['intervalo']}), primera con Fi ≥ {fmt(pos)}"),
            paso(f"Cálculo de {simbolo}", f"{simbolo} = Li + ((pos − Fi₋₁) / fi)·A",
                 f"{simbolo} = {fmt(f['lri'])} + (({fmt(pos)} − {F_ant}) / {f['fi']})·{fmt(f['A'])}",
                 f"{simbolo} = {fmt(valor)}"),
        ],
    }


def medidas_agrupadas(tabla, percentiles=None, deciles=None):
    filas = tabla["filas"]
    n = tabla["parametros"]["n"]
    s_xf = sum(f["xi_fi"] for f in filas)
    s_x2f = sum(f["xi2_fi"] for f in filas)

    # Tendencia central
    media = s_xf / n
    mediana = _cuantil(filas, n, 2, 4, "Me")
    mediana["pasos"][0]["formula"] = "pos = n / 2"
    mediana["pasos"][0]["sustitucion"] = f"pos = {n} / 2"

    fmax = max(f["fi"] for f in filas)
    modas = []
    for f in filas:
        if f["fi"] != fmax:
            continue
        i = f["clase"] - 1
        f_ant = filas[i - 1]["fi"] if i > 0 else 0
        f_sig = filas[i + 1]["fi"] if i < len(filas) - 1 else 0
        d1, d2 = f["fi"] - f_ant, f["fi"] - f_sig
        valor = f["xi"] if d1 + d2 == 0 else f["lri"] + d1 / (d1 + d2) * f["A"]
        modas.append({"valor": r(valor), "clase": f["clase"], "pasos": [
            paso("Clase modal", "Clase con mayor fi", "", f"Clase {f['clase']} ({f['intervalo']}), fi = {f['fi']}"),
            paso("Diferencias", "Δ1 = fi − fi₋₁ ;  Δ2 = fi − fi₊₁",
                 f"Δ1 = {f['fi']} − {f_ant} ;  Δ2 = {f['fi']} − {f_sig}", f"Δ1 = {d1} ;  Δ2 = {d2}"),
            paso("Moda (Czuber)", "Mo = Li + (Δ1 / (Δ1 + Δ2))·A",
                 f"Mo = {fmt(f['lri'])} + ({d1} / {d1 + d2})·{fmt(f['A'])}" if d1 + d2 else "Δ1 + Δ2 = 0 → se usa la marca de clase",
                 f"Mo = {fmt(valor)}"),
        ]})
    tipo_moda = "unimodal" if len(modas) == 1 else ("bimodal" if len(modas) == 2 else "multimodal")

    # Dispersión
    sc = sum((f["xi"] - media) ** 2 * f["fi"] for f in filas)
    var_m = sc / (n - 1) if n > 1 else 0
    var_p = sc / n
    s = math.sqrt(var_m)
    sigma = math.sqrt(var_p)
    cv = s / abs(media) * 100 if media != 0 else None
    dm = sum(abs(f["xi"] - media) * f["fi"] for f in filas) / n

    # Posición
    cuartiles = [_cuantil(filas, n, k, 4, f"Q{k}") for k in (1, 2, 3)]
    deciles_res = [_cuantil(filas, n, k, 10, f"D{k}") for k in (deciles or []) if 0 < k < 10]
    percentiles_res = [_cuantil(filas, n, k, 100, f"P{k}") for k in (percentiles or []) if 0 < k < 100]
    q1, q3 = cuartiles[0]["valor"], cuartiles[2]["valor"]
    p10 = _cuantil(filas, n, 10, 100, "P10")["valor"]
    p90 = _cuantil(filas, n, 90, 100, "P90")["valor"]
    ric = q3 - q1

    # Forma
    me = mediana["valor"]
    sk_pearson = 3 * (media - me) / s if s > 0 else 0
    sk_bowley = (q3 + q1 - 2 * me) / ric if ric > 0 else 0
    m3 = sum((f["xi"] - media) ** 3 * f["fi"] for f in filas) / n
    m4 = sum((f["xi"] - media) ** 4 * f["fi"] for f in filas) / n
    g1 = m3 / sigma ** 3 if sigma > 0 else 0
    g2 = m4 / sigma ** 4 - 3 if sigma > 0 else 0
    k_perc = ric / (2 * (p90 - p10)) if p90 > p10 else 0
    if abs(k_perc - 0.263) < 0.01:
        interp_k = "Mesocúrtica (K ≈ 0.263)"
    elif k_perc < 0.263:
        interp_k = "Leptocúrtica (K < 0.263)"
    else:
        interp_k = "Platicúrtica (K > 0.263)"

    totales = {
        "fi": n, "fr": r(sum(f["fr"] for f in filas)), "pct": r(sum(f["pct"] for f in filas)),
        "xi_fi": r(s_xf), "xi2_fi": r(s_x2f),
    }

    return {
        "totales": totales,
        "tendencia_central": {
            "media": {"valor": r(media), "pasos": [paso("Media", "x̄ = Σ(xi·fi) / n",
                                                       f"x̄ = {fmt(s_xf)} / {n}", f"x̄ = {fmt(media)}")]},
            "mediana": {"valor": r(me), "pasos": mediana["pasos"], "clase": mediana["clase"]},
            "moda": {"valores": modas, "tipo": tipo_moda},
        },
        "dispersion": {
            "rango": {"valor": tabla["parametros"]["rango"], "pasos": tabla["pasos_construccion"][:1]},
            "varianza": {"valor": r(var_m), "poblacional": r(var_p), "pasos": [
                paso("Varianza muestral", "s² = (Σ(xi²·fi) − n·x̄²) / (n − 1)",
                     f"s² = ({fmt(s_x2f)} − {n}·{fmt(media)}²) / {n - 1}", f"s² = {fmt(var_m)}"),
                paso("Varianza poblacional", "σ² = Σ(xi − x̄)²·fi / n", f"σ² = {fmt(sc)} / {n}", f"σ² = {fmt(var_p)}"),
            ]},
            "desviacion": {"valor": r(s), "poblacional": r(sigma), "pasos": [
                paso("Desviación estándar", "s = √s²", f"s = √{fmt(var_m)}", f"s = {fmt(s)}")]},
            "coeficiente_variacion": {"valor": r(cv) if cv is not None else None,
                                      "interpretacion": interpretar_cv(cv), "pasos": [
                paso("Coeficiente de variación", "CV = (s / x̄)·100",
                     f"CV = ({fmt(s)} / {fmt(media)})·100", f"CV = {fmt(cv, 2)} %")]},
            "desviacion_media": {"valor": r(dm), "pasos": [
                paso("Desviación media", "DM = Σ|xi − x̄|·fi / n", "", f"DM = {fmt(dm)}")]},
            "rango_intercuartil": {"valor": r(ric), "pasos": [
                paso("Rango intercuartil", "RIC = Q3 − Q1", f"RIC = {fmt(q3)} − {fmt(q1)}", f"RIC = {fmt(ric)}")]},
        },
        "posicion": {"cuartiles": cuartiles, "deciles": deciles_res, "percentiles": percentiles_res},
        "forma": {
            "asimetria_pearson": {"valor": r(sk_pearson), "interpretacion": interpretar_asimetria(sk_pearson), "pasos": [
                paso("Asimetría de Pearson", "Sk = 3(x̄ − Me) / s",
                     f"Sk = 3({fmt(media)} − {fmt(me)}) / {fmt(s)}", f"Sk = {fmt(sk_pearson)}")]},
            "asimetria_bowley": {"valor": r(sk_bowley), "interpretacion": interpretar_asimetria(sk_bowley), "pasos": [
                paso("Asimetría de Bowley", "Sk = (Q3 + Q1 − 2·Me) / (Q3 − Q1)",
                     f"Sk = ({fmt(q3)} + {fmt(q1)} − 2·{fmt(me)}) / ({fmt(q3)} − {fmt(q1)})", f"Sk = {fmt(sk_bowley)}")]},
            "asimetria_fisher": {"valor": r(g1), "interpretacion": interpretar_asimetria(g1), "pasos": [
                paso("Asimetría de Fisher", "g1 = Σ(xi − x̄)³·fi / (n·σ³)", f"g1 = {fmt(m3)} / {fmt(sigma)}³", f"g1 = {fmt(g1)}")]},
            "curtosis": {"valor": r(g2), "interpretacion": interpretar_curtosis_exceso(g2), "pasos": [
                paso("Curtosis (exceso)", "g2 = Σ(xi − x̄)⁴·fi / (n·σ⁴) − 3", f"g2 = {fmt(m4)} / {fmt(sigma)}⁴ − 3", f"g2 = {fmt(g2)}")]},
            "curtosis_percentilica": {"valor": r(k_perc), "interpretacion": interp_k, "pasos": [
                paso("Curtosis percentílica", "K = (Q3 − Q1) / (2·(P90 − P10))",
                     f"K = ({fmt(q3)} − {fmt(q1)}) / (2·({fmt(p90)} − {fmt(p10)}))", f"K = {fmt(k_perc)}")]},
        },
    }


def analizar_agrupados(datos=None, intervalos=None, percentiles=None, deciles=None, **opciones):
    if intervalos:
        tabla = tabla_desde_intervalos(intervalos)
    else:
        tabla = tabla_desde_datos(datos, **opciones)
    medidas = medidas_agrupadas(tabla, percentiles, deciles)
    return {
        "tipo": "agrupados",
        "parametros": tabla["parametros"],
        "pasos_construccion": tabla["pasos_construccion"],
        "filas": tabla["filas"],
        "ordenados": tabla["ordenados"],
        **medidas,
    }
