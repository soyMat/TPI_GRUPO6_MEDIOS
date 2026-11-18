"""Reglas de negocio y cálculo de disponibilidad del CU_01."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from typing import Any

from app.schemas import DatosSolicitud, leer_atributo

ESTADOS_EQUIPO_OPERATIVO = {"OPERATIVO", "DISPONIBLE", "ACTIVO"}
ESTADOS_OCUPACION_EFECTIVA = {
    "APROBADA",
    "APROBADA_CONFIRMADA",
    "CONFIRMADA",
    "EN_CURSO",
    "EN_CURSO_RETIRADO",
    "ACTIVA",
    "RESERVADA",
}
ROLES_PERMITIDOS_CU01 = {"ESTUDIANTE", "DOCENTE"}
DURACION_ESTANDAR_HORAS = 48


def sugerir_vencimiento_estandar(desde: datetime) -> datetime:
    """Devuelve el vencimiento sugerido estándar de 48 horas (RNF-03 / D-04)."""
    return desde + timedelta(hours=DURACION_ESTANDAR_HORAS)


def intervalos_solapan(
    inicio_a: datetime,
    fin_a: datetime,
    inicio_b: datetime,
    fin_b: datetime,
) -> bool:
    """Evalúa solapamiento en intervalos semiabiertos [desde, hasta)."""
    return inicio_a < fin_b and inicio_b < fin_a


def _normalizar_texto(valor: Any) -> str:
    texto = getattr(valor, "value", valor)
    return str(texto).strip().upper() if texto is not None else ""


def _es_verdadero(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return valor != 0
    if isinstance(valor, str):
        return valor.strip().lower() in {"1", "true", "si", "sí", "yes", "verdadero"}
    return False


class PoliticaPrestamo:
    "Evalúa y revalida reglas de negocio y disponibilidad para CU_01."

    def __init__(
        self,
        calendario: Any | None = None,
        consultar_disponibilidad: Callable[[str, datetime, datetime], int] | None = None,
        consultar_restricciones: Callable[..., Iterable[Any]] | None = None,
    ) -> None:
        self.calendario = calendario
        self.consultar_disponibilidad = consultar_disponibilidad
        self.consultar_restricciones = consultar_restricciones

    def evaluar(
        self,
        datos: DatosSolicitud,
        usuario: Any,
        tipo: Any,
        materia: Any,
    ) -> dict[str, Any]:
        """Equivalente UML: PoliticaPrestamo.evaluar."""
        return self._ejecutar_validacion(
            datos=datos,
            usuario=usuario,
            tipo=tipo,
            materia=materia,
            es_revalidacion=False,
        )

    def revalidar(
        self,
        datos: DatosSolicitud,
        usuario: Any,
        tipo: Any,
        materia: Any,
    ) -> dict[str, Any]:
        """Equivalente UML: PoliticaPrestamo.revalidar (invocado al confirmar)."""
        return self._ejecutar_validacion(
            datos=datos,
            usuario=usuario,
            tipo=tipo,
            materia=materia,
            es_revalidacion=True,
        )

    def calcular_disponibles(
        self,
        tipo: Any,
        desde: datetime,
        hasta: datetime,
    ) -> int:
        """Calcula unidades operativas libres en [desde, hasta) usando ocupaciones efectivas."""
        tipo_id = str(leer_atributo(tipo, "id", leer_atributo(tipo, "codigo", "")))

        if self.consultar_disponibilidad is not None:
            return max(0, int(self.consultar_disponibilidad(tipo_id, desde, hasta)))

        if self.calendario is not None:
            if hasattr(self.calendario, "unidades_disponibles"):
                return max(
                    0,
                    int(self.calendario.unidades_disponibles(tipo_id, desde, hasta)),
                )
            if hasattr(self.calendario, "disponibles"):
                return max(
                    0,
                    int(self.calendario.disponibles(tipo_id, desde, hasta)),
                )

        equipos = leer_atributo(tipo, "equipos", None)
        if equipos is None and self.calendario is not None:
            equipos = leer_atributo(self.calendario, "equipos", [])

        if equipos is None:
            disponibles_directos = leer_atributo(tipo, "unidades_disponibles", None)
            if disponibles_directos is not None:
                return max(0, int(disponibles_directos))
            return 0

        operativos = [
            eq
            for eq in equipos
            if (
                not tipo_id
                or str(leer_atributo(eq, "tipo_id", tipo_id)) == tipo_id
            )
            and self._equipo_operativo(eq)
        ]

        ocupaciones = leer_atributo(tipo, "ocupaciones", None)
        if ocupaciones is None and self.calendario is not None:
            ocupaciones = leer_atributo(self.calendario, "ocupaciones", [])
        ocupaciones = list(ocupaciones or [])

        ids_operativos = {
            str(leer_atributo(eq, "inventario", leer_atributo(eq, "id", idx)))
            for idx, eq in enumerate(operativos)
        }

        unidades_ocupadas = 0
        for ocupacion in ocupaciones:
            oc_tipo = leer_atributo(ocupacion, "tipo_id", None)
            if oc_tipo is not None and tipo_id and str(oc_tipo) != tipo_id:
                continue

            estado_oc = _normalizar_texto(leer_atributo(ocupacion, "estado", "ACTIVA"))
            if estado_oc not in ESTADOS_OCUPACION_EFECTIVA:
                continue

            oc_desde = leer_atributo(ocupacion, "desde")
            oc_hasta = leer_atributo(ocupacion, "hasta")
            if oc_desde is None or oc_hasta is None:
                continue

            if not intervalos_solapan(desde, hasta, oc_desde, oc_hasta):
                continue

            equipo_id = leer_atributo(ocupacion, "equipo_id", None)
            if equipo_id is not None:
                if str(equipo_id) in ids_operativos:
                    unidades_ocupadas += 1
            else:
                unidades_ocupadas += int(leer_atributo(ocupacion, "cantidad", 1))

        return max(0, len(operativos) - unidades_ocupadas)

    def _ejecutar_validacion(
        self,
        datos: DatosSolicitud,
        usuario: Any,
        tipo: Any,
        materia: Any,
        es_revalidacion: bool,
    ) -> dict[str, Any]:
        errores: list[dict[str, Any]] = []

        errores.extend(self._validar_campos(datos))
        if errores:
            return self._construir_resultado(
                valido=False,
                requiere_aval=False,
                errores=errores,
                datos=datos,
                tipo=tipo,
                materia=materia,
            )

        errores.extend(self._validar_rol(usuario))
        if errores:
            return self._construir_resultado(
                valido=False,
                requiere_aval=False,
                errores=errores,
                datos=datos,
                tipo=tipo,
                materia=materia,
            )

        errores.extend(self._validar_restricciones(usuario, tipo, datos.desde, datos.hasta))

        elegible, requiere_aval, error_elegibilidad = self._evaluar_elegibilidad_y_aval(
            usuario=usuario,
            tipo=tipo,
            materia=materia,
        )
        if not elegible and error_elegibilidad is not None:
            errores.append(error_elegibilidad)

        errores.extend(
            self._validar_disponibilidad(
                datos=datos,
                tipo=tipo,
                es_revalidacion=es_revalidacion,
            )
        )

        valido = len(errores) == 0
        return self._construir_resultado(
            valido=valido,
            requiere_aval=requiere_aval if valido else False,
            errores=errores,
            datos=datos,
            tipo=tipo,
            materia=materia,
        )

    @staticmethod
    def _validar_campos(datos: DatosSolicitud) -> list[dict[str, Any]]:
        errores: list[dict[str, Any]] = []

        if not str(leer_atributo(datos, "tipo_id", "")).strip():
            errores.append(
                {
                    "codigo": "CAMPO_REQUERIDO",
                    "mensaje": "Debe seleccionar un tipo de equipamiento.",
                    "campo": "tipo_id",
                }
            )

        if not str(leer_atributo(datos, "materia_id", "")).strip():
            errores.append(
                {
                    "codigo": "CAMPO_REQUERIDO",
                    "mensaje": "Debe seleccionar una materia o proyecto.",
                    "campo": "materia_id",
                }
            )

        cantidad = leer_atributo(datos, "cantidad", 0)
        if cantidad is None or int(cantidad) <= 0:
            errores.append(
                {
                    "codigo": "CANTIDAD_INVALIDA",
                    "mensaje": "La cantidad solicitada debe ser mayor a cero.",
                    "campo": "cantidad",
                }
            )

        desde = leer_atributo(datos, "desde")
        hasta = leer_atributo(datos, "hasta")
        if desde is None or hasta is None:
            errores.append(
                {
                    "codigo": "FECHA_REQUERIDA",
                    "mensaje": "Debe indicar fecha y hora de inicio y devolución.",
                    "campo": "desde" if desde is None else "hasta",
                }
            )
        elif desde >= hasta:
            errores.append(
                {
                    "codigo": "RANGO_FECHAS_INVALIDO",
                    "mensaje": "La fecha de devolución debe ser posterior al inicio.",
                    "campo": "hasta",
                }
            )

        return errores

    @staticmethod
    def _validar_rol(usuario: Any) -> list[dict[str, Any]]:
        rol = _normalizar_texto(leer_atributo(usuario, "rol", ""))
        if rol not in ROLES_PERMITIDOS_CU01:
            return [
                {
                    "codigo": "ROL_NO_PERMITIDO",
                    "mensaje": "El rol del usuario no está habilitado para solicitar préstamos.",
                    "campo": None,
                }
            ]
        return []

    def _validar_restricciones(
        self,
        usuario: Any,
        tipo: Any,
        desde: datetime,
        hasta: datetime,
    ) -> list[dict[str, Any]]:
        tipo_id = str(leer_atributo(tipo, "id", leer_atributo(tipo, "codigo", "")))
        restricciones: list[Any] = []

        if self.consultar_restricciones is not None:
            restricciones.extend(self.consultar_restricciones(usuario, tipo, desde, hasta))
        else:
            restricciones.extend(leer_atributo(usuario, "restricciones", []) or [])
            restricciones.extend(leer_atributo(tipo, "restricciones", []) or [])

        for restriccion in restricciones:
            activa = leer_atributo(restriccion, "activa", True)
            if not _es_verdadero(activa):
                continue

            inicio = leer_atributo(restriccion, "inicio", leer_atributo(restriccion, "desde"))
            fin = leer_atributo(restriccion, "fin", leer_atributo(restriccion, "hasta"))
            if inicio is not None and fin is not None:
                if not intervalos_solapan(desde, hasta, inicio, fin):
                    continue

            alcance_tipo = leer_atributo(
                restriccion,
                "tipo_equipamiento_id",
                leer_atributo(restriccion, "tipo_id", None),
            )
            if alcance_tipo is not None and str(alcance_tipo) != tipo_id:
                continue

            motivo = str(
                leer_atributo(
                    restriccion,
                    "motivo",
                    leer_atributo(
                        restriccion,
                        "descripcion",
                        "Existe una restricción activa que impide solicitar este equipamiento.",
                    ),
                )
            )
            return [
                {
                    "codigo": "RESTRICCION_ACTIVA",
                    "mensaje": motivo,
                    "campo": "tipo_id",
                }
            ]

        return []

    @staticmethod
    def _evaluar_elegibilidad_y_aval(
        usuario: Any,
        tipo: Any,
        materia: Any,
    ) -> tuple[bool, bool, dict[str, Any] | None]:
        es_alta_gama = _es_verdadero(leer_atributo(tipo, "alta_gama", False))
        if not es_alta_gama:
            return True, False, None

        rol = _normalizar_texto(leer_atributo(usuario, "rol", ""))
        if rol == "DOCENTE":
            # No aplicar reglas académicas exclusivas de Estudiante a Docente (TC-13)
            return True, False, None

        # Regla D-03 / sección 9.1: elegibilidad explícita en datos del estudiante o materia avanzada
        elegible_usuario = _es_verdadero(
            leer_atributo(
                usuario,
                "elegible_alta_gama",
                leer_atributo(usuario, "tesista_avanzado", False),
            )
        )
        materia_avanzada = _es_verdadero(
            leer_atributo(
                materia,
                "habilita_alta_gama",
                leer_atributo(materia, "avanzada", False),
            )
        )

        if elegible_usuario or materia_avanzada:
            # Estudiante elegible + alta gama -> válido pero requiere aval docente (TC-10)
            return True, True, None

        return (
            False,
            False,
            {
                "codigo": "NO_ELEGIBLE",
                "mensaje": (
                    "El equipamiento de alta gama requiere condición académica habilitada "
                    "(tesista o materia avanzada)."
                ),
                "campo": "tipo_id",
            },
        )

    def _validar_disponibilidad(
        self,
        datos: DatosSolicitud,
        tipo: Any,
        es_revalidacion: bool,
    ) -> list[dict[str, Any]]:
        disponibles = self.calcular_disponibles(tipo, datos.desde, datos.hasta)
        if disponibles < datos.cantidad:
            codigo = (
                "DISPONIBILIDAD_CAMBIO"
                if es_revalidacion
                else "SIN_DISPONIBILIDAD"
            )
            return [
                {
                    "codigo": codigo,
                    "mensaje": (
                        f"No hay disponibilidad suficiente para el período solicitado "
                        f"(disponibles: {disponibles}, solicitadas: {datos.cantidad})."
                    ),
                    "campo": "cantidad",
                }
            ]
        return []

    @staticmethod
    def _equipo_operativo(equipo: Any) -> bool:
        estado = _normalizar_texto(leer_atributo(equipo, "estado", "OPERATIVO"))
        return estado in ESTADOS_EQUIPO_OPERATIVO

    @staticmethod
    def _construir_resultado(
        valido: bool,
        requiere_aval: bool,
        errores: list[dict[str, Any]],
        datos: DatosSolicitud,
        tipo: Any,
        materia: Any,
    ) -> dict[str, Any]:
        return {
            "valido": valido,
            "requiere_aval": requiere_aval,
            "errores": errores,
            "resumen": {
                "tipo": str(leer_atributo(tipo, "nombre", datos.tipo_id)),
                "cantidad": datos.cantidad,
                "desde": datos.desde,
                "hasta": datos.hasta,
                "materia": str(leer_atributo(materia, "nombre", datos.materia_id)),
            },
        }