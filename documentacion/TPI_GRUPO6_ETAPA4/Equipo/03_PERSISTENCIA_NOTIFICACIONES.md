# Integrante 3 - Modelos, SQLite, repositorios y avisos

## Alcance y lecturas obligatorias

Leer `Material_catedra/AGENTS.md`, Playbook, RFC, CU_01 del TPI, contrato UML v9.3, `Equipo/00_ALCANCE_PROTOTIPO.md` y `Equipo/CONTRATOS_COMPARTIDOS.md` dentro de `documentacion/TPI_GRUPO6_ETAPA4/`.

Implementar sólo los datos necesarios para CU_01. No materializar las 62 clases del DCD ni implementar aprobación, entrega o correo.

## Archivos propios

`app/models.py`, `app/repository.py`, `app/notifications.py`, `scripts/seed_demo.py` y `tests/test_solicitudes.py`.

## Tareas y pruebas

- Modelar usuarios demo, tipos, equipos, materias, restricciones, ocupaciones, solicitudes, historial y notificaciones mínimas.
- Implementar SQLite/SQLAlchemy y un seed repetible con datos ficticios.
- Mantener único el inventario y guardar solicitud más cambio inicial en una transacción.
- Listar catálogos, resolver alias demo y listar solicitudes del usuario.
- Guardar avisos internos directamente cuando se requiere aval; no crear colas ni reintentos.
- No descontar disponibilidad por solicitudes pendientes.

TC principales: TC-07, 08, 09, 10 y 15; soportar TC-03, 06 y 12.

## Git y entorno

Instalar Git/Python si faltan y comprobar versiones. Después:

```bash
git clone https://github.com/soyMat/TPI_GRUPO6_MEDIOS.git
cd TPI_GRUPO6_MEDIOS
git switch main
git pull --ff-only origin main
git switch -c feat/03-datos-notificaciones
python -m venv .venv
# Activar .venv y ejecutar: python -m pip install -r requirements.txt
python -m pytest -q tests/test_solicitudes.py
git status
git diff --check
git add app/models.py app/repository.py app/notifications.py scripts/seed_demo.py tests/test_solicitudes.py
git commit -m "CU_01 B-02 B-06: persistir solicitudes y avisos"
git push -u origin feat/03-datos-notificaciones
```

Abrir PR hacia `main`. Nunca versionar `.env`, `.venv`, `*.db` o datos personales. No hacer commit, push o merge sin autorización.

## Prompt para el agente

> Implementá sólo modelos mínimos, SQLite, repositorios, auditoría, seed y avisos internos de CU_01. Leé todas las fuentes indicadas y respetá CONTRATOS_COMPARTIDOS. Modificá únicamente los archivos asignados. No programes API, ControlPrestamos, reglas de política o frontend. Usá datos ficticios, mantené atómico el guardado solicitud/historial y no hagas que una solicitud pendiente reserve equipos. Ejecutá pruebas y mostrá diff; consultá cualquier cambio contractual antes de hacerlo.

## Terminado

El seed es repetible, la base local no se versiona, inventarios son únicos, solicitud e historial se guardan juntos, los avisos son simples y los tests asignados pasan.
