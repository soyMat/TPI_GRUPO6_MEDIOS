from pathlib import Path
from types import SimpleNamespace

from fastapi.staticfiles import StaticFiles
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


class CatalogosDemo:
    def __init__(self) -> None:
        self.tipos = {
            "CAMARA": SimpleNamespace(id="CAMARA", nombre="Cámara HD", alta_gama=False),
            "CINE_PRO": SimpleNamespace(
                id="CINE_PRO", nombre="Cámara Cine 4K", alta_gama=True
            ),
        }
        self.materias = {
            "materia-1": SimpleNamespace(id="materia-1", nombre="Proyecto 2"),
            "materia-4": SimpleNamespace(id="materia-4", nombre="Proyecto 4"),
        }

    def listar_tipos(self):
        return list(self.tipos.values())

    def listar_materias(self):
        return list(self.materias.values())

    def obtener_tipo(self, tipo_id):
        if tipo_id not in self.tipos:
            raise LookupError(tipo_id)
        return self.tipos[tipo_id]

    def obtener_materia(self, materia_id):
        if materia_id not in self.materias:
            raise LookupError(materia_id)
        return self.materias[materia_id]


class PoliticaDemo:
    def __init__(self) -> None:
        self.forzar_conflicto_revalidar = False

    def evaluar(self, datos, usuario, tipo, materia):
        errores = []
        if datos.cantidad <= 0:
            errores.append(
                {
                    "codigo": "CANTIDAD_INVALIDA",
                    "mensaje": "La cantidad debe ser mayor a cero.",
                    "campo": "cantidad",
                }
            )
        if datos.hasta <= datos.desde:
            errores.append(
                {
                    "codigo": "PERIODO_INVALIDO",
                    "mensaje": "La fecha hasta debe ser posterior a desde.",
                    "campo": "hasta",
                }
            )
        if errores:
            return {"valido": False, "requiere_aval": False, "errores": errores}

        if getattr(usuario, "restringido", False):
            return {
                "valido": False,
                "requiere_aval": False,
                "errores": [
                    {
                        "codigo": "RESTRICCION_ACTIVA",
                        "mensaje": "El estudiante posee una restricción vigente.",
                    }
                ],
            }

        rol = str(getattr(usuario, "rol", "")).lower()
        if getattr(tipo, "alta_gama", False) and rol == "estudiante":
            if not getattr(usuario, "elegible_alta_gama", False):
                return {
                    "valido": False,
                    "requiere_aval": False,
                    "errores": [
                        {
                            "codigo": "NO_ELEGIBLE",
                            "mensaje": "El equipamiento de alta gama requiere materia avanzada o tesista.",
                        }
                    ],
                }
            return {"valido": True, "requiere_aval": True, "errores": []}

        return {"valido": True, "requiere_aval": False, "errores": []}

    def revalidar(self, datos, usuario, tipo, materia):
        if self.forzar_conflicto_revalidar:
            return {
                "valido": False,
                "requiere_aval": False,
                "errores": [
                    {
                        "codigo": "DISPONIBILIDAD_CAMBIO",
                        "mensaje": "La disponibilidad cambió antes de confirmar.",
                    }
                ],
            }
        return self.evaluar(datos, usuario, tipo, materia)


class RepositorioSolicitudesMemoria:
    def __init__(self) -> None:
        self.items = []

    def guardar_con_historial(self, solicitud):
        self.items.append(solicitud)

    def listar_de(self, usuario_id):
        return [
            {
                "numero": sol.numero,
                "estado": sol.estado,
                "tipo": sol.tipo.nombre,
                "cantidad": sol.datos.cantidad,
                "desde": sol.datos.desde,
                "hasta": sol.datos.hasta,
                "materia": sol.materia.nombre,
                "requiere_aval": sol.requiere_aval,
            }
            for sol in self.items
            if sol.usuario.id == usuario_id
        ]


class AuditorMemoria:
    def __init__(self) -> None:
        self.eventos = []

    def registrar_alta(self, solicitud, usuario):
        self.eventos.append((solicitud.numero, usuario.id))


class NotificadorMemoria:
    def __init__(self) -> None:
        self.avisos = []

    def avisar_aval(self, solicitud, materia):
        self.avisos.append((solicitud.numero, materia.id))


def construir_cliente_interfaz():
    politica = PoliticaDemo()
    catalogos = CatalogosDemo()
    solicitudes = RepositorioSolicitudesMemoria()
    auditor = AuditorMemoria()
    notificador = NotificadorMemoria()
    contador = {"n": 0}

    def crear_solicitud(datos, usuario, tipo, materia, requiere_aval):
        contador["n"] += 1
        return SimpleNamespace(
            numero=f"SOL-{contador['n']:03d}",
            estado="PENDIENTE_SOLICITADA",
            datos=datos,
            usuario=usuario,
            tipo=tipo,
            materia=materia,
            requiere_aval=requiere_aval,
        )

    usuarios = {
        "estudiante-comun": SimpleNamespace(
            id="u-1", rol="Estudiante", elegible_alta_gama=False, restringido=False
        ),
        "estudiante-elegible": SimpleNamespace(
            id="u-2", rol="Estudiante", elegible_alta_gama=True, restringido=False
        ),
        "estudiante-restringido": SimpleNamespace(
            id="u-3", rol="Estudiante", elegible_alta_gama=False, restringido=True
        ),
        "docente-demo": SimpleNamespace(
            id="u-4", rol="Docente", elegible_alta_gama=True, restringido=False
        ),
        "personal-demo": SimpleNamespace(
            id="u-5", rol="PersonalLaboratorio", elegible_alta_gama=False, restringido=False
        ),
    }

    control = ControlPrestamos(
        politica=politica,
        catalogos=catalogos,
        solicitudes=solicitudes,
        notificador=notificador,
        auditor=auditor,
        crear_solicitud=crear_solicitud,
    )
    api = crear_app(control, usuarios.__getitem__)
    api.mount("/", StaticFiles(directory="app/static", html=True), name="static")

    dependencias = SimpleNamespace(
        politica=politica,
        solicitudes=solicitudes,
        notificador=notificador,
        auditor=auditor,
    )
    return TestClient(api), dependencias


def test_archivos_estaticos_y_controles_ui_tc11_tc14_tc16():
    cliente, _ = construir_cliente_interfaz()

    html_resp = cliente.get("/")
    css_resp = cliente.get("/styles.css")
    js_resp = cliente.get("/app.js")

    assert html_resp.status_code == 200
    assert css_resp.status_code == 200
    assert js_resp.status_code == 200

    html = html_resp.text
    # Selector de usuario ficticio X-Usuario-Demo y límites de demo (TC-16)
    assert 'id="usuario-demo"' in html
    assert "X-Usuario-Demo" in html
    assert "estudiante-comun" in html
    assert "estudiante-elegible" in html
    assert "docente-demo" in html
    assert "No constituye autenticación productiva" in html

    # Controles del formulario, sugerencia 48h (TC-14) y recorridos alternativos (TC-11)
    assert 'id="btn-sugerir-48h"' in html
    assert 'id="btn-continuar"' in html
    assert 'id="btn-confirmar"' in html
    assert 'id="btn-volver"' in html
    assert 'id="btn-cancelar-resumen"' in html
    assert 'id="tab-mis-solicitudes"' in html

    # Bloqueo de doble clic en Confirmar sin Idempotency-Key
    js = Path("app/static/app.js").read_text(encoding="utf-8")
    assert "btnConfirmar.disabled = true" in js
    assert "Idempotency-Key" not in js


def test_recorrido_principal_y_mis_solicitudes_tc01_tc15():
    cliente, deps = construir_cliente_interfaz()

    tipos = cliente.get("/api/equipos/tipos")
    materias = cliente.get("/api/materias")
    assert tipos.status_code == 200
    assert materias.status_code == 200

    prev = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert prev.status_code == 200
    assert prev.json()["valido"] is True
    assert prev.json()["requiere_aval"] is False
    assert prev.json()["resumen"]["tipo"] == "Cámara HD"

    conf = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert conf.status_code == 201
    assert conf.json() == {
        "numero": "SOL-001",
        "estado": "PENDIENTE_SOLICITADA",
        "requiere_aval": False,
        "advertencias": [],
    }
    assert len(deps.auditor.eventos) == 1

    mias = cliente.get(
        "/api/solicitudes/mias",
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert mias.status_code == 200
    listado = mias.json()
    assert len(listado) == 1
    assert listado[0]["numero"] == "SOL-001"
    assert listado[0]["estado"] == "PENDIENTE_SOLICITADA"


def test_errores_validacion_restriccion_y_alta_gama_tc02_tc04_tc05():
    cliente, _ = construir_cliente_interfaz()

    # TC-02: datos inválidos por campo
    inv = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS | {"cantidad": 0},
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert inv.status_code == 422
    assert inv.json()["detail"]["errores"][0]["campo"] == "cantidad"

    # TC-04: restricción activa
    rest = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-restringido"},
    )
    assert rest.status_code == 403
    assert rest.json()["detail"]["codigo"] == "RESTRICCION_ACTIVA"

    # TC-05: estudiante común solicita alta gama sin elegibilidad
    no_eleg = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS | {"tipo_id": "CINE_PRO"},
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert no_eleg.status_code == 403
    assert no_eleg.json()["detail"]["codigo"] == "NO_ELEGIBLE"


def test_alta_gama_elegible_con_aval_pendiente_tc10():
    cliente, deps = construir_cliente_interfaz()
    datos_alta_gama = DATOS_VALIDOS | {"tipo_id": "CINE_PRO", "materia_id": "materia-4"}

    conf = cliente.post(
        "/api/solicitudes",
        json=datos_alta_gama,
        headers={"X-Usuario-Demo": "estudiante-elegible"},
    )
    assert conf.status_code == 201
    assert conf.json()["estado"] == "PENDIENTE_SOLICITADA"
    assert conf.json()["requiere_aval"] is True
    assert len(deps.notificador.avisos) == 1


def test_roles_demo_permitidos_y_denegados_tc13():
    cliente, _ = construir_cliente_interfaz()

    docente = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "docente-demo"},
    )
    assert docente.status_code == 201

    personal = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "personal-demo"},
    )
    assert personal.status_code == 403
    assert personal.json()["detail"]["codigo"] == "ROL_NO_PERMITIDO"

    sin_usuario = cliente.post("/api/solicitudes/prevalidar", json=DATOS_VALIDOS)
    assert sin_usuario.status_code == 403


def test_revalidacion_fallida_al_confirmar_devuelve_409_tc12():
    cliente, deps = construir_cliente_interfaz()

    prev = cliente.post(
        "/api/solicitudes/prevalidar",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert prev.status_code == 200

    deps.politica.forzar_conflicto_revalidar = True
    conf = cliente.post(
        "/api/solicitudes",
        json=DATOS_VALIDOS,
        headers={"X-Usuario-Demo": "estudiante-comun"},
    )
    assert conf.status_code == 409
    assert conf.json()["detail"]["codigo"] == "DISPONIBILIDAD_CAMBIO"
    assert deps.solicitudes.items == []