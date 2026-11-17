# Integrante 2 - Política y disponibilidad

## Alcance y lecturas obligatorias

Leer `Material_catedra/AGENTS.md`, `Material_catedra/SDD_PLAYBOOK.md`, el RFC vigente, la sección CU_01 del TPI, `Fuentes/Contrato_UML_v9_3.json`, `Equipo/00_ALCANCE_PROTOTIPO.md` y `Equipo/CONTRATOS_COMPARTIDOS.md`, todos bajo `documentacion/TPI_GRUPO6_ETAPA4/`.

Implementar reglas de CU_01 y cálculo de disponibilidad por período. No crear solicitudes, endpoints, tablas ni pantallas.

## Archivos propios

`app/politica.py` y `tests/test_validacion.py`. Cualquier archivo adicional requiere acuerdo previo.

## Tareas y pruebas

- Validar campos, cantidad positiva y `desde < hasta`.
- Calcular unidades operativas libres en `[desde, hasta)` usando ocupaciones efectivas; las solicitudes pendientes no ocupan.
- Aplicar restricciones activas y estados no disponibles.
- Separar elegibilidad académica de necesidad de aval.
- No aplicar reglas exclusivas de Estudiante a Docente.
- Ofrecer `evaluar` y `revalidar` con el resultado compartido.

TC principales: TC-02, 03, 04, 05, 06, 10, 12 y 14; colaborar con TC-13.

## Git y entorno

Instalar Git/Python si faltan, comprobar `git --version` y `python --version`, y luego:

```bash
git clone https://github.com/soyMat/TPI_GRUPO6_MEDIOS.git
cd TPI_GRUPO6_MEDIOS
git switch main
git pull --ff-only origin main
git switch -c feat/02-politica-disponibilidad
python -m venv .venv
# Activar .venv y ejecutar: python -m pip install -r requirements.txt
python -m pytest -q tests/test_validacion.py
git status
git diff --check
git add app/politica.py tests/test_validacion.py
git commit -m "CU_01 B-03 B-04: validar política y disponibilidad"
git push -u origin feat/02-politica-disponibilidad
```

Abrir PR hacia `main` con resultados reales. No usar `git add .`, `push --force`, commit, push o merge sin revisión/autorización.

## Prompt para el agente

> Implementá sólo política y disponibilidad de CU_01. Leé las fuentes obligatorias listadas en esta guía y respetá CONTRATOS_COMPARTIDOS. Modificá `app/politica.py` y `tests/test_validacion.py`. No programes endpoints, ControlPrestamos, SQL, modelos, notificaciones o frontend. Hacé una regla por incremento, ejecutá pytest y mostrá el diff. Consultá antes de cambiar un contrato compartido y no hagas acciones Git remotas sin permiso.

## Terminado

Las reglas prioritarias tienen tests claros, `evaluar` y `revalidar` producen el mismo formato, no hay escrituras ni lógica de interfaz y los TC asignados tienen evidencia.
