"""Carga idempotente de datos ficticios para la demostracion de CU_01."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import (
    AsignacionDocenteMateria,
    Base,
    Docente,
    Equipamiento,
    Estudiante,
    MateriaProyecto,
    PersonalLaboratorio,
    Restriccion,
    TipoEquipamiento,
    Usuario,
)

DATABASE_URL_DEFECTO = "sqlite:///./tpi_cu01.db"

UUID_EST_COMUN = UUID("11111111-1111-1111-1111-111111111101")
UUID_EST_ELEGIBLE = UUID("11111111-1111-1111-1111-111111111102")
UUID_EST_RESTRINGIDO = UUID("11111111-1111-1111-1111-111111111103")
UUID_DOCENTE_NO_ASIGNADO = UUID("11111111-1111-1111-1111-111111111100")
UUID_DOCENTE = UUID("11111111-1111-1111-1111-111111111104")
UUID_PERSONAL = UUID("11111111-1111-1111-1111-111111111105")

UUID_MAT_PROYECTO2 = UUID("22222222-2222-2222-2222-222222222201")
UUID_MAT_TALLER = UUID("22222222-2222-2222-2222-222222222202")
UUID_MAT_TESIS = UUID("22222222-2222-2222-2222-222222222203")
UUID_ASIGNACION_TESIS = UUID("33333333-3333-3333-3333-333333333301")


def poblar_datos_demo(session: Session) -> None:
    """Inserta usuarios, catalogos, inventario y reglas demo si no existen."""
    usuarios_demo: list[Usuario] = [
        Estudiante(
            id=UUID_EST_COMUN,
            nombre_completo="Camila Rojas (Estudiante comun)",
            dni="DEMO-EST-01",
            correo="estudiante.comun@example.test",
            alias="estudiante-comun",
            carrera="Medios Audiovisuales",
            anio_cursada=2,
            tesista_avanzado=False,
        ),
        Estudiante(
            id=UUID_EST_ELEGIBLE,
            nombre_completo="Mateo Pereyra (Estudiante elegible)",
            dni="DEMO-EST-02",
            correo="estudiante.elegible@example.test",
            alias="estudiante-elegible",
            carrera="Medios Audiovisuales",
            anio_cursada=4,
            tesista_avanzado=True,
        ),
        Estudiante(
            id=UUID_EST_RESTRINGIDO,
            nombre_completo="Lucas Fernandez (Estudiante restringido)",
            dni="DEMO-EST-03",
            correo="estudiante.restringido@example.test",
            alias="estudiante-restringido",
            carrera="Medios Audiovisuales",
            anio_cursada=3,
            tesista_avanzado=False,
        ),
        # Se inserta antes que la docente asignada para demostrar que el aviso no
        # depende del primer docente encontrado en la base.
        Docente(
            id=UUID_DOCENTE_NO_ASIGNADO,
            nombre_completo="Prof. No Asignado (Docente)",
            dni="DEMO-DOC-00",
            correo="docente.no.asignado@example.test",
            alias="docente-no-asignado",
            es_tutor=True,
            especialidad="Sonido",
        ),
        Docente(
            id=UUID_DOCENTE,
            nombre_completo="Prof. Valeria Mendez (Docente)",
            dni="DEMO-DOC-01",
            correo="docente.demo@example.test",
            alias="docente-demo",
            es_tutor=True,
            especialidad="Produccion audiovisual",
        ),
        PersonalLaboratorio(
            id=UUID_PERSONAL,
            nombre_completo="Martin Sosa (Personal de laboratorio)",
            dni="DEMO-LAB-01",
            correo="personal.demo@example.test",
            alias="personal-demo",
            legajo="LAB-DEMO-01",
        ),
    ]
    for usuario in usuarios_demo:
        if session.scalar(select(Usuario).where(Usuario.alias == usuario.alias)) is None:
            session.add(usuario)
    session.flush()

    tipos = [
        TipoEquipamiento(codigo="CAMARA", nombre="Camara HD", alta_gama=False),
        TipoEquipamiento(
            codigo="MICROFONO",
            nombre="Kit Microfono Direccional",
            alta_gama=False,
        ),
        TipoEquipamiento(codigo="CINE_PRO", nombre="Camara Cine 4K", alta_gama=True),
    ]
    for tipo in tipos:
        if session.get(TipoEquipamiento, tipo.codigo) is None:
            session.add(tipo)
    session.flush()

    unidades = [
        ("INV-CAM-01", "CAMARA", "OPERATIVO"),
        ("INV-CAM-02", "CAMARA", "OPERATIVO"),
        ("INV-CAM-03", "CAMARA", "MANTENIMIENTO"),
        ("INV-MIC-01", "MICROFONO", "OPERATIVO"),
        ("INV-MIC-02", "MICROFONO", "OPERATIVO"),
        ("INV-CINE-01", "CINE_PRO", "OPERATIVO"),
        ("INV-CINE-02", "CINE_PRO", "OPERATIVO"),
    ]
    for inventario, tipo_codigo, estado in unidades:
        existe = session.scalar(
            select(Equipamiento).where(
                Equipamiento.numero_inventario == inventario
            )
        )
        if existe is None:
            session.add(
                Equipamiento(
                    numero_inventario=inventario,
                    tipo_codigo=tipo_codigo,
                    estado=estado,
                )
            )

    materias = [
        MateriaProyecto(
            id=UUID_MAT_PROYECTO2,
            nombre="Proyecto 2",
            prioridad=2,
        ),
        MateriaProyecto(
            id=UUID_MAT_TALLER,
            nombre="Taller de Produccion Audiovisual",
            prioridad=1,
        ),
        MateriaProyecto(
            id=UUID_MAT_TESIS,
            nombre="Proyecto 4 - Tesis Audiovisual",
            prioridad=3,
        ),
    ]
    for materia in materias:
        if session.get(MateriaProyecto, materia.id) is None:
            session.add(materia)
    session.flush()

    if session.get(AsignacionDocenteMateria, UUID_ASIGNACION_TESIS) is None:
        hoy = date.today()
        session.add(
            AsignacionDocenteMateria(
                id=UUID_ASIGNACION_TESIS,
                desde=hoy - timedelta(days=365),
                hasta=hoy + timedelta(days=365),
                habilita_aval=True,
                docente_id=UUID_DOCENTE,
                materia_id=UUID_MAT_TESIS,
            )
        )

    restriccion = session.scalar(
        select(Restriccion).where(
            Restriccion.estudiante_id == UUID_EST_RESTRINGIDO
        )
    )
    if restriccion is None:
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(
            Restriccion(
                estudiante_id=UUID_EST_RESTRINGIDO,
                tipo_codigo="CAMARA",
                motivo="Devolucion pendiente con demora registrada en el laboratorio.",
                desde=ahora - timedelta(days=2),
                hasta=ahora + timedelta(days=30),
            )
        )

    session.commit()


def inicializar_base(database_url: str = DATABASE_URL_DEFECTO) -> None:
    connect_args = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    engine = create_engine(database_url, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    fabrica_sesiones = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    with fabrica_sesiones() as session:
        poblar_datos_demo(session)


if __name__ == "__main__":
    inicializar_base()
    print("Base SQLite inicializada con datos ficticios en tpi_cu01.db")
