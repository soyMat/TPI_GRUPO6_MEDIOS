from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.controller import ControlPrestamos
from app.main import crear_app


DATOS_VALIDOS = {
    "tipo_id": "CAMARA",
    "cantidad": 1,
    "desde": "2026-11-20T10:00:00",
    "hasta": "2026-11-22T10:00:00",
    "materia_id": "materia-1",
}


# Los dobles aislan la API de las reglas y la persistencia de otros modulos.
class CatalogosDoble:
    def __init__(self) -> None:
        self.tipo = SimpleNamespace(id="CAMARA", nombre="Cámara", alta_gama=False)
        self.materia = SimpleNamespace(id="materia-1", nombre="Proyecto 2")

    def listar_tipos(self):
        return [self.tipo]

    def listar_materias(self):
        return [self.materia]

    def obtener_tipo(self, tipo_id):
        if tipo_id != self.tipo.id:
            raise LookupError(tipo_id)
        return self.tipo

    def obtener_materia(self, materia_id):
        if materia_id != self.materia.id:
            raise LookupError(materia_id)
        return self.materia


class PoliticaDoble:
    def __init__(self) -> None:
        self.resultado_evaluar = {"valido": True, "errores": [], "requiere_aval": False}
        self.resultado_revalidar = {"valido": True, "errores": [], "requiere_aval": False}
        self.evaluaciones = []
        self.revalidaciones = []

    def evaluar(self, datos, usuario, tipo, materia):
        self.evaluaciones.append((datos, usuario, tipo, materia))
        return self.resultado_evaluar

    def revalidar(self, datos, usuario, tipo, materia):
        self.revalidaciones.append((datos, usuario, tipo, materia))
        return self.resultado_revalidar


class SolicitudesDoble:
    def __init__(self) -> None:
        self.guardadas = []
        self.usuario_listado = None
        self.error_al_guardar = None

    def guardar_con_historial(self, solicitud):
        if self.error_al_guardar:
            raise self.error_al_guardar
        self.guardadas.append(solicitud)

    def listar_de(self, usuario_id):
        self.usuario_listado = usuario_id
        return [
            {
                "numero": "SOL-001",
                "estado": "PENDIENTE_SOLICITADA",
                "tipo": "Cámara",
                "cantidad": 1,
                "desde": "2026-11-20T10:00:00",
                "hasta": "2026-11-22T10:00:00",
                "materia": "Proyecto 2",
                "requiere_aval": False,
            }
        ]


class AuditorDoble:
    def __init__(self) -> None:
        self.registros = []

    def registrar_alta(self, solicitud, usuario):
        self.registros.append((solicitud, usuario))


class NotificadorDoble:
    def __init__(self) -> None:
        self.avisos = []
        self.error_al_avisar = None

    def avisar_aval(self, solicitud, materia):
        if self.error_al_avisar:
            raise self.error_al_avisar
        self.avisos.append((solicitud, materia))


class FabricaSolicitudDoble:
    def __init__(self) -> None:
        self.creadas = []

    def __call__(self, datos, usuario, tipo, materia, requiere_aval):
        solicitud = SimpleNamespace(
            numero="SOL-001",
            estado="PENDIENTE_SOLICITADA",
            datos=datos,
            usuario=usuario,
            tipo=tipo,
            materia=materia,
            requiere_aval=requiere_aval,
        )
        self.creadas.append(solicitud)
        return solicitud


def construir_cliente():
    politica = PoliticaDoble()
    catalogos = CatalogosDoble()
    solicitudes = SolicitudesDoble()
    notificador = NotificadorDoble()
    auditor = AuditorDoble()
    fabrica = FabricaSolicitudDoble()
    usuarios = {
        "estudiante-comun": SimpleNamespace(
            id="usuario-1", rol="Estudiante", nombre="Estudiante Demo"
        ),
        "docente-demo": SimpleNamespace(
            id="usuario-2", rol="Docente", nombre="Docente Demo"
        ),
        "personal-demo": SimpleNamespace(
            id="usuario-3", rol="PersonalLaboratorio", nombre="Personal Demo"
        ),
    }

    control = ControlPrestamos(
        politica=politica,
        catalogos=catalogos,
        solicitudes=solicitudes,
        notificador=notificador,
        auditor=auditor,
        crear_solicitud=fabrica,
    )
    app = crear_app(control, usuarios.__getitem__)
    dependencias = SimpleNamespace(
        politica=politica,
        catalogos=catalogos,
        solicitudes=solicitudes,
        notificador=notificador,
        auditor=auditor,
        fabrica=fabrica,
        usuarios=usuarios,
    )
    return TestClient(app), dependencias


def test_listar_catalogos():
    cliente, _ = construir_cliente()

    tipos = cliente.get("/api/equipos/tipos")
    materias = cliente.get("/api/materias")

    assert tipos.status_code == 200
    assert tipos.json() == [{"id": "CAMARA", "nombre": "Cámara", "alta_gama": False}]
    assert materias.status_code == 200
    assert materias.json() == [{"id": "materia-1", "nombre": "Proyecto 2"}]


def test_app_sirve_frontend_estatico():
    cliente, _ = construir_cliente()

    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "Solicitud de Equipamiento (CU_01)" in respuesta.text


def test_prevalidar_usa_usuario_demo_y_devuelve_resumen():
    cliente, dobles = construir_cliente()

    respuesta = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["valido"] is True
    assert respuesta.json()["resumen"]["tipo"] == "Cámara"
    assert dobles.politica.evaluaciones[0][1].id == "usuario-1"


def test_datos_invalidos_devuelven_errores_por_campo_tc02():
    cliente, dobles = construir_cliente()
    dobles.politica.resultado_evaluar = {
        "valido": False,
        "requiere_aval": False,
        "errores": [
            {
                "codigo": "CANTIDAD_INVALIDA",
                "mensaje": "La cantidad debe ser positiva.",
                "campo": "cantidad",
            }
        ],
    }

    respuesta_cantidad = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS | {"cantidad": 0},
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    dobles.politica.resultado_evaluar = {
        "valido": False,
        "requiere_aval": False,
        "errores": [
            {
                "codigo": "PERIODO_INVALIDO",
                "mensaje": "La fecha hasta debe ser posterior a desde.",
                "campo": "hasta",
            }
        ],
    }
    respuesta_periodo = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS | {"hasta": "2026-11-19T10:00:00"},
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta_cantidad.status_code == 422
    assert respuesta_cantidad.json()["detail"]["codigo"] == "CANTIDAD_INVALIDA"
    assert respuesta_cantidad.json()["detail"]["errores"][0]["campo"] == "cantidad"
    assert respuesta_periodo.status_code == 422
    assert respuesta_periodo.json()["detail"]["codigo"] == "PERIODO_INVALIDO"
    assert len(dobles.politica.evaluaciones) == 2


def test_confirmar_revalida_audita_y_guarda_tc01_tc08_tc09():
    cliente, dobles = construir_cliente()

    respuesta = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "numero": "SOL-001",
        "estado": "PENDIENTE_SOLICITADA",
        "requiere_aval": False,
        "advertencias": [],
    }
    assert len(dobles.politica.revalidaciones) == 1
    assert len(dobles.auditor.registros) == 1
    assert len(dobles.solicitudes.guardadas) == 1
    assert dobles.notificador.avisos == []


def test_confirmar_con_aval_genera_aviso_interno_tc10():
    cliente, dobles = construir_cliente()
    dobles.politica.resultado_revalidar = {
        "valido": True,
        "errores": [],
        "requiere_aval": True,
    }

    respuesta = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["requiere_aval"] is True
    assert len(dobles.notificador.avisos) == 1


def test_falla_de_aviso_conserva_solicitud_y_advierte():
    cliente, dobles = construir_cliente()
    dobles.politica.resultado_revalidar = {
        "valido": True,
        "errores": [],
        "requiere_aval": True,
    }
    dobles.notificador.error_al_avisar = RuntimeError("aviso no disponible")

    respuesta = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 201
    assert len(dobles.solicitudes.guardadas) == 1
    assert respuesta.json()["advertencias"]


def test_falla_de_persistencia_no_muestra_exito():
    cliente, dobles = construir_cliente()
    dobles.solicitudes.error_al_guardar = RuntimeError("sqlite no disponible")

    respuesta = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 500
    assert respuesta.json()["detail"]["codigo"] == "ERROR_PERSISTENCIA"


def test_cambio_de_disponibilidad_impide_guardar_tc12():
    cliente, dobles = construir_cliente()
    dobles.politica.resultado_revalidar = {
        "valido": False,
        "requiere_aval": False,
        "errores": [
            {
                "codigo": "DISPONIBILIDAD_CAMBIO",
                "mensaje": "La disponibilidad cambió antes de confirmar.",
            }
        ],
    }

    respuesta = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"]["codigo"] == "DISPONIBILIDAD_CAMBIO"
    assert dobles.fabrica.creadas == []
    assert dobles.solicitudes.guardadas == []


def test_solo_estudiante_o_docente_pueden_solicitar_tc13():
    cliente, _ = construir_cliente()

    docente = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    personal = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "personal-demo"},
    )

    assert docente.status_code == 200
    assert personal.status_code == 403
    assert personal.json()["detail"]["codigo"] == "ROL_NO_PERMITIDO"


def test_mis_solicitudes_filtra_por_usuario_demo_tc15():
    cliente, dobles = construir_cliente()

    respuesta = cliente.get(
        "/api/solicitudes/mias",
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()[0]["numero"] == "SOL-001"
    assert dobles.solicitudes.usuario_listado == "usuario-1"


def test_usuario_demo_ausente_o_desconocido_es_rechazado():
    cliente, _ = construir_cliente()

    sin_header = cliente.post("/api/solicitudes/prevalidar", json=DATOS_VALIDOS)
    desconocido = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "nadie"},
    )

    assert sin_header.status_code == 403
    assert desconocido.status_code == 403
