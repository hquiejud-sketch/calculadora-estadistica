"""Tutor de IA con Google Gemini (API REST, sin SDK).

Si no hay clave o Gemini falla, se usa un respaldo local para que la app
siempre responda algo útil.
"""

import asyncio
import json

import httpx

from . import config
from .estadistica.utilidades import fmt

URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
# Si el modelo principal está saturado, se prueban estos en orden.
MODELOS_RESPALDO = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]

SISTEMA = """Eres "Estadi", un tutor de Estadística para estudiantes universitarios de ingeniería en Guatemala.
Escribes en español claro y directo, con frases cortas.
Recibes resultados YA CALCULADOS por la calculadora.
Reglas:
- NO recalcules ni inventes cifras: usa solo los valores que recibes.
- Explica qué significa cada medida en el contexto de los datos.
- Usa Markdown simple (## títulos, listas, **negritas**). Nada de tablas enormes.
- Si te preguntan algo fuera de estadística, redirige amablemente al tema."""

INSTRUCCION_INTERPRETAR = """Redacta la interpretación de este análisis para un reporte universitario con estas secciones:
## Resumen
## Tendencia central
## Dispersión
## Posición
## Forma de la distribución
## Conclusión
Máximo 350 palabras."""


def resumir(resultado: dict, contexto: dict | None = None) -> dict:
    """Reduce el resultado a lo esencial para mandarlo al modelo."""
    tc, disp, pos, forma = (resultado["tendencia_central"], resultado["dispersion"],
                            resultado["posicion"], resultado["forma"])
    base = {
        "contexto": contexto or {},
        "tipo": resultado["tipo"],
        "media": tc["media"]["valor"],
        "mediana": tc["mediana"]["valor"],
        "moda": ([m["valor"] for m in tc["moda"]["valores"]] if resultado["tipo"] == "agrupados"
                 else tc["moda"]["valores"]),
        "varianza_muestral": disp["varianza"]["valor"],
        "desviacion_estandar": disp["desviacion"]["valor"],
        "cv_pct": disp["coeficiente_variacion"]["valor"],
        "rango_intercuartil": disp["rango_intercuartil"]["valor"],
        "cuartiles": {f"Q{q['k']}": q["valor"] for q in pos["cuartiles"]},
        "percentiles": {f"P{q['k']}": q["valor"] for q in pos["percentiles"]},
        "deciles": {f"D{q['k']}": q["valor"] for q in pos["deciles"]},
        "asimetria": {k: {"valor": v["valor"], "lectura": v.get("interpretacion")}
                      for k, v in forma.items()},
    }
    if resultado["tipo"] == "agrupados":
        base["n"] = resultado["parametros"]["n"]
        base["tabla"] = [{"clase": f["intervalo"], "xi": f["xi"], "fi": f["fi"], "Fi": f["Fi"],
                          "pct": round(f["pct"], 2)} for f in resultado["filas"]]
    else:
        r = resultado["resumen"]
        base.update({"n": r["n"], "min": r["minimo"], "max": r["maximo"], "rango": r["rango"],
                     "atipicos": resultado["caja"]["atipicos"]})
    return base


async def _llamar_gemini(contents: list) -> str:
    cuerpo = {
        "systemInstruction": {"parts": [{"text": SISTEMA}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1500},
    }
    headers = {"x-goog-api-key": config.GEMINI_API_KEY, "Content-Type": "application/json"}
    ultimo_error = None
    bitacora = []  # qué respondió cada modelo, para diagnosticar
    modelos = dict.fromkeys([config.GEMINI_MODEL, *MODELOS_RESPALDO])
    async with httpx.AsyncClient(timeout=60) as cliente:
        for modelo in modelos:
            for intento in range(2):  # un reintento por modelo si está saturado
                try:
                    resp = await cliente.post(URL.format(modelo=modelo), headers=headers, json=cuerpo)
                except httpx.HTTPError as e:
                    ultimo_error = f"Sin conexión con Gemini ({e.__class__.__name__})"
                    bitacora.append(f"{modelo}: sin conexión")
                    print(f"[IA] {modelo}: sin conexión ({e})")
                    break
                if resp.status_code == 200:
                    data = resp.json()
                    partes = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    texto = "".join(p.get("text", "") for p in partes).strip()
                    if texto:
                        print(f"[IA] {modelo}: OK")
                        return texto
                    ultimo_error = "Gemini respondió vacío."
                    break
                try:
                    ultimo_error = resp.json().get("error", {}).get("message", resp.text)
                except ValueError:
                    ultimo_error = resp.text
                bitacora.append(f"{modelo}: error {resp.status_code}")
                print(f"[IA] {modelo}: error {resp.status_code} - {ultimo_error[:150]}")
                if resp.status_code in (401, 403):
                    raise RuntimeError(f"Clave de Gemini inválida o sin permiso: {ultimo_error}")
                if resp.status_code in (500, 503) and intento == 0:
                    await asyncio.sleep(1.5)  # saturado: esperar y reintentar
                    continue
                break  # 404 (modelo no existe), 429 (cuota) o 503 repetido: probar el siguiente modelo
    raise RuntimeError(f"{ultimo_error or 'Error desconocido'} | Intentos: {'; '.join(bitacora)}")


# ---------------------------------------------------------------------------
# Respaldo local (sin internet)
# ---------------------------------------------------------------------------

def interpretacion_local(res: dict, contexto: dict | None = None) -> str:
    r = resumir(res, contexto)
    var = (contexto or {}).get("variable") or "la variable"
    unidad = (contexto or {}).get("unidad") or ""
    media, me, s, cv = r["media"], r["mediana"], r["desviacion_estandar"], r["cv_pct"]
    moda = ", ".join(fmt(m) for m in r["moda"]) if r["moda"] else "no hay moda"
    asim = res["forma"]["asimetria_pearson"]
    q = r["cuartiles"]
    if cv is None:
        lectura_cv = "no se puede calcular porque la media es 0"
    elif cv < 15:
        lectura_cv = "los datos son homogéneos: la media representa bien al grupo"
    elif cv < 30:
        lectura_cv = "la variabilidad es moderada"
    else:
        lectura_cv = "los datos son muy dispersos: la media no representa bien al grupo"
    return f"""## Resumen
Se analizaron **{r['n']} datos** de {var} ({'datos agrupados' if r['tipo'] == 'agrupados' else 'datos no agrupados'}).

## Tendencia central
- Media: **{fmt(media)} {unidad}**. Es el valor promedio.
- Mediana: **{fmt(me)} {unidad}**. La mitad de los datos está por debajo de este valor.
- Moda: **{moda}**. Es el valor más frecuente.

## Dispersión
- Desviación estándar: **{fmt(s)} {unidad}**. En promedio, los datos se alejan eso de la media.
- Coeficiente de variación: **{fmt(cv, 2)} %**. Esto indica que {lectura_cv}.

## Posición
- El 25 % de los datos está por debajo de **{fmt(q['Q1'])}** (Q1) y el 75 % por debajo de **{fmt(q['Q3'])}** (Q3).
- El 50 % central de los datos está entre esos dos valores.

## Forma de la distribución
- Asimetría de Pearson: **{fmt(asim['valor'])}** → {asim['interpretacion'].lower()}.

## Conclusión
La media ({fmt(media)}) y la mediana ({fmt(me)}) {'son cercanas, así que la distribución es bastante equilibrada' if abs(media - me) < 0.1 * (s or 1) else 'se separan, lo que confirma el sesgo de la distribución'}.

> *Interpretación generada en modo local. Configura tu clave de Gemini en `backend/.env` para obtener explicaciones con IA.*"""


GLOSARIO = {
    "media": "La **media** es el promedio: sumas todos los datos y divides entre n. En agrupados se usa x̄ = Σ(xi·fi)/n con las marcas de clase.",
    "mediana": "La **mediana** es el valor que deja 50 % de los datos abajo y 50 % arriba. En agrupados se interpola dentro de la clase donde Fi ≥ n/2.",
    "moda": "La **moda** es el valor más repetido. En agrupados se usa la fórmula de Czuber: Mo = Li + (Δ1/(Δ1+Δ2))·A.",
    "varianza": "La **varianza** mide qué tanto se alejan los datos de la media, al cuadrado. La muestral divide entre n − 1.",
    "desviaci": "La **desviación estándar** es la raíz de la varianza. Está en las mismas unidades que los datos.",
    "coeficiente": "El **coeficiente de variación** es (s/x̄)·100. Menos de 15 % suele indicar datos homogéneos.",
    "cuartil": "Los **cuartiles** dividen los datos en 4 partes iguales: Q1 (25 %), Q2 (50 % = mediana) y Q3 (75 %).",
    "percentil": "Los **percentiles** dividen los datos en 100 partes. P90 deja 90 % de los datos por debajo.",
    "decil": "Los **deciles** dividen los datos en 10 partes. D3 deja 30 % de los datos por debajo.",
    "sturges": "La **regla de Sturges** da el número de clases: k = 1 + 3.322·log₁₀(n).",
    "amplitud": "La **amplitud** de clase es A = R/k, redondeada hacia arriba a la precisión de los datos.",
    "asimetr": "La **asimetría** indica hacia dónde se carga la distribución. Positiva: cola a la derecha. Negativa: cola a la izquierda.",
    "curtosis": "La **curtosis** mide qué tan apuntada es la distribución comparada con la normal.",
    "ojiva": "La **ojiva** es la gráfica de frecuencias acumuladas. Sirve para leer cuartiles y percentiles a ojo.",
    "histograma": "El **histograma** muestra barras pegadas con la frecuencia de cada clase.",
}


def chat_local(mensaje: str) -> str:
    texto = mensaje.lower()
    respuestas = [v for k, v in GLOSARIO.items() if k in texto]
    if respuestas:
        return "\n\n".join(respuestas[:3]) + "\n\n> *Respuesta en modo local. Con tu clave de Gemini puedo explicarte con tus propios datos.*"
    return ("Ahorita estoy en **modo local** (sin clave de Gemini), así que solo explico conceptos básicos: "
            "media, mediana, moda, varianza, desviación, cuartiles, percentiles, deciles, Sturges, amplitud, "
            "asimetría, curtosis, histograma u ojiva. Pregúntame por alguno.")


# ---------------------------------------------------------------------------
# API pública del módulo
# ---------------------------------------------------------------------------

async def interpretar(resultado: dict, contexto: dict | None = None) -> dict:
    if not config.ia_configurada():
        return {"texto": interpretacion_local(resultado, contexto), "fuente": "local",
                "aviso": "No hay clave de Gemini configurada."}
    datos = json.dumps(resumir(resultado, contexto), ensure_ascii=False)
    try:
        texto = await _llamar_gemini([{"role": "user", "parts": [{"text": f"{INSTRUCCION_INTERPRETAR}\n\nResultados:\n{datos}"}]}])
        return {"texto": texto, "fuente": "gemini"}
    except Exception as e:  # noqa: BLE001
        return {"texto": interpretacion_local(resultado, contexto), "fuente": "local",
                "aviso": f"Gemini no respondió: {e}"}


async def chat(mensaje: str, historial: list, resultado: dict | None = None, contexto: dict | None = None) -> dict:
    if not config.ia_configurada():
        return {"texto": chat_local(mensaje), "fuente": "local", "aviso": "No hay clave de Gemini configurada."}
    contents = []
    if resultado:
        datos = json.dumps(resumir(resultado, contexto), ensure_ascii=False)
        contents.append({"role": "user", "parts": [{"text": f"Estos son los resultados de mi análisis actual:\n{datos}"}]})
        contents.append({"role": "model", "parts": [{"text": "Entendido, ya tengo tus resultados. ¿Qué quieres saber?"}]})
    for m in historial[-10:]:
        contents.append({"role": "model" if m["rol"] == "ia" else "user", "parts": [{"text": m["contenido"]}]})
    contents.append({"role": "user", "parts": [{"text": mensaje}]})
    try:
        return {"texto": await _llamar_gemini(contents), "fuente": "gemini"}
    except Exception as e:  # noqa: BLE001
        return {"texto": chat_local(mensaje), "fuente": "local", "aviso": f"Gemini no respondió: {e}"}
