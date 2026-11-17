# Cierre editorial y control de presentación — TPI Grupo 6 · Etapa 4

**Modelo de referencia:** v9.3. **Alcance de este cierre:** corrección documental y de exportación, sin rediseño de arquitectura ni cambios en entrevistas, RF/RNF, Specs o casos de uso consolidados.

## Correcciones realizadas

1. **Referencias editoriales:** se reemplazaron los textos obsoletos «DCD actualizado a v9.2» y «Nota de sincronización UML — v9.2» por **v9.3** tanto en Word como en RFC Markdown.
2. **Escenario Docente:** la Figura 3 representa el escenario **Estudiante**. La aclaración figura directamente al pie de la imagen: CU_01 también admite **Docente**, pero su recorrido se verifica por separado mediante **TC-13**. No corresponde aplicarle `getAnioCursada()` ni las reglas de elegibilidad académica exclusivas del Estudiante. Esta distinción se hizo explícita también en el RFC.
3. **CU_01 Comunicación:** la Figura 4 se encontraba parcialmente fuera del margen derecho de su página en el PDF. Se redujo **solo el tamaño de la imagen** dentro del Word para que todos los objetos y sus enlaces entren en el formato de página, sin modificar el diagrama subyacente.
4. **Diagramas vectoriales en el PDF principal:** para evitar pixelación al ampliar, las páginas **35, 36, 37, 38, 39, 45 y 46** del PDF entregable incorporan las fuentes SVG vectoriales originales sobre las imágenes de Word (misma posición, tamaño y contenido). El Word conserva las imágenes PNG de alta resolución originales; las fuentes SVG acompañan esta entrega. Se adjunta además el **DCD vectorial extendido**, con su leyenda de 90 relaciones.

## Verificaciones

- **TPI Word/PDF:** 47 páginas, carátula original conservada.
- **RFC Word/PDF:** 19 páginas y estado «APROBADO PARA BUILD DEL PROTOTIPO CU_01» por el solicitante, sin atribuir aprobación al profesor.
- **Modelo:** 62 clases, 90 relaciones, 84 eventos de mensajes en matriz; **71/71** llamadas internas verificadas, sin inconsistencias mecánicas de método/parámetros/visibilidad.
- **Visibilidad:** atributo, parámetro, variable local o creación (además de auto-mensaje en la matriz); no se considera retorno como quinta forma independiente.
- **Diagramas:** ningún mensaje ni relación UML fue rediseñado en este cierre. Las figuras ya corregidas en v9.3 se conservaron.
- **Presentación:** la figura de CU_01 Comunicación ahora está completamente dentro de los límites de la página; las siete figuras técnicas insertadas en el PDF son seleccionables/ampliables por su contenido vectorial.
- **Referencias antiguas:** no quedan menciones visibles a v9.2 en el TPI ni el RFC finales.

## Límites explícitos

- **No** se implementó código ni se ejecutaron los casos TC-01...TC-16. TC-13 describe una prueba pendiente del recorrido Docente.
- El **RFC está aprobado para iniciar Build del CU_01 por el solicitante**; no hay aprobación académica del profesor ni cierre de Validate.
- La revisión mecánica de firmas no equivale a una validación conceptual docente de UML.
- El modelo completo conserva servicios fuera de CU_01; el prototipo implementará exclusivamente CU_01 conforme al RFC.

**Siguiente actividad:** cargar esta entrega en `docs/etapa4` del repositorio, acordar con el grupo los contratos y realizar Build con Codex conforme a `AGENTS.md` y `SDD_PLAYBOOK.md`.
