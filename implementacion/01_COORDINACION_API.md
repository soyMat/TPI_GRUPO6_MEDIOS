# Guía de trabajo para agente — INTEGRANTE 1 — Coordinación y API (responsable del repositorio)

**Rama sugerida:** `feat/01-integracion-api`. **Estado:** RFC v9.3 aprobado por el solicitante para BUILD de CU_01; validación académica y VALIDATE pendientes. **Dueño humano:** asignar en el grupo.

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

**Responsable:** quien está preparando el repositorio y coordinando el equipo. Esta es la parte que Codex debe desarrollar en la sesión inicial, pero no puede apropiarse de los módulos de las otras tres personas.

**Propiedad exclusiva orientativa:** `app/main.py`, `app/controller.py`, `app/schemas.py`, `tests/test_api.py`; además, preparación inicial del `README.md`, `.gitignore` y contratos compartidos aprobados. Si alguno existe, inspeccionarlo antes.

**Primero, coordinación (sin programar lógica ajena):**
1. Identificar el estado Git, archivos sin seguimiento y los RFC duplicados. Proponer consolidación documental segura; no borrar información distinta.
2. Proponer en `documentacion/TPI_GRUPO6_ETAPA4/Equipo/CONTRATOS_COMPARTIDOS.md` los DTO y contratos de interacción entre API, política y repositorios, sin modificar el RFC por cuenta propia. Definir las respuestas HTTP y el contrato de errores para el frontend.
3. Crear/actualizar las cuatro guías dentro de `Equipo/` y explicar estrategia PR. Pedir aprobación humana de la propuesta.
4. Preparar scaffold reproducible y test mínimo, solo después de confirmar plan, en rama propia.

**Después, implementación exclusiva de tu parte:**
- `ControlPrestamos` coordina CU_01, consulta `RepositorioCatalogos`, invoca `PoliticaPrestamo` y `RepositorioSolicitudes`, y delega avisos a `NotificadorSolicitudes`. No debe replicar reglas ni abrir SQL directamente.
- Endpoints previstos por RFC: `GET /api/equipos/tipos`, `GET /api/materias`, `POST /api/solicitudes/prevalidar`, `POST /api/solicitudes`, `GET /api/solicitudes/mias`.
- Usuario demo identificado por contexto de servidor, **no por un `usuario_id` arbitrario del formulario**. La manera de elegir usuario demo debe acordarse con frontend y quedar declarada; si exige una ruta extra, pedir actualización del RFC antes.
- Revalidar al confirmar; crear solo solicitud pendiente e historial y mostrar éxito solo tras persistencia exitosa. No implementar clases de otros integrantes, ni mockear éxitos finales para hacer pasar tests.
- Acordar con Persistencia el tratamiento de error de notificación posterior al guardado y con el equipo la idempotencia del doble clic, que el RFC marca como diseño a cerrar.
- El scaffold no debe introducir endpoints o librerías no contempladas por el RFC sin decisión registrada.

**Responsabilidades y pruebas:** B-01 y B-05 de la sección 10; contribuir a B-08. TC-01, TC-08, TC-09, TC-12, TC-13 y TC-15. **Dependencias:** el código definitivo de B-05 espera los contratos de Integrantes 2 y 3; utilizar pruebas con dobles/mocks de interfaces, sin crear implementaciones alternativas.

**Entrega de tu PR:** contratos aprobados y API/controlador con tests que corran. Registrar claramente qué está incompleto por dependencia de otros PR. No hacer merge automático.

### Prompt corto que debe leer el agente del Integrante 1

> Sos el agente encargado únicamente de Integración/API de CU_01. Leé las fuentes y este archivo. Primero auditá Git/docs, acordá contratos y armá las cuatro guías; después de la aprobación del humano, implementá solo `app/main.py`, `app/controller.py`, `app/schemas.py` y sus tests, en tareas pequeñas. No escribas las políticas, repositorios o frontend de los compañeros. Mostrá cada diff y el resultado real de las pruebas; esperá autorización entre incrementos importantes.
