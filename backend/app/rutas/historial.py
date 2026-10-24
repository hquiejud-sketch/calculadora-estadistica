from fastapi import APIRouter, Query

from .. import database as db

router = APIRouter(prefix="/api/historial", tags=["historial"])


@router.get("")
def listar(limite: int = Query(100, ge=1, le=500)):
    return db.listar_historial(limite)


@router.delete("", status_code=204)
def borrar():
    db.borrar_historial()
