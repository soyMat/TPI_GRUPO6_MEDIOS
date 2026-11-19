# Guía de trabajo para agente — INTEGRANTE 2 — Política de préstamo y disponibilidad

**Rama sugerida:** `feat/02-politica-disponibilidad`. **Estado:** RFC v9.3 aprobado por el solicitante para BUILD de CU_01; validación académica y VALIDATE pendientes. **Dueño humano:** asignar en el grupo.

## Fuente de verdad y límites

- Repositorio: `https://github.com/soyMat/TPI_GRUPO6_MEDIOS`.
- El material está en `documentacion/TPI_GRUPO6_ETAPA4/` (respetar mayúsculas reales).
- Antes de editar, leer **desde la raíz del repositorio** `AGENTS.md`, `SDD_PLAYBOOK.md`, `RFC_TEMPLATE.md`. Si faltan, comprobar las copias originales en `documentacion/TPI_GRUPO6_ETAPA4/Material_catedra/` y solicitar autorización para copiarlas sin alterar su contenido.
- RFC vigente: `documentacion/TPI_GRUPO6_ETAPA4/RFC/RFC_CU01_APROBADO_BUILD.md` (si la ruta real es distinta, encontrarla y establecerla como canónica).
- Leer la especificación textual CU_01 y RF/RNF de `documentacion/TPI_GRUPO6_ETAPA4/Entrega/TPI_GRUPO6_ETAPA4.pdf`, junto con `Fuentes/Contrato_UML_v9_3.json` y las matrices relevantes.
- **PLAN de CU_01 aprobado para BUILD por el solicitante**; no implica validación académica del profesor ni pruebas ejecutadas. Codex está permitido según aclaración del docente en clase.
- Implementar solo `CU_01 — Solicitar préstamo de equipamiento`. **No** implementar CU_02, CU_03, CU_04, aprobación real, entrega, devolución, reservas de aulas, login real o correos reales.
- Usuario de demo ficticio; solicitud queda `Pendiente/Solicitada`, **sin reservar unidades físicas**. Alta gama: elegibilidad de datos demo; aval posterior sin aprobarlo. Notificaciones solo internas. Duración estándar sugerida 48 horas; no convertir en máximo universal.
- No inventar nombres de operaciones que contradigan el DCD. Si el RFC y DCD se contradicen, registrar y consultar antes de introducir el cambio.
- Trabajar en incrementos pequeños, cumplir PLAN → BUILD → VALIDATE y no afirmar pruebas que no corriste.

## Mini tutorial de Git para integrantes (el agente debe respetarlo)

### Primer uso del repositorio (solo si no lo tenés clonado)

```bash
git --version
git config --global user.name "TU NOMBRE"
git config --global user.email "TU CORREO DE GIT"
git clone https://github.com/soyMat/TPI_GRUPO6_MEDIOS.git
cd TPI_GRUPO6_MEDIOS
git remote -v
git branch -a
git status
```

Si el repositorio **ya está abierto**, no volver a clonarlo y **no usar `git init`**. Antes de crear la rama, verificar cuál es la rama principal (`main` en los ejemplos; reemplazar por la real si es otra). Esperar que el PR de preparación y documentación esté integrado antes de iniciar trabajo en paralelo.

```bash
git switch main
git pull --ff-only origin main
git switch -c RAMA_ASIGNADA
```

### Cada tarea

```bash
git status
git diff --check
git diff
# Ejecutar las pruebas reales de tu módulo antes de commitear.
git add RUTAS_ESPECIFICAS_MODIFICADAS
git commit -m "CU_01 RF-03 TC-XX: descripción breve"
git push -u origin RAMA_ASIGNADA
```

Abrir Pull Request (PR) hacia `main`, con evidencia de tests y revisión por otra persona. No hacer push directo a main, no usar `git push --force`, `git reset --hard` ni `git clean -fd`. Evitar `git add .` si no se inspeccionaron los archivos; no versionar `.venv/`, `.env`, `*.db`, `*.sqlite3`, contraseñas ni datos reales. El agente **propone** los commits/PR y pide autorización antes de acciones remotas.

## Informe obligatorio al cerrar cada incremento

Describir archivos cambiados, CU/RF/RNF, TC cubiertos, comandos ejecutados y sus resultados verdaderos, posibles cambios al RFC, y el diff listo para revisión. Parar si falta un contrato compartido o si se necesita editar archivos de otro integrante.

## Trabajo asignado y límites

**Propiedad orientativa:** `app/politica.py`, `tests/test_validacion.py` y pruebas focalizadas de disponibilidad. Si `CalendarioRecursos` requiere otro módulo, proponerlo al Integrante 1 y aprobar el ajuste antes de crear una ruta fuera del RFC.

**Tareas:** implementar reglas puras/de servicio de `PoliticaPrestamo` y `CalendarioRecursos` según RFC + DCD: datos requeridos, cantidad > 0, fechas coherentes, ocupaciones efectivas por tipo y período, unidades operativas, restricciones vigentes, validaciones de alta gama y aval pendiente, revalidación al confirmar. Para estudiante, leer condición académica mediante sus accesores; para docente, no llamar a `getAnioCursada()` ni aplicar implícitamente reglas de Estudiante. No crear solicitudes ni persistirlas desde política. No registrar aprobaciones ni reservas reales.

**Dependencias:** obtener de Integrante 3 el contrato de lectura del calendario/inventario/ocupaciones; publicar a Integrante 1 las firmas, resultado de validación y errores. Respetar la convención de intervalo `[desde, hasta)` que propone el RFC. Para el fork/join, definir tres resultados de lectura independientes; si se implementa concurrencia real, coordinar manejo de sesiones SQLite sin compartir una sesión entre hilos.

**TC prioritarios:** TC-02, TC-03, TC-04, TC-05, TC-06, TC-10, TC-12, TC-14; y TC-13 para diferencia Estudiante/Docente.

**Hecho significa:** tests de elegible, no elegible, común, disponibilidad agotada, mantenimiento, restricciones, fecha inválida y cambios antes de confirmar; ninguna escritura de persistencia desde la política.

### Prompt para el agente del Integrante 2

> Leé AGENTS, Playbook, RFC final, CU_01, DCD y este documento. Tu propiedad es `PoliticaPrestamo`/disponibilidad, no `ControlPrestamos`, repositorios ni UI. Empezá por el contrato de validación con casos TC; tras validación humana, implementá una regla por vez, con pytest y diff. Consultá antes de cambiar una interfaz de otro responsable y no avances a la siguiente tarea sin mostrar evidencia.
