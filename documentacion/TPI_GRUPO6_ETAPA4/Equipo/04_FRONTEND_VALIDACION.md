# Integrante 4 - Interfaz y validación de la demo

## Alcance y lecturas obligatorias

Leer `Material_catedra/AGENTS.md`, Playbook, RFC, CU_01 del TPI, contrato UML v9.3, `Equipo/00_ALCANCE_PROTOTIPO.md` y `Equipo/CONTRATOS_COMPARTIDOS.md` dentro de `documentacion/TPI_GRUPO6_ETAPA4/`.

Construir la interfaz HTML/CSS/JavaScript nativa y preparar la demostración. El backend es la autoridad de reglas.

## Archivos propios

`app/static/`, `tests/test_interfaz.py` y evidencias/guion de demo acordados. No modificar controlador, política o persistencia.

## Tareas y pruebas

- Selector visible de usuario ficticio que envía `X-Usuario-Demo`.
- Formulario, Continuar/Cancelar, resumen, Confirmar/Volver/Cancelar y Mis solicitudes.
- Conservar datos al volver y mostrar errores concretos de API.
- Deshabilitar Confirmar y mostrar estado de carga mientras el POST está en curso.
- No implementar Idempotency-Key ni duplicar reglas de negocio en JavaScript.
- Mostrar solicitud como pendiente y distinguir aval pendiente de aprobación.
- Preparar guion de 3-5 minutos y evidencias auténticas.

TC principales: TC-01, 02, 10, 11, 13, 15 y 16; colaborar en la ejecución de TC-03..09, 12 y 14.

## Git y entorno

Instalar Git/Python si faltan y comprobar versiones. Después:

```bash
git clone https://github.com/soyMat/TPI_GRUPO6_MEDIOS.git
cd TPI_GRUPO6_MEDIOS
git switch main
git pull --ff-only origin main
git switch -c feat/04-frontend-validacion
python -m venv .venv
# Activar .venv y ejecutar: python -m pip install -r requirements.txt
python -m pytest -q tests/test_interfaz.py
git status
git diff --check
git add app/static tests/test_interfaz.py
git commit -m "CU_01 B-07 B-08: completar interfaz y demo"
git push -u origin feat/04-frontend-validacion
```

Abrir PR hacia `main` con capturas/salidas reales. No hacer commit, push o merge sin autorización.

## Prompt para el agente

> Implementá sólo la interfaz y validación demostrativa de CU_01. Leé las fuentes obligatorias y consumí exactamente CONTRATOS_COMPARTIDOS. Modificá `app/static/`, `tests/test_interfaz.py` y evidencias acordadas. No cambies backend ni reimplementes reglas. Deshabilitá Confirmar durante el envío, usá usuarios ficticios y mostrá errores/estado pendiente con claridad. Ejecutá las pruebas posibles, documentá evidencia real y pedí autorización antes de acciones Git.

## Terminado

El recorrido completo funciona contra la API integrada, el doble clic normal queda bloqueado en UI, los errores importantes se entienden, el listado muestra la solicitud y el guion puede repetirse desde un entorno limpio.
