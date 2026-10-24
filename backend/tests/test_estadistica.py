import statistics as st

import pytest

from app.estadistica import analizar_agrupados, analizar_no_agrupados

MUESTRA = [45, 52, 38, 61, 47, 55, 49, 63, 41, 58, 50, 44, 67, 53, 39, 57, 48, 62, 46, 51,
           54, 43, 59, 49, 65, 42, 56, 50, 47, 60, 36, 53, 48, 64, 45, 58, 51, 44, 55, 70]


def test_no_agrupados_contra_statistics():
    res = analizar_no_agrupados(MUESTRA)
    tc, disp = res["tendencia_central"], res["dispersion"]
    assert tc["media"]["valor"] == pytest.approx(st.mean(MUESTRA))
    assert tc["mediana"]["valor"] == pytest.approx(st.median(MUESTRA))
    assert disp["varianza"]["valor"] == pytest.approx(st.variance(MUESTRA))
    assert disp["varianza"]["poblacional"] == pytest.approx(st.pvariance(MUESTRA))
    assert disp["desviacion"]["valor"] == pytest.approx(st.stdev(MUESTRA))
    assert tc["media_geometrica"]["valor"] == pytest.approx(st.geometric_mean(MUESTRA))
    assert tc["media_armonica"]["valor"] == pytest.approx(st.harmonic_mean(MUESTRA))
    # Cuartiles por posición k(n+1)/4 = método "exclusive" de statistics.
    q = st.quantiles(MUESTRA, n=4, method="exclusive")
    assert [c["valor"] for c in res["posicion"]["cuartiles"]] == pytest.approx(q)


def test_no_agrupados_moda():
    res = analizar_no_agrupados([1, 2, 2, 3, 3, 4])
    assert res["tendencia_central"]["moda"]["valores"] == [2, 3]
    assert res["tendencia_central"]["moda"]["tipo"] == "bimodal"
    res = analizar_no_agrupados([1, 2, 3])
    assert res["tendencia_central"]["moda"]["tipo"] == "amodal"


def test_agrupados_sturges_continuo():
    res = analizar_agrupados(datos=MUESTRA, percentiles=[17])
    p = res["parametros"]
    assert p["k"] == 6 and p["amplitud"] == 6
    assert [f["fi"] for f in res["filas"]] == [4, 9, 11, 8, 6, 2]
    assert res["filas"][-1]["Fi"] == 40
    tc = res["tendencia_central"]
    assert tc["media"]["valor"] == pytest.approx(52.35)
    assert tc["mediana"]["valor"] == pytest.approx(51.8182, abs=1e-4)
    assert tc["moda"]["valores"][0]["valor"] == pytest.approx(50.4)
    assert res["dispersion"]["varianza"]["valor"] == pytest.approx(67.3615, abs=1e-4)
    assert res["posicion"]["percentiles"][0]["valor"] == pytest.approx(43.8667, abs=1e-4)


def test_agrupados_discreto_limites_reales():
    res = analizar_agrupados(datos=MUESTRA, modo="discreto")
    f0 = res["filas"][0]
    assert (f0["li"], f0["ls"], f0["lri"], f0["lrs"]) == (36, 41, 35.5, 41.5)
    assert res["tendencia_central"]["media"]["valor"] == pytest.approx(51.85)


def test_agrupados_desde_intervalos():
    intervalos = [{"li": 10, "ls": 20, "fi": 5}, {"li": 20, "ls": 30, "fi": 8},
                  {"li": 30, "ls": 40, "fi": 12}, {"li": 40, "ls": 50, "fi": 5}]
    res = analizar_agrupados(intervalos=intervalos)
    assert res["parametros"]["n"] == 30
    # x̄ = (15·5 + 25·8 + 35·12 + 45·5) / 30 = 920 / 30
    assert res["tendencia_central"]["media"]["valor"] == pytest.approx(920 / 30)
    # Me: pos = 15 -> clase 3, Me = 30 + (15 − 13)/12·10
    assert res["tendencia_central"]["mediana"]["valor"] == pytest.approx(30 + 2 / 12 * 10)


def test_intervalos_con_limites_aparentes():
    intervalos = [{"li": 20, "ls": 24, "fi": 3}, {"li": 25, "ls": 29, "fi": 7}, {"li": 30, "ls": 34, "fi": 4}]
    res = analizar_agrupados(intervalos=intervalos)
    assert res["parametros"]["modo"] == "discreto"
    assert res["filas"][0]["lri"] == 19.5 and res["filas"][0]["A"] == 5


def test_errores():
    with pytest.raises(ValueError):
        analizar_no_agrupados([5])
    with pytest.raises(ValueError):
        analizar_agrupados(intervalos=[{"li": 10, "ls": 5, "fi": 1}, {"li": 5, "ls": 1, "fi": 1}])
