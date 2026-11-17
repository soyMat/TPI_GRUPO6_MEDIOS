"""API FastAPI del prototipo CU_01."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.controller import ControlPrestamos, ErrorCU01
from app.schemas import (
    DatosSolicitud,
    MateriaSalida,
    ResultadoValidacionSalida,
    SolicitudCreadaSalida,
    SolicitudListadoSalida,
    TipoEquipamientoSalida,
    leer_atributo,
)


DIRECTORIO_ESTATICO = Path(__file__).resolve().parent / "static"


def crear_app(
    control: ControlPrestamos | None = None,
    resolver_usuario_demo: Callable[[str], Any] | None = None,
) -> FastAPI:
    """Construye la API permitiendo inyectar colaboradores reales o dobles de prueba."""

    api = FastAPI(title="Prototipo CU_01 - Grupo 6")

    # Mientras los otros módulos no estén integrados, la API informa el faltante
    # en lugar de simular una operación exitosa.
    def control_configurado() -> ControlPrestamos:
        if control is None:
            raise ErrorCU01(
                503,
                "DEPENDENCIAS_NO_CONFIGURADAS",
                "La integración del prototipo todavía no fue configurada.",
            )
        return control

    def usuario_demo(alias: str | None) -> Any:
        # El alias sólo identifica datos ficticios de la demo; no es autenticación.
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

        rol = str(leer_atributo(usuario, "rol", "")).lower()
        if rol not in {"estudiante", "docente"}:
            raise ErrorCU01(
                403,
                "ROL_NO_PERMITIDO",
                "El rol seleccionado no puede solicitar equipamiento.",
            )
        return usuario

    # Todos los errores propios del caso de uso mantienen una respuesta uniforme
    # para que el frontend pueda mostrar código, mensaje y campos afectados.
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

    # El montaje debe quedar después de las rutas /api para que StaticFiles no las
    # intercepte. La ruta absoluta permite iniciar Uvicorn desde cualquier carpeta.
    api.mount(
        "/",
        StaticFiles(directory=DIRECTORIO_ESTATICO, html=True),
        name="static",
    )

    return api


# La integración real se configurará cuando lleguen los módulos de los integrantes 2 y 3.
app = crear_app()
