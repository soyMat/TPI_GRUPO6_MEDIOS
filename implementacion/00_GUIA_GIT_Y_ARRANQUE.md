# GUÍA DE ARRANQUE Y GIT — Grupo 6, Etapa 4

**Versión documental:** v9.3 final. **Prototipo a implementar:** exclusivamente CU_01. **Asistente:** Codex permitido según aclaración docente referida por el grupo. **Proceso:** PLAN → BUILD → VALIDATE.

## Repositorio actual

La captura del usuario muestra `documentacion/TPI_GRUPO6_ETAPA4/` con `Entrega/`, `Fuentes/`, `Material_catedra/`, `Revision/`, `RFC/`, y tres archivos RFC aparentemente repetidos en `documentacion/`. La marca `U` indica archivos **untracked**: todavía no están registrados por Git. Verificar con `git status` antes de cambiar de rama. Esta guía no afirma que los archivos ya estén subidos a GitHub.

## Documentación canónica

Conservar la carpeta de etapa 4 y **una única copia maestra** del RFC Markdown en `documentacion/TPI_GRUPO6_ETAPA4/RFC/RFC_CU01_APROBADO_BUILD.md`, junto con sus formatos `.docx` y `.pdf`. Si los RFC de `documentacion/` tienen contenido distinto, no borrarlos sin comparación. `Entrega/` es histórico/académico, `Revision/` es evidencia y `Fuentes/` contiene fuentes UML para consultar; estos elementos no se importan como código de ejecución. Mantener los archivos de la cátedra sin alterarlos; copiar `AGENTS.md`, `SDD_PLAYBOOK.md` y `RFC_TEMPLATE.md` a la raíz si no existen, pues sus enlaces son relativos.

## Orden obligatorio de integración

1. El responsable del repositorio revisa `git status`, rama remota y archivos existentes.
2. Crea un cambio de **documentación + contratos compartidos + scaffold acordado**, preservando archivos `U`. Solicita revisión; solo entonces commit/push/PR.
3. Se integra el PR de preparación a la rama principal.
4. Los cuatro integrantes crean sus **ramas separadas desde la rama principal actualizada**.
5. Cada uno implementa únicamente sus archivos, con tests. Cada PR se revisa antes del merge.
6. Cuando se integran los cuatro PR, el equipo ejecuta `python -m pytest -q`, recorrido real CU_01 y TC-01..TC-16; documenta resultados, errores y correcciones.

## Comandos útiles (terminal de VS Code)

```bash
# Antes de tocar archivos:
git status
git remote -v
git branch --show-current
git branch -a

# Solo compañeros sin clon local:
git clone https://github.com/soyMat/TPI_GRUPO6_MEDIOS.git
cd TPI_GRUPO6_MEDIOS

# Cuando la documentación preparatoria esté integrada:
git switch main
git pull --ff-only origin main
git switch -c feat/02-politica-disponibilidad  # ejemplo, usar rama propia

# Por incremento (después de probar realmente):
git diff --check
git diff
git add app/politica.py tests/test_validacion.py
git commit -m "CU_01 TC-03: validar disponibilidad"
git push -u origin feat/02-politica-disponibilidad
```

Para Windows PowerShell: `py -m venv .venv`, `.\.venv\Scripts\Activate.ps1`; Linux/macOS: `python3 -m venv .venv`, `source .venv/bin/activate`. Las dependencias reales se instalan **solo cuando `requirements.txt` fue definido y probado**. En ambos sistemas: `python -m pip install -r requirements.txt` y `python -m pytest -q` cuando existan esos archivos.

## Asistencia de IA

El agente deberá leer su archivo `01_...` a `04_...`, `AGENTS.md`, `SDD_PLAYBOOK.md`, el RFC vigente, el CU_01 y las fuentes UML. No debe implementar el proyecto entero, cambiar RFC sin aprobación, declarar que pasó tests no ejecutados, ni hacer commits, pushes o merges sin permiso del humano.
