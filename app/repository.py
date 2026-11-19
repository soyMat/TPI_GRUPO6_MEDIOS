"""Repositorios SQLite y servicios de persistencia necesarios para CU_01."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    CambioEstado,
    DetallePrestamo,
    Equipamiento,
    MateriaProyecto,
    Prestamo,
    Restriccion,
    SolicitudPrestamo,
    TipoEquipamiento,
    Usuario,
)
from app.schemas import DatosSolicitud, leer_atributo

ESTADOS_OPERATIVOS = ("OPERATIVO", "DISPONIBLE", "ACTIVO")


def _sin_zona_horaria(fecha: datetime) -> datetime:
    """Normaliza fechas para las comparaciones que realiza SQLite."""
    return fecha.replace(tzinfo=None) if fecha.tzinfo is not None else fecha


class RepositorioCatalogos:
    """Consulta tipos de equipamiento y materias del conjunto de demostracion."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_tipos(self) -> list[dict[str, Any]]:
        consulta = select(TipoEquipamiento).order_by(TipoEquipamiento.nombre)
        return [
            {
                "id": tipo.codigo,
                "nombre": tipo.nombre,
                "alta_gama": bool(tipo.alta_gama),
            }
            for tipo in self.session.scalars(consulta).all()
        ]

    def listar_materias(self) -> list[dict[str, str]]:
        consulta = select(MateriaProyecto).order_by(MateriaProyecto.nombre)
        return [
            {"id": str(materia.id), "nombre": materia.nombre}
            for materia in self.session.scalars(consulta).all()
        ]

    def obtener_tipo(self, tipo_id: str) -> TipoEquipamiento:
        tipo = self.session.scalar(
            select(TipoEquipamiento).where(TipoEquipamiento.codigo == tipo_id)
        )
        if tipo is None:
            raise LookupError(f"Tipo de equipamiento inexistente: {tipo_id}")
        return tipo

    def obtener_materia(self, materia_id: str) -> MateriaProyecto:
        try:
            identificador = UUID(str(materia_id))
        except (ValueError, AttributeError) as error:
            raise LookupError(f"Identificador de materia invalido: {materia_id}") from error

        materia = self.session.scalar(
            select(MateriaProyecto).where(MateriaProyecto.id == identificador)
        )
        if materia is None:
            raise LookupError(f"Materia inexistente: {materia_id}")
        return materia


class CalendarioRecursos:
    """Calcula disponibilidad real y recupera restricciones vigentes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def unidades_disponibles(
        self, tipo_id: str, desde: datetime, hasta: datetime
    ) -> int:
        desde_local = _sin_zona_horaria(desde)
        hasta_local = _sin_zona_horaria(hasta)

        total_operativos = self.session.scalar(
            select(func.count(Equipamiento.id)).where(
                Equipamiento.tipo_codigo == tipo_id,
                func.upper(Equipamiento.estado).in_(ESTADOS_OPERATIVOS),
            )
        ) or 0

        # Las solicitudes pendientes no ocupan unidades. Solo se cuentan prestamos
        # efectivos que se solapan con el periodo solicitado.
        ocupados = self.session.scalar(
            select(func.count(func.distinct(DetallePrestamo.equipamiento_id)))
            .join(Prestamo, DetallePrestamo.prestamo_id == Prestamo.id)
            .join(Equipamiento, DetallePrestamo.equipamiento_id == Equipamiento.id)
            .where(
                Equipamiento.tipo_codigo == tipo_id,
                func.upper(Equipamiento.estado).in_(ESTADOS_OPERATIVOS),
                Prestamo.desde < hasta_local,
                desde_local < Prestamo.hasta,
            )
        ) or 0

        return max(0, int(total_operativos) - int(ocupados))

    def consultar_restricciones(
        self, usuario: Any, _tipo: Any, _desde: datetime, _hasta: datetime
    ) -> list[Restriccion]:
        usuario_id = leer_atributo(usuario, "id")
        if usuario_id is None:
            return []
        consulta = select(Restriccion).where(
            Restriccion.estudiante_id == usuario_id,
        )
        return list(self.session.scalars(consulta).all())


def crear_solicitud_prestamo(
    datos: DatosSolicitud,
    usuario: Any,
    tipo: TipoEquipamiento,
    materia: MateriaProyecto,
    requiere_aval: bool,
) -> SolicitudPrestamo:
    """Construye la solicitud; ControlPrestamos conserva la responsabilidad creadora."""
    return SolicitudPrestamo(
        usuario_id=leer_atributo(usuario, "id"),
        tipo_codigo=tipo.codigo,
        cantidad=datos.cantidad,
        desde=_sin_zona_horaria(datos.desde),
        hasta=_sin_zona_horaria(datos.hasta),
        materia_id=materia.id,
        requiere_aval=requiere_aval,
        estado="PENDIENTE_SOLICITADA",
        materia=materia,
    )


class AuditorSolicitudes:
    """Agrega el cambio inicial al historial antes del guardado transaccional."""

    def registrar_alta(
        self, solicitud: SolicitudPrestamo, usuario: Any
    ) -> CambioEstado:
        cambio = CambioEstado(
            actor_id=leer_atributo(usuario, "id"),
            anterior=None,
            nuevo=solicitud.estado,
        )
        solicitud.cambios_estado.append(cambio)
        return cambio


class RepositorioSolicitudes:
    """Guarda solicitud e historial juntos y lista las solicitudes de un usuario."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def guardar_con_historial(self, solicitud: SolicitudPrestamo) -> SolicitudPrestamo:
        try:
            self.session.add(solicitud)
            self.session.commit()
            self.session.refresh(solicitud)
            return solicitud
        except Exception:
            self.session.rollback()
            raise

    def listar_de(self, usuario_id: Any) -> list[dict[str, Any]]:
        consulta = (
            select(SolicitudPrestamo, TipoEquipamiento, MateriaProyecto)
            .join(
                TipoEquipamiento,
                SolicitudPrestamo.tipo_codigo == TipoEquipamiento.codigo,
            )
            .join(
                MateriaProyecto,
                SolicitudPrestamo.materia_id == MateriaProyecto.id,
            )
            .where(SolicitudPrestamo.usuario_id == usuario_id)
            .order_by(
                SolicitudPrestamo.creada_en.desc(),
                SolicitudPrestamo.numero.desc(),
            )
        )
        filas = self.session.execute(consulta).all()
        return [
            {
                "numero": str(solicitud.numero),
                "estado": solicitud.estado,
                "tipo": tipo.nombre,
                "cantidad": solicitud.cantidad,
                "desde": solicitud.desde,
                "hasta": solicitud.hasta,
                "materia": materia.nombre,
                "requiere_aval": bool(solicitud.requiere_aval),
            }
            for solicitud, tipo, materia in filas
        ]


class ResolutorUsuarioDemo:
    """Resuelve el alias ficticio enviado en X-Usuario-Demo."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def __call__(self, alias: str) -> Usuario:
        usuario = self.session.scalar(select(Usuario).where(Usuario.alias == alias))
        if usuario is None:
            raise KeyError(f"Usuario demo desconocido: {alias}")
        return usuario
