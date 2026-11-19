"""Carga idempotente de datos ficticios de demostración para CU_01."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import (
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

# UUIDs fijos para que el seed sea 100% repetible entre reinicios
UUID_EST_COMUN = UUID("11111111-1111-1111-1111-111111111101")
UUID_EST_ELEGIBLE = UUID("11111111-1111-1111-1111-111111111102")
UUID_EST_RESTRINGIDO = UUID("11111111-1111-1111-1111-111111111103")
UUID_DOCENTE = UUID("11111111-1111-1111-1111-111111111104")
UUID_PERSONAL = UUID("11111111-1111-1111-1111-111111111105")

UUID_MAT_PROYECTO2 = UUID("22222222-2222-2222-2222-222222222201")
UUID_MAT_TALLER = UUID("22222222-2222-2222-2222-222222222202")
UUID_MAT_TESIS = UUID("22222222-2222-2222-2222-222222222203")


def poblar_datos_demo(session: Session) -> None:
    """Inserta usuarios, tipos, unidades, materias y restricciones demo si no existen."""
    # 1. Usuarios ficticios de demostración (coinciden con el selector X-Usuario-Demo)
    usuarios_demo: list[Usuario] = [
        Estudiante(
            id=UUID_EST_COMUN,
            nombre_completo="Camila Rojas (Estudiante Común)",
            dni="42100101",
            correo="camila.rojas@demo.untdf.edu.ar",
            alias="estudiante-comun",
            elegible_alta_gama=False,
        ),
        Estudiante(
            id=UUID_EST_ELEGIBLE,
            nombre_completo="Mateo Pereyra (Estudiante Elegible)",
            dni="41200202",
            correo="mateo.pereyra@demo.untdf.edu.ar",
            alias="estudiante-elegible",
            elegible_alta_gama=True,
        ),
        Estudiante(
            id=UUID_EST_RESTRINGIDO,
            nombre_completo="Lucas Fernández (Estudiante Restringido)",
            dni="43300303",
            correo="lucas.fernandez@demo.untdf.edu.ar",
            alias="estudiante-restringido",
            elegible_alta_gama=False,
        ),
        Docente(
            id=UUID_DOCENTE,
            nombre_completo="Prof. Valeria Méndez (Docente)",
            dni="28400404",
            correo="valeria.mendez@demo.untdf.edu.ar",
            alias="docente-demo",
            es_tutor=True,
        ),
        PersonalLaboratorio(
            id=UUID_PERSONAL,
            nombre_completo="Martín Sosa (Personal Laboratorio)",
            dni="31500505",
            correo="martin.sosa@demo.untdf.edu.ar",
            alias="personal-demo",
        ),
    ]

    for usuario in usuarios_demo:
        existente = session.scalar(select(Usuario).where(Usuario.alias == usuario.alias))
        if existente is None:
            session.add(usuario)

    session.flush()

    # 2. Restricción activa para estudiante-restringido (TC-04)
    restriccion_existente = session.scalar(
        select(Restriccion).where(Restriccion.estudiante_id == UUID_EST_RESTRINGIDO)
    )
    if restriccion_existente is None:
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(
            Restriccion(
                estudiante_id=UUID_EST_RESTRINGIDO,
                tipo_codigo=None,
                motivo="Devolución pendiente con demora registrada en el laboratorio.",
                desde=ahora - timedelta(days=2),
                hasta=ahora + timedelta(days=30),
                activa=True,
            )
        )

    # 3. Tipos de equipamiento
    tipos = [
        TipoEquipamiento(codigo="CAMARA", nombre="Cámara HD", alta_gama=False),
        TipoEquipamiento(
            codigo="MICROFONO", nombre="Kit Micrófono Direccional", alta_gama=False
        ),
        TipoEquipamiento(codigo="CINE_PRO", nombre="Cámara Cine 4K", alta_gama=True),
    ]
    for tipo in tipos:
        if session.get(TipoEquipamiento, tipo.codigo) is None:
            session.add(tipo)

    session.flush()

    # 4. Unidades físicas en inventario (incluye una en MANTENIMIENTO para TC-06)
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
        existe_eq = session.scalar(
            select(Equipamiento).where(Equipamiento.numero_inventario == inventario)
        )
        if existe_eq is None:
            session.add(
                Equipamiento(
                    numero_inventario=inventario,
                    tipo_codigo=tipo_codigo,
                    estado=estado,
                )
            )

    # 5. Materias y proyectos
    materias = [
        MateriaProyecto(
            id=UUID_MAT_PROYECTO2,
            nombre="Proyecto 2",
            prioridad=2,
            habilita_alta_gama=False,
        ),
        MateriaProyecto(
            id=UUID_MAT_TALLER,
            nombre="Taller de Producción Audiovisual",
            prioridad=1,
            habilita_alta_gama=False,
        ),
        MateriaProyecto(
            id=UUID_MAT_TESIS,
            nombre="Proyecto 4 - Tesis Audiovisual",
            prioridad=3,
            habilita_alta_gama=True,
        ),
    ]
    for materia in materias:
        if session.get(MateriaProyecto, materia.id) is None:
            session.add(materia)

    session.commit()


def inicializar_base(database_url: str = DATABASE_URL_DEFECTO) -> None:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        poblar_datos_demo(session)


if __name__ == "__main__":
    inicializar_base()
    print("Base de datos SQLite inicializada con datos demo en tpi_cu01.db")