"""Pruebas unitarias de política y disponibilidad para CU_01."""

from datetime import datetime, timedelta

from app.politica import PoliticaPrestamo, sugerir_vencimiento_estandar
from app.schemas import DatosSolicitud


def _datos(
    tipo_id: str = "CAMARA",
    cantidad: int = 1,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    materia_id: str = "MAT-01",
) -> DatosSolicitud:
    inicio = desde or datetime(2026, 11, 20, 10, 0)
    fin = hasta or datetime(2026, 11, 22, 10, 0)
    return DatosSolicitud(
        tipo_id=tipo_id,
        cantidad=cantidad,
        desde=inicio,
        hasta=fin,
        materia_id=materia_id,
    )


def test_tc02_cantidad_no_positiva_y_rango_fechas_invalido() -> None:
    politica = PoliticaPrestamo()
    usuario = {"id": "u-1", "rol": "ESTUDIANTE"}
    tipo = {"id": "CAMARA", "nombre": "Cámara", "alta_gama": False, "unidades_disponibles": 3}
    materia = {"id": "MAT-01", "nombre": "Proyecto 1"}

    res_cantidad = politica.evaluar(_datos(cantidad=0), usuario, tipo, materia)
    assert res_cantidad["valido"] is False
    assert res_cantidad["errores"][0]["campo"] == "cantidad"
    assert res_cantidad["errores"][0]["codigo"] == "CANTIDAD_INVALIDA"

    inicio = datetime(2026, 11, 20, 10, 0)
    res_fechas = politica.evaluar(
        _datos(desde=inicio, hasta=inicio),
        usuario,
        tipo,
        materia,
    )
    assert res_fechas["valido"] is False
    assert res_fechas["errores"][0]["campo"] == "hasta"
    assert res_fechas["errores"][0]["codigo"] == "RANGO_FECHAS_INVALIDO"


def test_tc03_y_tc06_disponibilidad_excluye_no_operativos_y_pendientes() -> None:
    inicio = datetime(2026, 11, 20, 10, 0)
    fin = datetime(2026, 11, 22, 10, 0)

    equipos = [
        {"inventario": "EQ-01", "tipo_id": "CAMARA", "estado": "OPERATIVO"},
        {"inventario": "EQ-02", "tipo_id": "CAMARA", "estado": "OPERATIVO"},
        {"inventario": "EQ-03", "tipo_id": "CAMARA", "estado": "MANTENIMIENTO"},
        {"inventario": "EQ-04", "tipo_id": "CAMARA", "estado": "FUERA_DE_SERVICIO"},
    ]
    ocupaciones = [
        # Ocupación efectiva en el período: consume 1 unidad operativa
        {
            "equipo_id": "EQ-01",
            "tipo_id": "CAMARA",
            "desde": datetime(2026, 11, 21, 8, 0),
            "hasta": datetime(2026, 11, 21, 18, 0),
            "estado": "APROBADA",
        },
        # Solicitud pendiente en el período: NO consume disponibilidad
        {
            "equipo_id": "EQ-02",
            "tipo_id": "CAMARA",
            "desde": inicio,
            "hasta": fin,
            "estado": "PENDIENTE_SOLICITADA",
        },
    ]

    politica = PoliticaPrestamo()
    usuario = {"id": "u-1", "rol": "ESTUDIANTE"}
    tipo = {
        "id": "CAMARA",
        "nombre": "Cámara",
        "alta_gama": False,
        "equipos": equipos,
        "ocupaciones": ocupaciones,
    }
    materia = {"id": "MAT-01", "nombre": "Proyecto 1"}

    # Queda exactamente 1 unidad libre (EQ-02): pedir 1 es válido
    res_ok = politica.evaluar(_datos(cantidad=1, desde=inicio, hasta=fin), usuario, tipo, materia)
    assert res_ok["valido"] is True

    # TC-03: pedir 2 unidades cuando solo 1 está libre devuelve SIN_DISPONIBILIDAD
    res_sin_cupo = politica.evaluar(
        _datos(cantidad=2, desde=inicio, hasta=fin),
        usuario,
        tipo,
        materia,
    )
    assert res_sin_cupo["valido"] is False
    assert res_sin_cupo["errores"][0]["codigo"] == "SIN_DISPONIBILIDAD"


def test_intervalos_semiabiertos_no_solapan_en_borde() -> None:
    equipos = [{"inventario": "EQ-01", "tipo_id": "CAMARA", "estado": "OPERATIVO"}]
    ocupaciones = [
        {
            "equipo_id": "EQ-01",
            "tipo_id": "CAMARA",
            "desde": datetime(2026, 11, 20, 10, 0),
            "hasta": datetime(2026, 11, 22, 10, 0),
            "estado": "CONFIRMADA",
        }
    ]
    politica = PoliticaPrestamo()
    usuario = {"id": "u-1", "rol": "ESTUDIANTE"}
    tipo = {
        "id": "CAMARA",
        "nombre": "Cámara",
        "alta_gama": False,
        "equipos": equipos,
        "ocupaciones": ocupaciones,
    }
    materia = {"id": "MAT-01", "nombre": "Proyecto 1"}

    # Empieza exactamente cuando termina la ocupación anterior: [22 10:00, 24 10:00)
    res = politica.evaluar(
        _datos(
            cantidad=1,
            desde=datetime(2026, 11, 22, 10, 0),
            hasta=datetime(2026, 11, 24, 10, 0),
        ),
        usuario,
        tipo,
        materia,
    )
    assert res["valido"] is True


def test_tc04_restriccion_activa_bloquea_solicitud() -> None:
    politica = PoliticaPrestamo()
    usuario = {
        "id": "u-1",
        "rol": "ESTUDIANTE",
        "restricciones": [
            {
                "activa": True,
                "tipo_id": "CAMARA",
                "motivo": "Devolución pendiente con demora.",
            }
        ],
    }
    tipo = {"id": "CAMARA", "nombre": "Cámara", "alta_gama": False, "unidades_disponibles": 5}
    materia = {"id": "MAT-01", "nombre": "Proyecto 1"}

    res = politica.evaluar(_datos(), usuario, tipo, materia)
    assert res["valido"] is False
    assert res["errores"][0]["codigo"] == "RESTRICCION_ACTIVA"
    assert "Devolución pendiente" in res["errores"][0]["mensaje"]


def test_tc05_y_tc10_alta_gama_elegibilidad_y_aval() -> None:
    politica = PoliticaPrestamo()
    tipo_alta_gama = {
        "id": "CINE-4K",
        "nombre": "Cámara Cine 4K",
        "alta_gama": True,
        "unidades_disponibles": 2,
    }
    materia_comun = {"id": "MAT-01", "nombre": "Taller Inicial", "avanzada": False}
    materia_avanzada = {"id": "MAT-AV", "nombre": "Tesis Audiovisual", "avanzada": True}

    estudiante_comun = {"id": "est-comun", "rol": "ESTUDIANTE", "elegible_alta_gama": False}
    estudiante_tesista = {"id": "est-tesista", "rol": "ESTUDIANTE", "tesista_avanzado": True}

    # TC-05: estudiante común + alta gama -> bloqueo NO_ELEGIBLE
    res_no_elegible = politica.evaluar(
        _datos(tipo_id="CINE-4K", materia_id="MAT-01"),
        estudiante_comun,
        tipo_alta_gama,
        materia_comun,
    )
    assert res_no_elegible["valido"] is False
    assert res_no_elegible["requiere_aval"] is False
    assert res_no_elegible["errores"][0]["codigo"] == "NO_ELEGIBLE"

    # TC-10 (por condición de tesista): válido + requiere_aval=True
    res_tesista = politica.evaluar(
        _datos(tipo_id="CINE-4K", materia_id="MAT-01"),
        estudiante_tesista,
        tipo_alta_gama,
        materia_comun,
    )
    assert res_tesista["valido"] is True
    assert res_tesista["requiere_aval"] is True
    assert res_tesista["errores"] == []

    # TC-10 (por materia avanzada): válido + requiere_aval=True
    res_materia_av = politica.evaluar(
        _datos(tipo_id="CINE-4K", materia_id="MAT-AV"),
        estudiante_comun,
        tipo_alta_gama,
        materia_avanzada,
    )
    assert res_materia_av["valido"] is True
    assert res_materia_av["requiere_aval"] is True


def test_tc13_docente_no_recibe_reglas_exclusivas_de_estudiante() -> None:
    politica = PoliticaPrestamo()
    docente = {"id": "doc-1", "rol": "DOCENTE"}
    tipo_alta_gama = {
        "id": "CINE-4K",
        "nombre": "Cámara Cine 4K",
        "alta_gama": True,
        "unidades_disponibles": 1,
    }
    materia = {"id": "MAT-01", "nombre": "Taller Inicial", "avanzada": False}

    res = politica.evaluar(_datos(tipo_id="CINE-4K"), docente, tipo_alta_gama, materia)
    assert res["valido"] is True
    assert res["requiere_aval"] is False
    assert res["errores"] == []


def test_tc12_revalidar_detecta_cambio_de_disponibilidad_al_confirmar() -> None:
    disponibles_actuales = 1
    politica = PoliticaPrestamo(
        consultar_disponibilidad=lambda tipo_id, desde, hasta: disponibles_actuales
    )
    usuario = {"id": "u-1", "rol": "ESTUDIANTE"}
    tipo = {"id": "CAMARA", "nombre": "Cámara", "alta_gama": False}
    materia = {"id": "MAT-01", "nombre": "Proyecto 1"}
    datos = _datos(cantidad=1)

    res_pre = politica.evaluar(datos, usuario, tipo, materia)
    assert res_pre["valido"] is True
    assert set(res_pre.keys()) == {"valido", "requiere_aval", "errores", "resumen"}

    # Se ocupa el último equipo entre prevalidación y confirmación
    disponibles_actuales = 0
    res_rev = politica.revalidar(datos, usuario, tipo, materia)
    assert res_rev["valido"] is False
    assert res_rev["errores"][0]["codigo"] == "DISPONIBILIDAD_CAMBIO"
    assert set(res_rev.keys()) == {"valido", "requiere_aval", "errores", "resumen"}


def test_tc14_sugerencia_estandar_48_horas() -> None:
    retiro = datetime(2026, 11, 20, 10, 0)
    assert sugerir_vencimiento_estandar(retiro) == retiro + timedelta(hours=48)
