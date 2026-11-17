# Integrante 1 - Coordinación, API y ControlPrestamos

## Alcance y lecturas obligatorias

Implementar únicamente la coordinación HTTP de CU_01. Leer:

- `documentacion/TPI_GRUPO6_ETAPA4/Material_catedra/AGENTS.md`
- `documentacion/TPI_GRUPO6_ETAPA4/Material_catedra/SDD_PLAYBOOK.md`
- `documentacion/TPI_GRUPO6_ETAPA4/RFC/RFC_CU01_APROBADO_BUILD.md`
- `documentacion/TPI_GRUPO6_ETAPA4/Entrega/TPI_GRUPO6_ETAPA4.pdf`, sección CU_01
- `documentacion/TPI_GRUPO6_ETAPA4/Fuentes/Contrato_UML_v9_3.json`
- `documentacion/TPI_GRUPO6_ETAPA4/Equipo/00_ALCANCE_PROTOTIPO.md`
- `documentacion/TPI_GRUPO6_ETAPA4/Equipo/CONTRATOS_COMPARTIDOS.md`

## Archivos propios

`app/main.py`, `app/controller.py`, `app/schemas.py`, `tests/test_api.py` y coordinación de contratos. No implementar `politica.py`, modelos, repositorios, notificaciones ni frontend.

## Tareas y pruebas

1. Definir schemas mínimos de entrada, validación, resumen y error.
2. Exponer los cinco endpoints exactos del RFC.
3. Resolver `X-Usuario-Demo` usando un colaborador inyectado y validar roles permitidos.
4. Implementar `ControlPrestamos.prevalidar`, `confirmar` y `listarDe` delegando reglas y persistencia.
5. Revalidar antes del guardado; auditar y guardar solicitud/historial; avisar sólo si requiere aval.
6. Probar con dobles de política y repositorios, sin crear implementaciones productivas de compañeros.

TC principales: TC-01, TC-08, TC-09, TC-12, TC-13 y TC-15. Registrar dependencias que impidan una prueba integrada.

## Git y entorno

En Windows instalar Git desde `https://git-scm.com/download/win` o con `winget install --id Git.Git -e`; instalar Python desde `https://python.org/downloads/`. Reiniciar la terminal y comprobar `git --version` y `python --version`.

```bash
git clone https://github.com/soyMat/TPI_GRUPO6_MEDIOS.git
cd TPI_GRUPO6_MEDIOS
git switch main
git pull --ff-only origin main
git switch -c feat/01-integracion-api
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q tests/test_api.py
git status
git diff --check
git diff
git add app/main.py app/controller.py app/schemas.py tests/test_api.py
git commit -m "CU_01 B-05: coordinar API de solicitudes"
git push -u origin feat/01-integracion-api
```

Abrir un Pull Request hacia `main`, describir TC ejecutados y pedir revisión. El agente no debe hacer commit, push o merge sin autorización humana.

## Prompt para el agente

> Trabajá sólo en la API y ControlPrestamos de CU_01. Leé AGENTS, Playbook, RFC v9.3, CU_01, contrato UML, alcance del prototipo y CONTRATOS_COMPARTIDOS en las rutas indicadas por esta guía. Modificá únicamente `app/main.py`, `app/controller.py`, `app/schemas.py` y `tests/test_api.py`. Usá dobles para política, repositorios, auditor y notificador. Implementá una tarea pequeña por vez, ejecutá las pruebas reales y mostrá diff y estado. No programes reglas, SQLite, notificaciones ni frontend. No hagas commit, push o merge sin permiso.

## Terminado

Los cinco endpoints respetan el contrato, las dependencias están inyectadas, no hay SQL ni reglas duplicadas en el controlador, las pruebas propias pasan y todo pendiente de otros PR está documentado.
