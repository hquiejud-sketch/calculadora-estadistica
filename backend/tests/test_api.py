import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "prueba.db")
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_flujo_completo():
    with TestClient(app) as c:
        assert c.get("/api/salud").json()["ia"] == "local"
        datos = c.get("/api/ejemplo").json()["datos"]

        sol = {"tipo": "agrupados", "datos": datos, "opciones": {"percentiles": [17]}}
        res = c.post("/api/analizar", json=sol)
        assert res.status_code == 200
        assert res.json()["tendencia_central"]["media"]["valor"] == 52.35

        r2 = c.post("/api/analizar", json={"tipo": "no_agrupados", "datos": datos})
        assert r2.status_code == 200

        g = c.post("/api/analisis", json={"titulo": "Parcial 1", "solicitud": sol,
                                          "contexto": {"variable": "notas", "unidad": "pts"}})
        assert g.status_code == 201
        aid = g.json()["id"]
        assert c.get("/api/analisis").json()[0]["titulo"] == "Parcial 1"

        it = c.post("/api/ia/interpretar", json={"resultado": res.json(), "analisis_id": aid}).json()
        assert it["fuente"] == "local" and "## Resumen" in it["texto"]
        ch = c.post("/api/ia/chat", json={"mensaje": "¿qué es la mediana?", "analisis_id": aid}).json()
        assert "mediana" in ch["texto"].lower()

        det = c.get(f"/api/analisis/{aid}").json()
        assert len(det["mensajes"]) == 2 and det["interpretacion"]

        acciones = [h["accion"] for h in c.get("/api/historial").json()]
        assert {"ANALIZAR", "GUARDAR", "IA_INTERPRETAR", "IA_CHAT"} <= set(acciones)

        assert c.delete(f"/api/analisis/{aid}").status_code == 204
        assert c.get(f"/api/analisis/{aid}").status_code == 404


def test_importar_csv_y_errores():
    with TestClient(app) as c:
        r = c.post("/api/importar", files={"archivo": ("d.csv", b"x\n1,5\n2.5\n7", "text/csv")})
        assert r.json()["datos"] == [1, 5, 2.5, 7]
        r = c.post("/api/analizar", json={"tipo": "no_agrupados", "datos": [3]})
        assert r.status_code == 422
