"""Schemas HTTP mínimos para el prototipo CU_01."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatosSolicitud(BaseModel):
    tipo_id: str = Field(min_length=1)
    cantidad: int
    desde: datetime
    hasta: datetime
    materia_id: str = Field(min_length=1)

class ErrorValidacion(BaseModel):
    codigo: str
    mensaje: str
    campo: str | None = None


class ResumenPrevalidacion(BaseModel):
    tipo: str
    cantidad: int
    desde: datetime
    hasta: datetime
    materia: str


class ResultadoValidacionSalida(BaseModel):
    valido: bool
    requiere_aval: bool = False
    errores: list[ErrorValidacion] = Field(default_factory=list)
    resumen: ResumenPrevalidacion | None = None


class TipoEquipamientoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str
    alta_gama: bool = False


class MateriaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str


class SolicitudCreadaSalida(BaseModel):
    numero: str
    estado: str
    requiere_aval: bool = False
    advertencias: list[str] = Field(default_factory=list)


class SolicitudListadoSalida(BaseModel):
    """Vista reducida; el repositorio entrega estos datos sin exponer entidades ORM."""

    model_config = ConfigDict(from_attributes=True)

    numero: str
    estado: str
    tipo: str
    cantidad: int
    desde: datetime
    hasta: datetime
    materia: str
    requiere_aval: bool = False


class RespuestaError(BaseModel):
    codigo: str
    mensaje: str
    errores: list[ErrorValidacion] = Field(default_factory=list)


def leer_atributo(objeto: Any, nombre: str, predeterminado: Any = None) -> Any:
    if isinstance(objeto, dict):
        return objeto.get(nombre, predeterminado)
    return getattr(objeto, nombre, predeterminado)
