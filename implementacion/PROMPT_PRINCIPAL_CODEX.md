# PROMPT PRINCIPAL PARA CODEX EN VS CODE — ARRANQUE CU_01 DEL TPI GRUPO 6

Actuá como desarrollador principal y coordinador técnico de nuestro TPI de Ingeniería de Software I. Estás dentro de un workspace local que debe corresponder al repositorio `https://github.com/soyMat/TPI_GRUPO6_MEDIOS`.

## Objetivo y autoridad

Quiero comenzar BUILD del **único caso de uso CU_01 — Solicitar préstamo de equipamiento**, distribuyendo el trabajo entre cuatro integrantes que usarán sus propios agentes. **Tu responsabilidad de programación es solo la del INTEGRANTE 1 (mi parte): coordinación, API, DTO y `ControlPrestamos`.** No desarrolles también los otros tres módulos.

Usá exclusivamente como autoridad funcional y de arquitectura:
- `documentacion/TPI_GRUPO6_ETAPA4/RFC/RFC_CU01_APROBADO_BUILD.md` (RFC final v9.3 aprobado por el solicitante para Build), o la ruta canónica equivalente que encuentres en disco.
- `documentacion/TPI_GRUPO6_ETAPA4/Entrega/TPI_GRUPO6_ETAPA4.pdf` (CU_01 textual, RF/RNF, especificaciones).
- `documentacion/TPI_GRUPO6_ETAPA4/Fuentes/Contrato_UML_v9_3.json`, `Matriz_Contratos_UML_v9_3.csv`, `Relaciones_DCD_v9_3.csv` y diagramas relevantes.
- `AGENTS.md`, `SDD_PLAYBOOK.md`, `RFC_TEMPLATE.md`, que provienen de `documentacion/TPI_GRUPO6_ETAPA4/Material_catedra/`.

No modifiques arquitectura GRASP, diagramas, entrevistas, RF/RNF, Specs, CU, portada ni archivos fuente de teoría. El DCD completo tiene más clases que el prototipo: implementá solo las clases/operaciones necesarias para CU_01.

### Decisiones ya tomadas (NO reabrir sin contradicción real)
- Codex está permitido por indicación del profesor en clase; Gemini no es obligatorio.
- Alcance de BUILD: solo CU_01, no CU_02/03/04 ni aprobación física, entrega, devolución, reserva de aulas, correo real o login productivo.
- Usuarios ficticios precargados. La sesión demo identifica al usuario desde el servidor; no confiar en `usuario_id` libre enviado desde el formulario.
- Duración estándar sugerida de 48 horas, **no máximo universal**.
- Las solicitudes se crean `Pendiente/Solicitada`, con auditoría, sin consumir ni asignar equipamiento físico.
- Equipamiento de alta gama: `TipoEquipamiento.altaGama`; el estudiante no elegible se bloquea; el elegible que necesita aval queda pendiente, con aviso interno. El Docente debe tener flujo propio sin aplicar `getAnioCursada()` implícitamente.
- Se consideran disponibilidades reales/ocupaciones aprobadas, con revalidación al confirmar. Las validaciones independientes y el fork/join se respetan según el RFC.
- Gate 1 de decisiones para Build fue aprobado por el solicitante; la **validación académica del profesor y la fase Validate están pendientes**.

## FASE 0 — INSPECCIÓN SEGURA (obligatoria; ninguna eliminación/commit/push todavía)

1. Detectá cuál es la raíz real de Git (`git rev-parse --show-toplevel`), la rama actual y remotos; corré `git status --short`, `git branch -a`, `git remote -v`. No hagas `git init`, `git clone` dentro del repositorio, `git clean`, `reset --hard` ni `push --force`.
2. En mi captura veo la carpeta `documentacion/TPI_GRUPO6_ETAPA4` y marcas `U`: esos archivos están sin seguimiento. No los borres y no cambies de rama hasta entender el estado. Verificá si ya hay código o commits de compañeros y respetalos.
3. Enumerá los archivos de `documentacion/TPI_GRUPO6_ETAPA4/{Entrega,Fuentes,Material_catedra,Revision,RFC}`. Localizá las **tres copias extras del RFC** fuera de `TPI_GRUPO6_ETAPA4` que se ven en la captura. Compará sus contenidos/sha256 y decime qué es idéntico y qué no. Proponé quitar solo duplicados **confirmados**, no fuentes académicas ni distintas revisiones que contengan información.
4. Inspeccioná el RFC, `AGENTS.md` y SDD_PLAYBOOK completos antes de hacer nada más. El RFC vigente ya permite iniciar Build, no lo marques EN REVISIÓN. Si faltan archivos de la cátedra en la raíz, prepará copias **idénticas** desde `Material_catedra/`; no modifiques sus reglas.
5. Verificá las versiones de Python/VS Code/Git locales y proponé dependencias compatibles con la máquina. No supongas que las versiones candidatas del RFC ya se instalaron o funcionan.

## FASE 1 — ORGANIZACIÓN DEL EQUIPO Y GIT

Prepará `README.md`, `.gitignore`, estructura aprobada del RFC y la siguiente documentación en `documentacion/TPI_GRUPO6_ETAPA4/Equipo/`:
- `00_GUIA_GIT_Y_ARRANQUE.md`: explicación para principiantes de instalar Git, identidad, clonar repo **solo si no se tiene**, abrir VS Code, venv Windows/Linux, instalar deps una vez aprobadas, actualizar main, crear rama, revisar diff, ejecutar tests, commit, push, PR y manejo de conflictos sin perder trabajo. Incluir comandos concretos, no solo teoría.
- `01_COORDINACION_API.md`: mi parte, con instrucciones para agente y archivos exclusivos.
- `02_POLITICA_DISPONIBILIDAD.md`: política y disponibilidad, para compañero 2.
- `03_PERSISTENCIA_NOTIFICACIONES.md`: SQLAlchemy/SQLite, modelos, repositorios, auditoría, seed y avisos internos, para compañero 3.
- `04_FRONTEND_VALIDACION.md`: HTML/CSS/JS, flujo UI, pruebas y demo, para compañero 4.
- `CONTRATOS_COMPARTIDOS.md`: tabla de tipos/DTO, operaciones públicas, respuestas de error/HTTP, firmas de interfaz entre política/control/repositorios y responsabilidades/archivos de cada integrante. Este archivo es una **propuesta que requiere revisión humana del equipo**, no permiso para cambiar RFC.

En cada guía de los cuatro integrantes incluir obligatoriamente:
- fuente de verdad y rutas **reales** del repo, alcance CU_01 y reglas RFC ya aprobadas;
- mini tutorial Git concreto para novatos y nombre de rama (`feat/01-integracion-api`, `feat/02-politica-disponibilidad`, `feat/03-datos-notificaciones`, `feat/04-frontend-validacion`), aclarando que si main no es rama predeterminada debe adaptarse;
- archivos bajo su propiedad, tareas B-XX/TC-XX, criterios de aceptación y dependencias de otros compañeros;
- un **prompt autónomo para pegar a su propio agente** que le obligue a leer `AGENTS.md`, Playbook, RFC, CU_01 y los contratos; implementar solo su parte, con tests reales y PR;
- prohibición de editar archivos de otros, escribir toda la app, subir `.env`/`.venv`/`*.db`, inventar endpoints, y hacer push/merge sin permiso.

Reparto que debés respetar:
1) YO / INTEGRANTE 1: `app/main.py`, `app/controller.py`, `app/schemas.py`, `tests/test_api.py`, integración y contratos compartidos. Endpoints exactos del RFC: GET `/api/equipos/tipos`, GET `/api/materias`, POST `/api/solicitudes/prevalidar`, POST `/api/solicitudes`, GET `/api/solicitudes/mias`.
2) INTEGRANTE 2: `app/politica.py`, reglas, disponibilidad por período, tests de validaciones (TC-02,03,04,05,06,10,12,14).
3) INTEGRANTE 3: `app/models.py`, `app/repository.py`, `app/notifications.py`, `scripts/seed_demo.py`, SQLite, historial y avisos (TC-07,08,09,10,15).
4) INTEGRANTE 4: `app/static/`, `tests/test_interfaz.py`, demostración y evidencias TC-01..16, sin reimplementar lógica de negocio en frontend.

Los cuatro agentes deben trabajar con las **mismas interfaces y el mismo RFC**. Primero integrar la documentación/contratos a la rama base; **recién después** cada compañero crea su rama desde una base sincronizada. Si las carpetas reales ya tienen otra organización válida, no dupliques ni las migres innecesariamente.

## FASE 2 — IMPLEMENTÁ MI PARTE, NO LAS DE MIS COMPAÑEROS

Después de que yo apruebe la Fase 1, creá o usá una rama `feat/01-integracion-api` derivada de main actualizado (adaptar si la rama principal es otra y cuidando cambios untracked).

Seguí PLAN → BUILD → VALIDATE en tareas pequeñas:
- B-01: entorno reproducible y scaffold mínimo acorde al RFC, `.gitignore`, `requirements.txt` y pruebas básicas. No introducir un endpoint de negocio no aprobado para facilitar la demo.
- Contratos: fijar con ejemplos de request/response los cinco endpoints, DTO de validación y códigos de error, así como interfaces esperadas para política/repositorios y selección segura de usuario demo. **Si una decisión técnica está pendiente** (por ejemplo idempotencia en doble clic o falla de avisos), proponerla y pedir mi aprobación antes de programarla.
- B-05 de tu propiedad: desarrollar `ControlPrestamos` y rutas API, delegando a `PoliticaPrestamo`, `RepositorioCatalogos`, `RepositorioSolicitudes`, `AuditorSolicitudes` y `NotificadorSolicitudes` por interfaces. No implementar las reglas, repositorios ni UI de otros integrantes como atajo. Para pruebas unitarias de la API se permiten mocks de esas interfaces; no declarar integración real hasta disponer de PR de compañeros.
- Siempre revalidar al confirmar; no crear préstamo efectivo, no reservar equipos, no mostrar HTTP 201 falso. Cubrir TC-01,08,09,12,13,15 donde tus dependencias y entorno lo permitan; reportar los que dependan de la integración.
- No agregar rutas o archivos fuera de estructura RFC sin aprobación. No instalar paquetes al azar; justificar versiones y verificarlas con comandos reales.

**Después de cada incremento funcional:** correr los tests que existan, mostrar `git diff --check`, diff, `git status`, lista de archivos, TC y sus resultados efectivos, y sugerir un mensaje de commit trazable. **No hagas commit, push, PR ni merge sin mi autorización expresa**. Si hay decisiones que bloquean un módulo, avanzá en tests/contratos que sí sean independientes; nunca rellenes silenciosamente con fakes productivos.

## FORMATO DE RESPUESTA Y PUNTOS DE CONTROL

Tu primera respuesta debe contener: (a) diagnóstico real de repositorio Git/documentación/duplicados; (b) estructura concreta propuesta sin borrado; (c) cuatro roles y archivos; (d) contratos/ambigüedades técnicas a acordar; (e) lista de pasos y primera acción segura. Si todavía no verificaste un dato, marcá "no verificado".

Podés inspeccionar y preparar borradores de documentación, pero **detenete y esperá mi aprobación** antes de la limpieza destructiva, modificaciones mayores, instalación de dependencias, implementación B-01/B-05, commit/push/PR. En fases de código, pedí aprobación entre tareas verificables. El objetivo no es entregar "todo resuelto" de golpe: es que mi parte corra, tenga pruebas y pueda integrarse sin conflictos con las otras tres partes.
