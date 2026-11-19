"""Pruebas de integracion de CU_01 contra una base SQLite real."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.main import crear_app_integrada
from app.models import (
    CambioEstado,
    DetallePrestamo,
    Equipamiento,
    Notificacion,
    Prestamo,
    SolicitudPrestamo,
)
from scripts.seed_demo import (
    UUID_DOCENTE,
    UUID_DOCENTE_NO_ASIGNADO,
    UUID_EST_COMUN,
    UUID_MAT_PROYECTO2,
    UUID_MAT_TESIS,
)


def _crear_cliente(tmp_path: Path) -> tuple[TestClient, str]:
    ruta = tmp_path / "test_cu01.db"
    database_url = f"sqlite:///{ruta}"
    api = crear_app_integrada(database_url=database_url, montar_estaticos=False)
    return TestClient(api), database_url


def _periodo(dias_desde_hoy: int = 1) -> tuple[datetime, datetime]:
    inicio = (datetime.now() + timedelta(days=dias_desde_hoy)).replace(
        hour=10,
        minute=0,
        second=0,
        microsecond=0,
    )
    return inicio, inicio + timedelta(hours=48)


def _payload(
    tipo_id: str = "CAMARA",
    cantidad: int = 1,
    materia_id: str = str(UUID_MAT_PROYECTO2),
    dias_desde_hoy: int = 1,
) -> dict[str, object]:
    desde, hasta = _periodo(dias_desde_hoy)
    return {
        "tipo_id": tipo_id,
        "cantidad": cantidad,
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "materia_id": materia_id,
    }


def test_inventario_unico_impide_duplicados(tmp_path: Path) -> None:
    _, database_url = _crear_cliente(tmp_path)
    motor = create_engine(database_url)

    with Session(motor) as session:
        session.add(
            Equipamiento(
                numero_inventario="INV-CAM-01",
                tipo_codigo="CAMARA",
                estado="OPERATIVO",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_confirmar_guarda_solicitud_e_historial_juntos(tmp_path: Path) -> None:
    cliente, database_url = _crear_cliente(tmp_path)

    respuesta = cliente.post(
        "/api/solicitudes",
        json=_payload(),
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "PENDIENTE_SOLICITADA"

    motor = create_engine(database_url)
    with Session(motor) as session:
        solicitudes = session.scalars(select(SolicitudPrestamo)).all()
        cambios = session.scalars(select(CambioEstado)).all()
        assert len(solicitudes) == 1
        assert solicitudes[0].usuario_id == UUID_EST_COMUN
        assert len(cambios) == 1
        assert cambios[0].solicitud_numero == solicitudes[0].numero
        assert cambios[0].actor_id == UUID_EST_COMUN
        assert cambios[0].nuevo == "PENDIENTE_SOLICITADA"


def test_solicitud_pendiente_no_ocupa_pero_prestamo_efectivo_si(
    tmp_path: Path,
) -> None:
    cliente, database_url = _crear_cliente(tmp_path)
    payload = _payload(cantidad=2)

    creada = cliente.post(
        "/api/solicitudes",
        json=payload,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert creada.status_code == 201

    sigue_disponible = cliente.post(
        "/api/solicitudes/prevalidar",
        json=payload,
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert sigue_disponible.status_code == 200

    desde = datetime.fromisoformat(str(payload["desde"]))
    hasta = datetime.fromisoformat(str(payload["hasta"]))
    motor = create_engine(database_url)
    with Session(motor) as session:
        equipo = session.scalar(
            select(Equipamiento).where(
                Equipamiento.numero_inventario == "INV-CAM-01"
            )
        )
        prestamo = Prestamo(
            solicitud_numero=int(creada.json()["numero"]),
            desde=desde,
            hasta=hasta,
        )
        prestamo.detalles.append(DetallePrestamo(equipamiento_id=equipo.id))
        session.add(prestamo)
        session.commit()

    sin_cupo = cliente.post(
        "/api/solicitudes/prevalidar",
        json=payload,
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert sin_cupo.status_code == 409
    assert sin_cupo.json()["detail"]["codigo"] == "SIN_DISPONIBILIDAD"


def test_alta_gama_notifica_solo_docente_asignado_y_lista_solicitud(
    tmp_path: Path,
) -> None:
    cliente, database_url = _crear_cliente(tmp_path)
    payload = _payload(
        tipo_id="CINE_PRO",
        materia_id=str(UUID_MAT_TESIS),
        dias_desde_hoy=4,
    )

    confirmacion = cliente.post(
        "/api/solicitudes",
        json=payload,
        headers={"X-Usuario-Demo": "estudiante-elegible"},
    )
    assert confirmacion.status_code == 201
    assert confirmacion.json()["requiere_aval"] is True
    assert confirmacion.json()["advertencias"] == []

    motor = create_engine(database_url)
    with Session(motor) as session:
        avisos = session.scalars(select(Notificacion)).all()
        assert len(avisos) == 1
        assert avisos[0].destinatario_id == UUID_DOCENTE
        assert avisos[0].destinatario_id != UUID_DOCENTE_NO_ASIGNADO

    mias = cliente.get(
        "/api/solicitudes/mias",
        headers={"X-Usuario-Demo": "estudiante-elegible"},
    )
    assert mias.status_code == 200
    assert len(mias.json()) == 1
    assert mias.json()[0]["tipo"] == "Camara Cine 4K"
    assert mias.json()[0]["requiere_aval"] is True


def test_errores_reales_por_datos_restriccion_y_alta_gama(tmp_path: Path) -> None:
    cliente, _ = _crear_cliente(tmp_path)

    incompleta = cliente.post(
        "/api/solicitudes/prevalidar",
        json={"tipo_id": "CAMARA"},
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert incompleta.status_code == 422

    restringida = cliente.post(
        "/api/solicitudes/prevalidar",
        json=_payload(),
        headers={"X-Usuario-Demo": "estudiante-restringido"},
    )
    assert restringida.status_code == 403
    assert restringida.json()["detail"]["codigo"] == "RESTRICCION_ACTIVA"

    no_elegible = cliente.post(
        "/api/solicitudes/prevalidar",
        json=_payload(tipo_id="CINE_PRO"),
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert no_elegible.status_code == 403
    assert no_elegible.json()["detail"]["codigo"] == "NO_ELEGIBLE"


def test_docente_no_recibe_reglas_exclusivas_de_estudiante(tmp_path: Path) -> None:
    cliente, _ = _crear_cliente(tmp_path)
    respuesta = cliente.post(
        "/api/solicitudes",
        json=_payload(tipo_id="CINE_PRO", dias_desde_hoy=7),
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["requiere_aval"] is False


def test_confirmar_revalida_disponibilidad_antes_de_guardar(tmp_path: Path) -> None:
    cliente, database_url = _crear_cliente(tmp_path)
    payload = _payload(cantidad=2, dias_desde_hoy=10)

    prevalidacion = cliente.post(
        "/api/solicitudes/prevalidar",
        json=payload,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert prevalidacion.status_code == 200

    solicitud_base = cliente.post(
        "/api/solicitudes",
        json=payload | {"cantidad": 1},
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert solicitud_base.status_code == 201

    motor = create_engine(database_url)
    with Session(motor) as session:
        equipo = session.scalar(
            select(Equipamiento).where(
                Equipamiento.numero_inventario == "INV-CAM-01"
            )
        )
        session.add(
            Prestamo(
                solicitud_numero=int(solicitud_base.json()["numero"]),
                desde=datetime.fromisoformat(str(payload["desde"])),
                hasta=datetime.fromisoformat(str(payload["hasta"])),
                detalles=[DetallePrestamo(equipamiento_id=equipo.id)],
            )
        )
        session.commit()

    confirmacion = cliente.post(
        "/api/solicitudes",
        json=payload,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert confirmacion.status_code == 409
    assert confirmacion.json()["detail"]["codigo"] == "DISPONIBILIDAD_CAMBIO"

    with Session(motor) as session:
        cantidad = session.scalar(select(func.count(SolicitudPrestamo.numero)))
        assert cantidad == 1
