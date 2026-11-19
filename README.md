# Prototipo CU_01 - Prestamo de equipamiento

Trabajo Practico Integrador de **Ingenieria de Software I**, Grupo 6.

## Que demuestra

La aplicacion permite seleccionar un usuario ficticio, consultar equipos y materias, validar una solicitud de prestamo, confirmarla como `PENDIENTE_SOLICITADA` y verla en **Mis solicitudes**. Tambien demuestra restricciones, disponibilidad, equipamiento de alta gama, aval docente posterior e historial inicial.

Es una demo local. No incluye autenticacion real, aprobacion, entrega, devolucion, prorrogas ni correo electronico.

## Tecnologias

Python, FastAPI, Uvicorn, SQLite, SQLAlchemy, HTML, CSS, JavaScript y pytest. Las versiones estan fijadas en `requirements.txt`.

## Instalacion en Windows

Requiere Python 3.13 o posterior, Git y un navegador actualizado.

```powershell
git clone https://github.com/soyMat/TPI_GRUPO6_MEDIOS.git
cd TPI_GRUPO6_MEDIOS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Preparar datos e iniciar

Desde la raiz del repositorio:

```powershell
python -m scripts.seed_demo
python -m uvicorn app.main:app --reload
```

Abrir `http://127.0.0.1:8000/`. El seed es idempotente y utiliza solamente datos ficticios. La base local `tpi_cu01.db` no se versiona.

## Pruebas

```powershell
python -m pytest -q
```

Las pruebas incluyen reglas unitarias, API con dobles e integracion real contra SQLite.

## Trabajo por integrante

| Integrante | Responsabilidad y evidencia verificada |
| --- | --- |
| Mateo Mazuela | API, schemas, `ControlPrestamos` y coordinacion. Implementacion base en `81268d2` y ajustes de integracion en la rama propia. |
| Milagros Martinez | Politica y disponibilidad en `app/politica.py`, integradas desde el PR #2. |
| Agustin Arias | Modelos, SQLite, repositorios y notificaciones iniciales, integrados mediante los PR #3 y #5. |
| Luca Mechulan | Interfaz y pruebas de demostracion del PR #1; su PR #4 aporto la base del seed, composicion SQLite y pruebas de persistencia recuperadas durante la integracion final. |

La atribucion se basa en los autores de commits y referencias de Pull Requests disponibles en Git.

## Documentacion

La fuente de verdad es el RFC aprobado en `documentacion/TPI_GRUPO6_ETAPA4/RFC/`. Las responsabilidades e interfaces estan en `documentacion/TPI_GRUPO6_ETAPA4/Equipo/`.
