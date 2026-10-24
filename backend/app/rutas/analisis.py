from fastapi import APIRouter, File, HTTPException, UploadFile

from .. import database as db
from ..esquemas import SolicitudAnalisis, SolicitudGuardar
from ..estadistica import analizar_agrupados, analizar_no_agrupados
from ..importar import leer_archivo

router = APIRouter(prefix="/api", tags=["análisis"])

EJEMPLO = [45, 52, 38, 61, 47, 55, 49, 63, 41, 58, 50, 44, 67, 53, 39, 57, 48, 62, 46, 51,
           54, 43, 59, 49, 65, 42, 56, 50, 47, 60, 36, 53, 48, 64, 45, 58, 51, 44, 55, 70]


def calcular(sol: SolicitudAnalisis) -> dict:
    op = sol.opciones
    datos = [int(x) if float(x).is_integer() else x for x in (sol.datos or [])]
    try:
        if sol.tipo == "no_agrupados":
            if not datos:
                raise ValueError("Ingresa los datos a analizar.")
            return analizar_no_agrupados(datos, op.percentiles, op.deciles)
        if sol.intervalos:
            return analizar_agrupados(intervalos=[i.model_dump() for i in sol.intervalos],
                                      percentiles=op.percentiles, deciles=op.deciles)
        if not datos:
            raise ValueError("Ingresa los datos o los intervalos de la tabla.")
        return analizar_agrupados(
            datos=datos, percentiles=op.percentiles, deciles=op.deciles,
            metodo_k=op.metodo_k, k_manual=op.k, amplitud_manual=op.amplitud,
            limite_inicial=op.limite_inicial, modo=op.modo,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/ejemplo")
def ejemplo():
    return {"datos": EJEMPLO, "variable": "Calificaciones del parcial", "unidad": "puntos"}


@router.post("/analizar")
def analizar(sol: SolicitudAnalisis):
    res = calcular(sol)
    n = res["resumen"]["n"] if sol.tipo == "no_agrupados" else res["parametros"]["n"]
    origen = "intervalos" if sol.intervalos else "datos"
    db.registrar("ANALIZAR", f"{sol.tipo.replace('_', ' ')} · n = {n} · desde {origen}")
    return res


@router.post("/importar")
async def importar(archivo: UploadFile = File(...)):
    contenido = await archivo.read()
    if len(contenido) > 2_000_000:
        raise HTTPException(413, "El archivo pesa más de 2 MB.")
    try:
        datos = leer_archivo(archivo.filename or "", contenido)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    if not datos:
        raise HTTPException(422, "No encontré números en el archivo.")
    db.registrar("IMPORTAR", f"{archivo.filename} · {len(datos)} datos")
    return {"datos": datos, "archivo": archivo.filename}


@router.get("/analisis")
def listar():
    return db.listar_analisis()


@router.post("/analisis", status_code=201)
def guardar(sol: SolicitudGuardar):
    res = calcular(sol.solicitud)
    entrada = {"datos": sol.solicitud.datos, "intervalos": [i.model_dump() for i in sol.solicitud.intervalos or []],
               "contexto": sol.contexto.model_dump()}
    nuevo_id = db.guardar_analisis(sol.titulo, sol.solicitud.tipo, entrada,
                                   sol.solicitud.opciones.model_dump(), res, sol.interpretacion)
    db.registrar("GUARDAR", f"#{nuevo_id} · {sol.titulo}")
    return {"id": nuevo_id}


@router.get("/analisis/{analisis_id}")
def obtener(analisis_id: int):
    a = db.obtener_analisis(analisis_id)
    if not a:
        raise HTTPException(404, "Análisis no encontrado.")
    return a


@router.delete("/analisis/{analisis_id}", status_code=204)
def eliminar(analisis_id: int):
    if not db.eliminar_analisis(analisis_id):
        raise HTTPException(404, "Análisis no encontrado.")
    db.registrar("ELIMINAR", f"#{analisis_id}")
