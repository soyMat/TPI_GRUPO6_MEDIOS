"""Pruebas de integración real contra SQLite para CU_01 (TC-03, 06, 07, 08, 09, 10, 15)."""

from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
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
    UUID_EST_COMUN,
    UUID_MAT_PROYECTO2,
    UUID_MAT_TESIS,
)


def _crear_cliente_sqlite(tmp_path: Path) -> tuple[TestClient, str]:
    db_path = tmp_path / "test_cu01.db"
    db_url = f"sqlite:///{db_path}"
    api = crear_app_integrada(database_url=db_url, montar_estaticos=False)
    return TestClient(api), db_url


def test_tc07_inventario_unico_impide_duplicados(tmp_path: Path) -> None:
    _, db_url = _crear_cliente_sqlite(tmp_path)
    engine = create_engine(db_url)

    with Session(engine) as session:
        session.add(
            Equipamiento(
                numero_inventario="INV-CAM-01",  # Ya existe en el seed
                tipo_codigo="CAMARA",
                estado="OPERATIVO",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_tc08_tc09_guardado_atomico_solicitud_e_historial_en_sqlite(
    tmp_path: Path,
) -> None:
    cliente, db_url = _crear_cliente_sqlite(tmp_path)
    payload = {
        "tipo_id": "CAMARA",
        "cantidad": 1,
        "desde": "2026-11-20T10:00:00",
        "hasta": "2026-11-22T10:00:00",
        "materia_id": str(UUID_MAT_PROYECTO2),
    }

    respuesta = cliente.post(
        "/api/solicitudes",
        json=payload,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "PENDIENTE_SOLICITADA"
    assert cuerpo["requiere_aval"] is False

    engine = create_engine(db_url)
    with Session(engine) as session:
        solicitudes = session.scalars(select(SolicitudPrestamo)).all()
        cambios = session.scalars(select(CambioEstado)).all()

        assert len(solicitudes) == 1
        assert str(solicitudes[0].numero) == cuerpo["numero"]
        assert solicitudes[0].usuario_id == UUID_EST_COMUN

        assert len(cambios) == 1
        assert cambios[0].solicitud_numero == solicitudes[0].numero
        assert cambios[0].anterior is None
        assert cambios[0].nuevo == "PENDIENTE_SOLICITADA"
        assert cambios[0].actor_id == UUID_EST_COMUN


def test_tc03_tc06_solicitud_pendiente_no_ocupa_pero_prestamo_efectivo_si(
    tmp_path: Path,
) -> None:
    cliente, db_url = _crear_cliente_sqlite(tmp_path)
    # En el seed, CAMARA tiene 2 unidades OPERATIVO y 1 en MANTENIMIENTO -> libres = 2
    payload_dos_camaras = {
        "tipo_id": "CAMARA",
        "cantidad": 2,
        "desde": "2026-11-20T10:00:00",
        "hasta": "2026-11-22T10:00:00",
        "materia_id": str(UUID_MAT_PROYECTO2),
    }

    # 1. Creamos una solicitud por las 2 unidades (queda en PENDIENTE_SOLICITADA)
    creada = cliente.post(
        "/api/solicitudes",
        json=payload_dos_camaras,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert creada.status_code == 201

    # 2. TC-06: Otra prevalidación por 2 unidades en el mismo horario sigue dando válida
    # porque la solicitud pendiente NO consume disponibilidad física.
    preval_sin_ocupacion = cliente.post(
        "/api/solicitudes/prevalidar",
        json=payload_dos_camaras,
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert preval_sin_ocupacion.status_code == 200
    assert preval_sin_ocupacion.json()["valido"] is True

    # 3. Registramos un préstamo efectivo sobre 1 unidad operativa en ese rango
    engine = create_engine(db_url)
    with Session(engine) as session:
        equipo_op = session.scalar(
            select(Equipamiento).where(Equipamiento.numero_inventario == "INV-CAM-01")
        )
        prestamo = Prestamo(
            solicitud_numero=int(creada.json()["numero"]),
            desde=datetime(2026, 11, 20, 12, 0),
            hasta=datetime(2026, 11, 21, 12, 0),
        )
        prestamo.detalles.append(DetallePrestamo(equipamiento_id=equipo_op.id))
        session.add(prestamo)
        session.commit()

    # 4. TC-03: Ahora pedir 2 unidades falla con 409 SIN_DISPONIBILIDAD, pero pedir 1 pasa
    preval_excedida = cliente.post(
        "/api/solicitudes/prevalidar",
        json=payload_dos_camaras,
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert preval_excedida.status_code == 409
    assert preval_excedida.json()["detail"]["codigo"] == "SIN_DISPONIBILIDAD"

    preval_una = cliente.post(
        "/api/solicitudes/prevalidar",
        json=payload_dos_camaras | {"cantidad": 1},
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert preval_una.status_code == 200


def test_tc10_tc15_alta_gama_genera_notificacion_real_y_filtra_mis_solicitudes(
    tmp_path: Path,
) -> None:
    cliente, db_url = _crear_cliente_sqlite(tmp_path)
    payload_cine = {
        "tipo_id": "CINE_PRO",
        "cantidad": 1,
        "desde": "2026-11-23T09:00:00",
        "hasta": "2026-11-25T09:00:00",
        "materia_id": str(UUID_MAT_TESIS),
    }

    conf = cliente.post(
        "/api/solicitudes",
        json=payload_cine,
        headers={"X-Usuario-Demo": "estudiante-elegible"},
    )
    assert conf.status_code == 201
    assert conf.json()["requiere_aval"] is True
    assert conf.json()["advertencias"] == []

    # Verificamos la fila real en la tabla notificaciones
    engine = create_engine(db_url)
    with Session(engine) as session:
        avisos = session.scalars(select(Notificacion)).all()
        assert len(avisos) == 1
        assert avisos[0].destinatario_id == UUID_DOCENTE
        assert str(avisos[0].solicitud_numero) == conf.json()["numero"]

    # TC-15: Mis solicitudes devuelve la solicitud con nombres legibles sólo al autor
    mias_elegible = cliente.get(
        "/api/solicitudes/mias",
        headers={"X-Usuario-Demo": "estudiante-elegible"},
    )
    assert mias_elegible.status_code == 200
    items = mias_elegible.json()
    assert len(items) == 1
    assert items[0]["tipo"] == "Cámara Cine 4K"
    assert items[0]["materia"] == "Proyecto 4 - Tesis Audiovisual"
    assert items[0]["requiere_aval"] is True

    mias_comun = cliente.get(
        "/api/solicitudes/mias",
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert mias_comun.status_code == 200
    assert mias_comun.json() == []