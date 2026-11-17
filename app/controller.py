"""Coordinación del CU_01 sin implementar reglas ni persistencia concretas."""

from collections.abc import Callable
from typing import Any

from app.schemas import DatosSolicitud, leer_atributo


class ErrorCU01(Exception):
    """Error controlado que la capa HTTP traduce al estado correspondiente."""

    def __init__(
        self,
        status_code: int,
        codigo: str,
        mensaje: str,
        errores: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(mensaje)
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        self.errores = errores or []


class ControlPrestamos:
    """Orquesta colaboradores del CU_01 mediante inyección simple por constructor."""

    def __init__(
        self,
        politica: Any,
        catalogos: Any,
        solicitudes: Any,
        notificador: Any,
        auditor: Any,
        crear_solicitud: Callable[..., Any],
    ) -> None:
        self.politica = politica
        self.catalogos = catalogos
        self.solicitudes = solicitudes
        self.notificador = notificador
        self.auditor = auditor
        self.crear_solicitud = crear_solicitud

    def listar_tipos(self) -> list[Any]:
        return self.catalogos.listar_tipos()

    def listar_materias(self) -> list[Any]:
        return self.catalogos.listar_materias()

    def prevalidar(self, datos: DatosSolicitud, usuario: Any) -> dict[str, Any]:
        """Consulta catálogos y delega las reglas sin modificar datos persistentes."""

        tipo, materia = self._obtener_catalogos(datos)
        resultado = self.politica.evaluar(datos, usuario, tipo, materia)
        return self._resultado_valido(resultado, datos, tipo, materia)

    def confirmar(self, datos: DatosSolicitud, usuario: Any) -> dict[str, Any]:
        """Revalida y registra únicamente una solicitud pendiente con su historial."""

        # Los catálogos y las reglas se vuelven a consultar porque la disponibilidad
        # pudo cambiar desde la pantalla de resumen.
        tipo, materia = self._obtener_catalogos(datos)
        resultado = self.politica.revalidar(datos, usuario, tipo, materia)
        resultado_normalizado = self._resultado_valido(
            resultado, datos, tipo, materia
        )
        requiere_aval = resultado_normalizado["requiere_aval"]

        # Solicitud e historial se guardan antes de avisar. Si esta parte falla, la
        # API nunca devuelve un número de solicitud ni un falso éxito.
        try:
            solicitud = self.crear_solicitud(
                datos, usuario, tipo, materia, requiere_aval
            )
            self.auditor.registrar_alta(solicitud, usuario)
            self.solicitudes.guardar_con_historial(solicitud)
        except ErrorCU01:
            raise
        except Exception as error:
            raise ErrorCU01(
                500,
                "ERROR_PERSISTENCIA",
                "No fue posible registrar la solicitud.",
            ) from error

        advertencias: list[str] = []
        if requiere_aval:
            # El RFC permite conservar la solicitud si falla el aviso posterior;
            # la advertencia hace visible esa diferencia durante la demostración.
            try:
                self.notificador.avisar_aval(solicitud, materia)
            except Exception:
                advertencias.append(
                    "La solicitud fue registrada, pero no se pudo guardar el aviso interno."
                )

        return {
            "numero": str(leer_atributo(solicitud, "numero")),
            "estado": self._texto_estado(
                leer_atributo(solicitud, "estado", "PENDIENTE_SOLICITADA")
            ),
            "requiere_aval": requiere_aval,
            "advertencias": advertencias,
        }

    def listar_de(self, usuario: Any) -> list[Any]:
        usuario_id = leer_atributo(usuario, "id")
        return self.solicitudes.listar_de(usuario_id)

    def _obtener_catalogos(self, datos: DatosSolicitud) -> tuple[Any, Any]:
        try:
            tipo = self.catalogos.obtener_tipo(datos.tipo_id)
            materia = self.catalogos.obtener_materia(datos.materia_id)
        except (KeyError, LookupError) as error:
            raise ErrorCU01(
                422,
                "CATALOGO_INVALIDO",
                "El tipo de equipamiento o la materia no existe.",
            ) from error
        return tipo, materia

    def _resultado_valido(
        self, resultado: Any, datos: DatosSolicitud, tipo: Any, materia: Any
    ) -> dict[str, Any]:
        valido = bool(leer_atributo(resultado, "valido", False))
        requiere_aval = bool(leer_atributo(resultado, "requiere_aval", False))
        errores = [
            self._normalizar_error(error)
            for error in leer_atributo(resultado, "errores", [])
        ]

        if not valido:
            status_code = self._status_para_errores(errores)
            raise ErrorCU01(
                status_code,
                errores[0]["codigo"] if errores else "SOLICITUD_INVALIDA",
                errores[0]["mensaje"] if errores else "La solicitud no es válida.",
                errores,
            )

        return {
            "valido": True,
            "requiere_aval": requiere_aval,
            "errores": [],
            "resumen": {
                "tipo": str(leer_atributo(tipo, "nombre", datos.tipo_id)),
                "cantidad": datos.cantidad,
                "desde": datos.desde,
                "hasta": datos.hasta,
                "materia": str(
                    leer_atributo(materia, "nombre", datos.materia_id)
                ),
            },
        }

    @staticmethod
    def _normalizar_error(error: Any) -> dict[str, Any]:
        return {
            "codigo": str(leer_atributo(error, "codigo", "SOLICITUD_INVALIDA")),
            "mensaje": str(leer_atributo(error, "mensaje", "Solicitud inválida")),
            "campo": leer_atributo(error, "campo"),
        }

    @staticmethod
    def _status_para_errores(errores: list[dict[str, Any]]) -> int:
        """Agrupa errores de dominio en los estados HTTP acordados por el equipo."""

        codigos = {error["codigo"] for error in errores}
        if codigos & {"SIN_DISPONIBILIDAD", "DISPONIBILIDAD_CAMBIO"}:
            return 409
        if codigos & {"RESTRICCION_ACTIVA", "NO_ELEGIBLE", "ROL_NO_PERMITIDO"}:
            return 403
        return 422

    @staticmethod
    def _texto_estado(estado: Any) -> str:
        return str(getattr(estado, "value", estado))
