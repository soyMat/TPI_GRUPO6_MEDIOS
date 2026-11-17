# Grupo 6 · Etapa 4 — Control de notación UML v9.3

**Fecha:** 17/11/2026. **Base:** v9.2 ya corregida, RFC aprobado para Build del prototipo CU_01. **Propósito:** mejorar notación/legibilidad sin rediseñar GRASP ni reescribir entrevistas, requerimientos, especificaciones o casos de uso.

**Alcance de la aprobación:** el RFC está aprobado para **BUILD de CU_01 por el solicitante**. No hay aprobación del docente ni se ejecutaron todavía las pruebas de implementación.

## Criterios de la cátedra efectivamente comprobados

- **Observaciones escritas de la tercera entrega, p. 6:** una sola perspectiva de clases; los objetos de interacción deben corresponder a clases reales, los mensajes a operaciones receptoras reales, el emisor debe ver al receptor; números anidados y creación dirigida a la caja del objeto.
- **UML-Interacción, pp. 3–6:** activaciones como rectángulos sobre la línea de vida; mensajes sincrónicos con línea continua; `«create»` hacia la cabecera del objeto creado; mensajes numerados sobre enlaces y dirección de flecha en comunicación; objetos `objeto:Clase`.
- **Modelado de la Dinámica del Sistema con UML, pp. 30–33, 35–39, 45–48:** equivalencia semántica entre secuencia/comunicación, uso de escenarios para comportamiento condicional complejo, elementos de actividades y estados con eventos/transiciones.
- **Modelo de Diseño, pp. 4–12:** visibilidad por atributo, parámetro, local y global; el objeto recibido de una operación puede tener visibilidad local.
- **Consigna de cuarta entrega, p. 1:** DCD/GRASP, actividad con paralelismo, estados y RFC/prototipo del CU crítico.

## Qué se evaluó antes de corregir

La v9.2 **ya cumplía** gran parte de lo que pedía el nuevo prompt: objeto subrayado, activaciones, creación síncrona y en posición de creación, `alt` con guardas, comunicación con mensajes sobre enlaces, auto-mensaje `3: crearEstudiante(datos)` de CU_07, dependencia ControlRegistro → RepositorioUsuarios, relaciones generales de notificaciones y emergencias, y estados `evento [guarda] / efecto`. Rehacerlo habría introducido riesgos nuevos.

## Cambios efectivamente aplicados en v9.3

| Punto del pedido | Tratamiento | Comprobación / límite |
|---|---|---|
| 1 — Actividad CU_01 | **Corregido:** todas las salidas de decisión se rotularon `[sí]`, `[no]`, `[volver]`, `[cancelar]`, `[confirmar]`. Se reubicó `[volver]` junto al arco de salida de la decisión, lejos del fork. | Se conservaron nodos, tres validaciones paralelas, fork/join, merges y revalidación. No se agregaron swimlanes para evitar modificar su flujo. |
| 2 — CU_01 secuencia | **Ajustado:** el acceso a `Estudiante.getAnioCursada()` se colocó en `opt [tipo.altaGama]`; activaciones, `«create»` con flecha continua, guardas y anidamientos estaban ya incluidos. | Escenario **Estudiante**. La rama válida de equipamiento común/sin aval es la que se muestra en comunicación. Error/volver/cancelar quedan en operandos excluyentes del `alt`. |
| 3 — CU_02 secuencia | **Corregido:** `getVenceEn()` ocurre antes del `alt` inicial, que distingue `[préstamo inactivo o vencido]` y `[activo y no vencido]`. Se sincronizó el orden con JSON, CSV y matriz del Word. | Si es inválido, vuelve al listado; conflicto o desistimiento tampoco crea `SolicitudProrroga`. Las activaciones ya estaban modeladas. |
| 4 — CU_01 comunicación | **Mejorado el trazado:** se redujo el espacio vacío y se reposicionaron mensajes para separarlos de los objetos. Se mantienen números jerárquicos, flechas dirigidas y métodos sobre el enlace; sin tarjetas A/B/C. | Deliberadamente representa **un subescenario exitoso** (Estudiante + equipamiento común, sin aval), siguiendo la recomendación de separar alternativas complejas. No representa todas las extensiones. |
| 5 — CU_07 comunicación | **Verificado sin rediseño:** existe `3: crearEstudiante(datos)` como auto-mensaje, seguido de `3.1: «create» Estudiante(datos)` y `3.2: guardar(estudiante)`. `existeDni`, `existeCorreo` y `guardar` van de `ControlRegistro` a `RepositorioUsuarios`. | Se mantiene el bloque `[válido]` y el aviso `[inválido o duplicado]`. |
| 6 — DCD | **Se conserva la arquitectura:** mismas 62 clases, 90 relaciones, responsabilidades, abstracciones y clases interpuestas de v9.2. Las flechas de navegabilidad de asociación/dependencia se ajustaron a punta abierta; generalizaciones/realizaciones siguen con triángulo hueco. | Se entrega un **póster vectorial del mismo DCD**, con una leyenda integrada de las 90 relaciones y multiplicidades para consultar sin CSV. La Figura 2 del Word sigue siendo una única figura. La legibilidad a tamaño de impresión normal sigue limitada por la densidad del modelo. |
| 6A / 6B — Avisos y emergencia | **Ya corregido en v9.2:** notificaciones con un único origen opcional entre solicitud/préstamo/reserva/emergencia; emergencia incluye reserva, retiro programado y tutoría mediante sus clases de afectación. | No se agregaron nuevas clases en v9.3. No forman parte del prototipo CU_01 salvo avisos de solicitudes. |
| 7 — Visibilidad | **Verificado:** la matriz y relaciones usan `atributo`, `parámetro`, `variable local` o `creación` (más `self` para auto-mensaje). | `creación` y `self` se usan como categorías de la comprobación de mensajes; las formas teóricas básicas siguen siendo cuatro. `retorno` no se trata como quinta forma. |
| 8 — Estados | **Conservado:** `evento [guarda] / efecto` y referencias CU como aclaración; estados sin modificación. | Pendiente/Solicitada no es un préstamo físico. |
| 9 — Casos de uso | **Conservado:** único límite del sistema; no se eliminaron los `«extend»` CU_07/CU_08 solicitados por el profesor ni la continuidad CU_21/CU_16. | El tamaño de la figura y la lectura exacta de los puntos de extensión deben revisarse a escala real con el docente; no se reinterpretaron. |
| 10 — Objetos subrayados | **Ya cumplido:** `objeto:Clase` subrayado en secuencia y comunicación. | Sin cambios conceptuales. |
| 11 — Documento | **Actualizado:** figuras/captions 2, 3, 4, 5 y 8; explicación de actividades; título 11.5 a «Decisiones definidas para la demo y controles pendientes»; trazabilidad de mensajes CU_02. | Portada y páginas 1–34 idénticas visualmente a v9.2. 47 páginas en total. |
| 12 — RFC | **Sin cambio de decisiones:** se conservó el RFC «Aprobado para Build» y únicamente se actualizaron referencias a los nombres de fuentes UML v9.3. | 19 páginas, sin declaración de instalación ni pruebas ejecutadas. |
| 13 — Validación | **Ejecutada:** verificación de las clases/operaciones receptoras, cantidad de argumentos, relación/visibilidad mecánica y clases declaradas; inspección visual de secuencias, comunicación y actividades. | La validación mecánica no prueba por sí sola conformidad conceptual o de tipos de parámetros en ejecución. |

## Verificaciones registradas

| Control | Resultado |
|---|---|
| Clases en contrato | 62 |
| Relaciones en contrato | 90 |
| Eventos/mensajes de CU_01, CU_02 y CU_07 | 84 |
| Llamadas internas con operación, aridad y visibilidad respaldadas | **71/71, cero fallos mecánicos** |
| Rótulos `2.alt`, `3.alt`, `4.alt` | No se usan |
| `«create»` con mensaje síncrono dirigido a cabecera | Conservado |
| DCD dividido | No, una sola figura; póster de lectura ampliada del **mismo modelo** |
| PDF TPI | 47 páginas |
| PDF RFC | 19 páginas |
| Portada y páginas 1–34 respecto a v9.2 | **Sin diferencias de imagen** a escala de control |
| Aplicación construida / TC01–TC16 probados | **No**, continúa Build/Validate |

## Riesgos que NO sería responsable ocultar

1. El **DCD tiene 62 clases y 90 relaciones**, y leer todas sus conexiones sobre una página A1/A2 sin ampliar sigue siendo difícil. Se adjunta un SVG/PDF vectorial ampliable con las relaciones incorporadas en la misma lámina. Este mecanismo ayuda pero **no garantiza** que el profesor considere suficiente su presentación visual.
2. CU_01 secuencia cubre **Estudiante**; la prueba de **Docente** está prevista en el RFC, pero no fingimos que ambos actores ejecutan la misma ruta académica. Para un sistema real debería dibujarse o implementarse una rama específica de docente.
3. CU_01 comunicación es un **subescenario del CU_01 secuencia**, no una copia íntegra de todas las alternativas. Esta elección es coherente con la recomendación de la teoría cuando el caso tiene mucha lógica condicional.
4. La guarda de préstamo vigente en CU_02 se verifica en la selección; el contrato de confirmación conserva una revalidación de estado/conflicto. La comparación exacta del reloj con vencimiento durante la confirmación puede requerir otra lectura de fecha en una implementación completa de CU_02, que **no se desarrollará** en este prototipo.
5. Las asociaciones de notificaciones/emergencias extienden la **cobertura del diseño acumulado**, no la implementación del CU_01. Ninguna aprobación del docente se presupone.

## Recomendación

Usar **v9.3** como versión UML para revisión final del grupo; trabajar con el RFC **aprobado para Build de CU_01**. Antes de entregar, abrir al 100 % el DCD vectorial, Figuras 3–6 y actividad, y contrastarlos con las observaciones del profesor. Evitar otra reestructuración GRASP sin una nueva objeción concreta.
