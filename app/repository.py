"""Repositorios SQLite/SQLAlchemy, auditoría y calendario de recursos para CU_01."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

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


def _sin_tz(fecha: datetime) -> datetime:
    """Normaliza datetimes a naive para comparaciones consistentes con SQLite."""
    return fecha.replace(tzinfo=None) if fecha.tzinfo is not None else fecha


class RepositorioCatalogos:
    """Consulta catálogos de tipos de equipamiento y materias."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_tipos(self) -> list[TipoEquipamiento]:
        consulta = select(TipoEquipamiento).order_by(TipoEquipamiento.nombre)
        return list(self.session.scalars(consulta).all())

    def listar_materias(self) -> list[dict[str, str]]:
        consulta = select(MateriaProyecto).order_by(MateriaProyecto.nombre)
        materias = self.session.scalars(consulta).all()
        return [{"id": str(m.id), "nombre": m.nombre} for m in materias]

    def obtener_tipo(self, tipo_id: str) -> TipoEquipamiento:
        consulta = select(TipoEquipamiento).where(TipoEquipamiento.codigo == tipo_id)
        tipo = self.session.scalar(consulta)
        if tipo is None:
            raise LookupError(f"Tipo de equipamiento inexistente: {tipo_id}")
        return tipo

    def obtener_materia(self, materia_id: str) -> MateriaProyecto:
        try:
            uid = UUID(str(materia_id))
        except (ValueError, AttributeError) as error:
            raise LookupError(f"Identificador de materia inválido: {materia_id}") from error

        consulta = select(MateriaProyecto).where(MateriaProyecto.id == uid)
        materia = self.session.scalar(consulta)
        if materia is None:
            raise LookupError(f"Materia inexistente: {materia_id}")
        return materia


class CalendarioRecursos:
    """Experto en disponibilidad física y restricciones vigentes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def unidades_disponibles(
        self, tipo_id: str, desde: datetime, hasta: datetime
    ) -> int:
        desde_naive = _sin_tz(desde)
        hasta_naive = _sin_tz(hasta)

        total_operativos = (
            self.session.scalar(
                select(func.count(Equipamiento.id)).where(
                    Equipamiento.tipo_codigo == tipo_id,
                    func.upper(Equipamiento.estado).in_(ESTADOS_OPERATIVOS),
                )
            )
            or 0
        )

        # Solo préstamos efectivos (Prestamo + DetallePrestamo) ocupan unidades;
        # las solicitudes en PENDIENTE_SOLICITADA no restan disponibilidad.
        ocupados = (
            self.session.scalar(
                select(func.count(func.distinct(DetallePrestamo.equipamiento_id)))
                .join(Prestamo, DetallePrestamo.prestamo_id == Prestamo.id)
                .join(Equipamiento, DetallePrestamo.equipamiento_id == Equipamiento.id)
                .where(
                    Equipamiento.tipo_codigo == tipo_id,
                    func.upper(Equipamiento.estado).in_(ESTADOS_OPERATIVOS),
                    Prestamo.desde < hasta_naive,
                    desde_naive < Prestamo.hasta,
                )
            )
            or 0
        )

        return max(0, int(total_operativos) - int(ocupados))

    def consultar_restricciones(
        self, usuario: Any, _tipo: Any, _desde: datetime, _hasta: datetime
    ) -> list[Restriccion]:
        usuario_id = leer_atributo(usuario, "id")
        if usuario_id is None:
            return []
        consulta = select(Restriccion).where(
            Restriccion.estudiante_id == usuario_id,
            Restriccion.activa.is_(True),
        )
        return list(self.session.scalars(consulta).all())


def crear_solicitud_prestamo(
    datos: DatosSolicitud,
    usuario: Any,
    tipo: TipoEquipamiento,
    materia: MateriaProyecto,
    requiere_aval: bool,
) -> SolicitudPrestamo:
    """Fábrica inyectada en ControlPrestamos para instanciar SolicitudPrestamo."""
    return SolicitudPrestamo(
        usuario_id=usuario.id,
        tipo_codigo=tipo.codigo,
        cantidad=datos.cantidad,
        desde=_sin_tz(datos.desde),
        hasta=_sin_tz(datos.hasta),
        materia_id=materia.id,
        requiere_aval=requiere_aval,
        estado="PENDIENTE_SOLICITADA",
        tipo=tipo,
        materia=materia,
    )


class AuditorSolicitudes:
    """Registra el historial de cambios de estado de la solicitud (RNF-19)."""

    def registrar_alta(
        self, solicitud: SolicitudPrestamo, usuario: Any
    ) -> CambioEstado:
        return CambioEstado(
            solicitud=solicitud,
            actor_id=leer_atributo(usuario, "id"),
            anterior=None,
            nuevo=solicitud.estado,
        )


class RepositorioSolicitudes:
    """Persistencia transaccional y consulta de solicitudes del usuario."""

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
            select(SolicitudPrestamo)
            .options(
                selectinload(SolicitudPrestamo.tipo),
                selectinload(SolicitudPrestamo.materia),
            )
            .where(SolicitudPrestamo.usuario_id == usuario_id)
            .order_by(
                SolicitudPrestamo.creada_en.desc(),
                SolicitudPrestamo.numero.desc(),
            )
        )
        solicitudes = self.session.scalars(consulta).all()
        return [
            {
                "numero": str(sol.numero),
                "estado": sol.estado,
                "tipo": sol.tipo.nombre if sol.tipo else sol.tipo_codigo,
                "cantidad": sol.cantidad,
                "desde": sol.desde,
                "hasta": sol.hasta,
                "materia": sol.materia.nombre if sol.materia else str(sol.materia_id),
                "requiere_aval": bool(sol.requiere_aval),
            }
            for sol in solicitudes
        ]


class ResolutorUsuarioDemo:
    """Resuelve el alias enviado en X-Usuario-Demo contra usuarios precargados."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def __call__(self, alias: str) -> Usuario:
        consulta = select(Usuario).where(Usuario.alias == alias)
        usuario = self.session.scalar(consulta)
        if usuario is None:
            raise KeyError(f"Usuario demo desconocido: {alias}")
        return usuario