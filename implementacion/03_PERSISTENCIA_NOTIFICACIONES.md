# Guía de trabajo para agente — INTEGRANTE 3 — Modelos, SQLite, auditoría y notificaciones

**Rama sugerida:** `feat/03-datos-notificaciones`. **Estado:** RFC v9.3 aprobado por el solicitante para BUILD de CU_01; validación académica y VALIDATE pendientes. **Dueño humano:** asignar en el grupo.

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

**Propiedad orientativa:** `app/models.py`, `app/repository.py`, `app/notifications.py`, `scripts/seed_demo.py`, `tests/test_solicitudes.py`. No editar endpoints, reglas políticas ni UI.

**Tareas:** representar `Usuario`/`Estudiante`/`Docente`, `TipoEquipamiento`, inventario, materias, restricciones, asignaciones docente–materia, `Solicitud`, `SolicitudPrestamo`, `CambioEstado` y avisos necesarios para el prototipo CU_01; no implementar todo el DCD de 62 clases. Emplear SQLite + SQLAlchemy conforme al RFC y contratos `Repositorio*`. Seed completamente ficticio y repetible, sin subir la base local a Git.

**Reglas:** alta gama es atributo de `TipoEquipamiento`, no de cada equipo; registros `SolicitudPrestamo + CambioEstado` son atómicos. `AuditorSolicitudes` registra el evento inicial. `NotificadorSolicitudes` depende de `CanalNotificacion`, y `CanalPlataforma` guarda avisos en `RepositorioNotificaciones` (sin correo real). No reservar recursos al guardar la solicitud. Las solicitudes pendientes no consumen disponibilidad.

**Acuerdos previos:** API de repositorios e integración con ControlPrestamos, rollback en error de guardar solicitud, destinatarios demo, tratamiento de falla del envío de avisos y su evidencia verificable. Si el RFC deja una decisión técnica abierta, proponer y pedir resolución antes de implementarla.

**TC prioritarios:** TC-07, TC-08, TC-09, TC-10, TC-15 y soporte de TC-03, TC-06, TC-12.

**Hecho significa:** seed idempotente, inventario único, consulta de catálogo reproducible, persistencia transaccional sin huérfanos, avisos por plataforma con destino real ficticio, pruebas automatizadas y `.db` fuera de Git.

### Prompt para el agente del Integrante 3

> Leé AGENTS, Playbook, RFC final, CU_01, contrato UML y este archivo. Tu parte es modelos/repositorios/SQLite/auditoría/avisos internos; no programes controller, políticas o frontend. Primero acordá tipos y funciones públicas con Integrante 1. Después implementá B-02, B-05-datos y B-06 en tareas pequeñas, con tests, revisión de diff y reporte de resultados reales. No asumas que la simulación equivale a seguridad productiva.
