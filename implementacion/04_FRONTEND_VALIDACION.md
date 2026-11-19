# Guía de trabajo para agente — INTEGRANTE 4 — Interfaz web, pruebas y demo

**Rama sugerida:** `feat/04-frontend-validacion`. **Estado:** RFC v9.3 aprobado por el solicitante para BUILD de CU_01; validación académica y VALIDATE pendientes. **Dueño humano:** asignar en el grupo.

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

**Propiedad orientativa:** `app/static/` (HTML, CSS, JavaScript nativos), `tests/test_interfaz.py` y material de evidencias/demo bajo `documentacion/TPI_GRUPO6_ETAPA4/Equipo/`. No modificar API, política o base de datos.

**Tareas:** formularios de tipo, cantidad, fechas y materia/proyecto; acciones Continuar y Cancelar; resumen con Confirmar, Volver, Cancelar; mensajes diferenciados de inválido, indisponible, restricción y alta gama; confirmación solo cuando la API retorna HTTP 201 real; listado Mis Solicitudes para el usuario demo. Si requiere aval posterior, explicar que está pendiente, nunca aprobado. No simular una reserva de unidades.

**Contrato:** consumir solo las cinco rutas del RFC y la forma de selección de usuario demo acordada con Integrante 1. Si falta un endpoint para la demo, no inventarlo por tu cuenta: proponer modificación del RFC/contrato y esperar aprobación. Evitar construir lógica de validación de negocio duplicada en navegador: validaciones cosméticas ayudan, backend decide.

**Pruebas y demo:** TC-01, TC-02, TC-10, TC-11, TC-13, TC-15 y TC-16; colaborar en TC-03..09, TC-12 y TC-14. Preparar guion de 3–5 minutos: caso válido, error de formulario, disponibilidad agotada, alta gama elegible con aviso pendiente, docente demo. Guardar evidencia real y anonimizada, no capturas inventadas.

**Hecho significa:** navegación completa CU_01, estados de carga/errores claros, vuelta conserva datos, cancelar no crea solicitud, UI usa API real y pasos reproducibles para demo.

### Prompt para el agente del Integrante 4

> Leé AGENTS, Playbook, RFC final, CU_01 y este archivo. Sos responsable solo de interfaz y pruebas de aceptación; trabajá desde la API compartida y sin cambiar el backend. Primero acordá DTO/errores con Integrante 1. Luego implementá una pantalla/flujo por incremento, probá realmente en navegador/pytest cuando corresponda, mostrá el diff y pedí revisión antes de seguir. Documentá TC y evidencias auténticas.
