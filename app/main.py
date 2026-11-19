"""API FastAPI del prototipo CU_01."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.controller import ControlPrestamos, ErrorCU01
from app.models import Base
from app.notifications import NotificadorSolicitudes
from app.politica import PoliticaPrestamo
from app.repository import (
    AuditorSolicitudes,
    CalendarioRecursos,
    RepositorioCatalogos,
    RepositorioSolicitudes,
    ResolutorUsuarioDemo,
    crear_solicitud_prestamo,
)
from app.schemas import (
    DatosSolicitud,
    MateriaSalida,
    ResultadoValidacionSalida,
    SolicitudCreadaSalida,
    SolicitudListadoSalida,
    TipoEquipamientoSalida,
    leer_atributo,
)
from scripts.seed_demo import DATABASE_URL_DEFECTO, poblar_datos_demo


DIRECTORIO_ESTATICO = Path(__file__).resolve().parent / "static"


def crear_app(
    control: ControlPrestamos | None = None,
    resolver_usuario_demo: Callable[[str], Any] | None = None,
    montar_estaticos: bool = True,
) -> FastAPI:
    """Construye la API con colaboradores reales o dobles de prueba."""
    api = FastAPI(title="Prototipo CU_01 - Grupo 6")

    # Si faltan colaboradores, se informa el problema en lugar de simular exito.
    def control_configurado() -> ControlPrestamos:
        if control is None:
            raise ErrorCU01(
                503,
                "DEPENDENCIAS_NO_CONFIGURADAS",
                "La integración del prototipo todavía no fue configurada.",
            )
        return control

    def usuario_demo(alias: str | None) -> Any:
        # El alias identifica personas ficticias; no representa autenticacion real.
        if resolver_usuario_demo is None:
            raise ErrorCU01(
                503,
                "DEPENDENCIAS_NO_CONFIGURADAS",
                "El resolutor de usuarios demo todavía no fue configurado.",
            )
        if not alias:
            raise ErrorCU01(403, "USUARIO_DEMO_REQUERIDO", "Seleccione un usuario demo.")
        try:
            usuario = resolver_usuario_demo(alias)
        except (KeyError, LookupError) as error:
            raise ErrorCU01(
                403, "USUARIO_DEMO_INVALIDO", "El usuario demo no existe."
            ) from error
        if usuario is None:
            raise ErrorCU01(403, "USUARIO_DEMO_INVALIDO", "El usuario demo no existe.")

        rol = str(
            leer_atributo(
                usuario,
                "rol",
                leer_atributo(usuario, "tipo_usuario", ""),
            )
        ).lower()
        if rol not in {"estudiante", "docente"}:
            raise ErrorCU01(
                403,
                "ROL_NO_PERMITIDO",
                "El rol seleccionado no puede solicitar equipamiento.",
            )
        return usuario

    @api.exception_handler(ErrorCU01)
    async def manejar_error_cu01(_request: Any, error: ErrorCU01) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={
                "detail": {
                    "codigo": error.codigo,
                    "mensaje": error.mensaje,
                    "errores": error.errores,
                }
            },
        )

    @api.exception_handler(RequestValidationError)
    async def manejar_datos_invalidos(
        _request: Any, error: RequestValidationError
    ) -> JSONResponse:
        errores = [
            {
                "codigo": "DATO_INVALIDO",
                "mensaje": detalle["msg"],
                "campo": ".".join(str(parte) for parte in detalle["loc"][1:]) or None,
            }
            for detalle in error.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "detail": {
                    "codigo": "DATOS_INVALIDOS",
                    "mensaje": "Revise los datos de la solicitud.",
                    "errores": errores,
                }
            },
        )

    @api.get("/api/equipos/tipos", response_model=list[TipoEquipamientoSalida])
    def listar_tipos() -> list[Any]:
        return control_configurado().listar_tipos()

    @api.get("/api/materias", response_model=list[MateriaSalida])
    def listar_materias() -> list[Any]:
        return control_configurado().listar_materias()

    @api.post(
        "/api/solicitudes/prevalidar",
        response_model=ResultadoValidacionSalida,
    )
    def prevalidar(
        datos: DatosSolicitud,
        x_usuario_demo: str | None = Header(default=None, alias="X-Usuario-Demo"),
    ) -> dict[str, Any]:
        usuario = usuario_demo(x_usuario_demo)
        return control_configurado().prevalidar(datos, usuario)

    @api.post(
        "/api/solicitudes",
        response_model=SolicitudCreadaSalida,
        status_code=201,
    )
    def confirmar(
        datos: DatosSolicitud,
        x_usuario_demo: str | None = Header(default=None, alias="X-Usuario-Demo"),
    ) -> dict[str, Any]:
        usuario = usuario_demo(x_usuario_demo)
        return control_configurado().confirmar(datos, usuario)

    @api.get(
        "/api/solicitudes/mias",
        response_model=list[SolicitudListadoSalida],
    )
    def listar_propias(
        x_usuario_demo: str | None = Header(default=None, alias="X-Usuario-Demo"),
    ) -> list[Any]:
        usuario = usuario_demo(x_usuario_demo)
        return control_configurado().listar_de(usuario)

    # Se monta al final para que StaticFiles no intercepte las rutas /api.
    if montar_estaticos and DIRECTORIO_ESTATICO.is_dir():
        api.mount(
            "/",
            StaticFiles(directory=str(DIRECTORIO_ESTATICO), html=True),
            name="static",
        )

    return api


def crear_app_integrada(
    database_url: str = DATABASE_URL_DEFECTO,
    montar_estaticos: bool = True,
) -> FastAPI:
    """Ensambla la demo con SQLite, politica, repositorios y avisos internos."""
    argumentos_sqlite = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    motor = create_engine(database_url, connect_args=argumentos_sqlite)
    Base.metadata.create_all(bind=motor)

    fabrica_sesiones = sessionmaker(
        bind=motor,
        autoflush=False,
        autocommit=False,
    )
    with fabrica_sesiones() as sesion_inicial:
        poblar_datos_demo(sesion_inicial)

    sesion = scoped_session(fabrica_sesiones)
    catalogos = RepositorioCatalogos(sesion)
    calendario = CalendarioRecursos(sesion)
    politica = PoliticaPrestamo(
        calendario=calendario,
        consultar_disponibilidad=calendario.unidades_disponibles,
        consultar_restricciones=calendario.consultar_restricciones,
    )
    control = ControlPrestamos(
        politica=politica,
        catalogos=catalogos,
        solicitudes=RepositorioSolicitudes(sesion),
        notificador=NotificadorSolicitudes(sesion),
        auditor=AuditorSolicitudes(),
        crear_solicitud=crear_solicitud_prestamo,
    )
    return crear_app(
        control=control,
        resolver_usuario_demo=ResolutorUsuarioDemo(sesion),
        montar_estaticos=montar_estaticos,
    )


app = crear_app_integrada()
