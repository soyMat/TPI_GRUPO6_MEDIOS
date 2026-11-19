"""Notificaciones internas en plataforma para solicitudes que requieren aval."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Docente, Notificacion
from app.schemas import leer_atributo


class CanalPlataforma:
    """Implementación concreta del canal interno en plataforma (DCD v9.3)."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def enviar(
        self,
        destinatario_id: UUID,
        mensaje: str,
        solicitud_numero: int | None = None,
    ) -> Notificacion:
        try:
            notificacion = Notificacion(
                destinatario_id=destinatario_id,
                solicitud_numero=solicitud_numero,
                mensaje=mensaje,
            )
            self.session.add(notificacion)
            self.session.commit()
            self.session.refresh(notificacion)
            return notificacion
        except Exception:
            self.session.rollback()
            raise


class NotificadorSolicitudes:
    """Genera el aviso interno cuando CU_01 determina requiere_aval=True."""

    def __init__(self, session: Session, canal: CanalPlataforma | None = None) -> None:
        self.session = session
        self.canal = canal or CanalPlataforma(session)

    def avisar_aval(self, solicitud: Any, materia: Any) -> Notificacion:
        docente = self.session.scalar(select(Docente).limit(1))
        if docente is None:
            raise RuntimeError(
                "No existe un docente destinatario para registrar el aviso de aval."
            )

        numero = leer_atributo(solicitud, "numero")
        nombre_materia = leer_atributo(materia, "nombre", "materia asignada")
        mensaje = (
            f"Solicitud #{numero} pendiente de aval docente para {nombre_materia}."
        )
        return self.canal.enviar(
            destinatario_id=docente.id,
            mensaje=mensaje,
            solicitud_numero=numero,
        )