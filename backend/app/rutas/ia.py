from fastapi import APIRouter

from .. import database as db
from .. import ia
from ..esquemas import SolicitudChat, SolicitudInterpretar

router = APIRouter(prefix="/api/ia", tags=["tutor IA"])


@router.post("/interpretar")
async def interpretar(sol: SolicitudInterpretar):
    res = await ia.interpretar(sol.resultado, sol.contexto.model_dump())
    if sol.analisis_id:
        db.actualizar_interpretacion(sol.analisis_id, res["texto"])
    db.registrar("IA_INTERPRETAR", f"fuente: {res['fuente']}")
    return res


@router.post("/chat")
async def chat(sol: SolicitudChat):
    res = await ia.chat(sol.mensaje, [m.model_dump() for m in sol.historial],
                        sol.resultado, sol.contexto.model_dump())
    db.guardar_mensaje(sol.analisis_id, "usuario", sol.mensaje)
    db.guardar_mensaje(sol.analisis_id, "ia", res["texto"])
    db.registrar("IA_CHAT", sol.mensaje[:80])
    return res
