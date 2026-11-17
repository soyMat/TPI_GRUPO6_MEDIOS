# Alcance práctico del prototipo CU_01

Este documento registra decisiones de implementación para la demostración de Ingeniería de Software I. No modifica los requerimientos, el RFC aprobado ni los diagramas UML v9.3.

## Objetivo

Construir una aplicación web pequeña que permita seleccionar un usuario ficticio, completar una solicitud de equipamiento, prevalidarla, confirmarla en estado `Pendiente/Solicitada` y consultarla en "Mis solicitudes".

## Simplificaciones autorizadas

- La identidad se simula con un usuario ficticio seleccionado en la interfaz. La API recibe el alias mediante `X-Usuario-Demo` y sólo acepta aliases precargados. No hay login ni seguridad productiva.
- SQLite y el conjunto inicial de datos son locales. No se versionan archivos `.db`.
- El frontend deshabilita `Confirmar` mientras la petición está en curso. No se implementan claves de idempotencia, hashes ni protección productiva contra solicitudes repetidas.
- Los avisos de aval se guardan directamente como notificaciones internas. No hay correo, colas ni reintentos.
- Las pruebas se concentran en el flujo principal, errores de datos, disponibilidad, restricciones, alta gama, revalidación y consulta posterior.
- No se agregan Docker, microservicios, autenticación real ni casos de uso distintos de CU_01.

## Límites que deben explicarse en la demo

- Seleccionar otro usuario demo no equivale a autenticarse.
- Una solicitud pendiente no reserva ni entrega equipos.
- Deshabilitar un botón evita el doble clic normal de la interfaz, pero no es idempotencia de backend.
- Una notificación interna es un registro local, no un correo enviado.
- Los TC se consideran cumplidos sólo cuando fueron ejecutados y se conserva evidencia real.

## Fuente de verdad

En caso de contradicción, detener el cambio y revisar, en este orden:

1. `documentacion/TPI_GRUPO6_ETAPA4/RFC/RFC_CU01_APROBADO_BUILD.md`.
2. `documentacion/TPI_GRUPO6_ETAPA4/Entrega/TPI_GRUPO6_ETAPA4.pdf`.
3. `documentacion/TPI_GRUPO6_ETAPA4/Fuentes/Contrato_UML_v9_3.json`.
4. `documentacion/TPI_GRUPO6_ETAPA4/Equipo/CONTRATOS_COMPARTIDOS.md` para detalles técnicos mínimos.
