# Contratos compartidos mínimos - CU_01

**Estado:** propuesta de integración para revisión humana. No reemplaza ni modifica el RFC o UML v9.3.

## Reglas comunes

- Sólo se implementa CU_01.
- `ControlPrestamos` coordina; no contiene SQL ni replica reglas de `PoliticaPrestamo`.
- La confirmación siempre vuelve a consultar catálogos y llama a `revalidar` antes de guardar.
- Toda solicitud creada queda en `PENDIENTE_SOLICITADA` y no consume disponibilidad.
- Los nombres públicos de las operaciones del dominio siguen `Contrato_UML_v9_3.json`.
- En Python se admite `snake_case`; cada equivalencia con el nombre UML se documenta en el código o los tests.

## Usuario de demostración

El selector del frontend envía el header `X-Usuario-Demo` en las tres operaciones que dependen de identidad. Su valor es un alias estable, no un UUID ingresado libremente. Ejemplos de aliases a definir en el seed: `estudiante-comun`, `estudiante-elegible` y `docente-demo`.

La capa API resuelve el alias contra usuarios ficticios precargados. Alias ausente, desconocido o de un rol no permitido produce HTTP `403`. Esta selección es simulación explícita, no autenticación.

## DTO de entrada

`DatosSolicitud`:

```json
{
  "tipo_id": "CAMARA",
  "cantidad": 1,
  "desde": "2026-11-20T10:00:00",
  "hasta": "2026-11-22T10:00:00",
  "materia_id": "uuid-o-identificador-del-seed"
}
```

El usuario no forma parte del cuerpo. Los intervalos se interpretan como `[desde, hasta)`.

## Resultado de validación

```json
{
  "valido": true,
  "requiere_aval": false,
  "errores": [],
  "resumen": {
    "tipo": "Cámara",
    "cantidad": 1,
    "desde": "2026-11-20T10:00:00",
    "hasta": "2026-11-22T10:00:00",
    "materia": "Proyecto 2"
  }
}
```

Cada error tiene `codigo`, `mensaje` y, cuando corresponde, `campo`.

## API HTTP

| Método y ruta | Identidad | Respuesta mínima |
| --- | --- | --- |
| `GET /api/equipos/tipos` | No | Lista `id`, `nombre`, `alta_gama` |
| `GET /api/materias` | No | Lista `id`, `nombre` |
| `POST /api/solicitudes/prevalidar` | `X-Usuario-Demo` | `ResultadoValidacion`, HTTP 200 si puede mostrarse resumen |
| `POST /api/solicitudes` | `X-Usuario-Demo` | `numero`, `estado`, `requiere_aval`, `advertencias`; HTTP 201 |
| `GET /api/solicitudes/mias` | `X-Usuario-Demo` | Solicitudes del usuario demo actual |

Errores compartidos: `422` para campos inválidos o catálogo inexistente, `403` para rol/restricción/elegibilidad, `409` para indisponibilidad o cambio detectado al confirmar, y `500` para fallo de persistencia. Nunca se responde éxito si solicitud e historial no fueron guardados.

Si la solicitud fue guardada pero falla un aviso, se conserva la solicitud y la respuesta 201 incluye una advertencia. No se implementan reintentos automáticos.

## Colaboradores de ControlPrestamos

Se inyectan como objetos simples; no hace falta crear un framework de interfaces.

| Colaborador | Operaciones Python acordadas | Correspondencia UML |
| --- | --- | --- |
| `RepositorioCatalogos` | `listar_tipos()`, `listar_materias()`, `obtener_tipo(tipo_id)`, `obtener_materia(materia_id)` | `obtenerTipo`, `obtenerMateria`; los listados son soporte técnico de los endpoints |
| `PoliticaPrestamo` | `evaluar(datos, usuario, tipo, materia)`, `revalidar(...)` | `evaluar`, `revalidar` |
| `AuditorSolicitudes` | `registrar_alta(solicitud, usuario)` | `registrarAlta` |
| `RepositorioSolicitudes` | `guardar_con_historial(solicitud)`, `listar_de(usuario_id)` | `guardarConHistorial`, `listarDe` |
| `NotificadorSolicitudes` | `avisar_aval(solicitud, materia)` | `avisarAval` |
| Resolutor demo | callable `resolver(alias) -> Usuario` | Usuario identificado en sesión demo |
| Fábrica inyectada | callable `crear_solicitud(datos, usuario, tipo, materia, requiere_aval) -> SolicitudPrestamo` | Constructor de `SolicitudPrestamo`; ControlPrestamos conserva la responsabilidad de creación |

Los métodos para listar catálogos y resolver aliases son detalles técnicos necesarios para la API/demo. No agregan reglas al modelo académico.

## Responsabilidad por archivo

| Integrante | Archivos principales |
| --- | --- |
| 1 | `app/main.py`, `app/controller.py`, `app/schemas.py`, `tests/test_api.py` |
| 2 | `app/politica.py`, `tests/test_validacion.py` |
| 3 | `app/models.py`, `app/repository.py`, `app/notifications.py`, `scripts/seed_demo.py`, `tests/test_solicitudes.py` |
| 4 | `app/static/`, `tests/test_interfaz.py`, evidencias de demo |

Un cambio que necesite editar archivos de otra persona se acuerda antes de hacerlo.
