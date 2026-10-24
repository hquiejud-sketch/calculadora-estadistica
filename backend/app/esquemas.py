"""Modelos de entrada de la API (validación automática con Pydantic)."""

from typing import Literal

from pydantic import BaseModel, Field


class Intervalo(BaseModel):
    li: float
    ls: float
    fi: int = Field(ge=0)


class Opciones(BaseModel):
    metodo_k: Literal["sturges", "raiz", "manual"] = "sturges"
    k: int | None = Field(default=None, ge=1, le=50)
    amplitud: float | None = Field(default=None, gt=0)
    limite_inicial: float | None = None
    modo: Literal["continuo", "discreto"] = "continuo"
    percentiles: list[int] = Field(default_factory=lambda: [10, 90])
    deciles: list[int] = Field(default_factory=list)


class SolicitudAnalisis(BaseModel):
    tipo: Literal["no_agrupados", "agrupados"]
    datos: list[float] | None = None
    intervalos: list[Intervalo] | None = None
    opciones: Opciones = Field(default_factory=Opciones)


class Contexto(BaseModel):
    variable: str = ""
    unidad: str = ""
    descripcion: str = ""


class SolicitudGuardar(BaseModel):
    titulo: str = Field(min_length=1, max_length=120)
    solicitud: SolicitudAnalisis
    contexto: Contexto = Field(default_factory=Contexto)
    interpretacion: str | None = None


class SolicitudInterpretar(BaseModel):
    resultado: dict
    contexto: Contexto = Field(default_factory=Contexto)
    analisis_id: int | None = None


class Mensaje(BaseModel):
    rol: Literal["usuario", "ia"]
    contenido: str


class SolicitudChat(BaseModel):
    mensaje: str = Field(min_length=1, max_length=2000)
    historial: list[Mensaje] = Field(default_factory=list)
    resultado: dict | None = None
    contexto: Contexto = Field(default_factory=Contexto)
    analisis_id: int | None = None
