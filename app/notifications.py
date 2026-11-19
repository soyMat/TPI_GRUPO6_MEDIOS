"""Avisos internos para solicitudes de CU_01 que requieren aval."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AsignacionDocenteMateria, Docente, Notificacion
from app.schemas import leer_atributo


class CanalPlataforma:
    """Canal interno que incorpora cada aviso a la transaccion actual."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def enviar(self, aviso: Notificacion) -> None:
        self.session.add(aviso)


class NotificadorSolicitudes:
    """Crea avisos para docentes asignados y habilitados para avalar la materia."""

    def __init__(self, session: Session, canal: CanalPlataforma | None = None) -> None:
        self.session = session
        self.canal = canal or CanalPlataforma(session)

    def avisar_aval(self, solicitud: Any, materia: Any) -> list[Notificacion]:
        hoy = date.today()
        docentes = self.session.scalars(
            select(Docente)
            .join(
                AsignacionDocenteMateria,
                AsignacionDocenteMateria.docente_id == Docente.id,
            )
            .where(
                AsignacionDocenteMateria.materia_id
                == leer_atributo(materia, "id"),
                AsignacionDocenteMateria.habilita_aval.is_(True),
                AsignacionDocenteMateria.desde <= hoy,
                AsignacionDocenteMateria.hasta >= hoy,
            )
            .order_by(Docente.nombre_completo)
        ).all()
        if not docentes:
            raise RuntimeError(
                "No hay docentes asignados y habilitados para registrar el aviso de aval."
            )

        numero = leer_atributo(solicitud, "numero")
        nombre_materia = leer_atributo(materia, "nombre", "materia asignada")
        avisos = [
            Notificacion(
                destinatario_id=docente.id,
                solicitud_numero=numero,
                mensaje=(
                    f"Solicitud #{numero} pendiente de aval docente para "
                    f"{nombre_materia}."
                ),
            )
            for docente in docentes
        ]

        try:
            for aviso in avisos:
                self.canal.enviar(aviso)
            self.session.commit()
            return avisos
        except Exception:
            self.session.rollback()
            raise
