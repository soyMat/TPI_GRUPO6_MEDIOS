"""Schemas HTTP mínimos para el prototipo CU_01."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Este DTO valida solamente la forma de la entrada. Las reglas de cantidad,
# período, disponibilidad y elegibilidad pertenecen a PoliticaPrestamo.
class DatosSolicitud(BaseModel):
    tipo_id: str = Field(min_length=1)
    cantidad: int
    desde: datetime
    hasta: datetime
    materia_id: str = Field(min_length=1)


# Los siguientes schemas fijan el contrato de salida sin exponer modelos ORM.
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


def leer_atributo(objeto: Any, nombre: str, predeterminado: Any = None) -> Any:
    """Lee por igual diccionarios de prueba y objetos del dominio integrados."""

    if isinstance(objeto, dict):
        return objeto.get(nombre, predeterminado)
    return getattr(objeto, nombre, predeterminado)
