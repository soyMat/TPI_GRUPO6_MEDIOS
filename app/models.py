
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import (Boolean, DateTime, ForeignKey, Integer, String, Uuid)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship)
from sqlalchemy import Date
from datetime import date


class Base(DeclarativeBase):
    pass

# Usuarios y herencia de usuarios
class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nombre_completo: Mapped[str] = mapped_column(String(150))
    dni: Mapped[str] = mapped_column(String(20), unique=True)
    correo: Mapped[str] = mapped_column(String(150), unique=True)
    # Alias utilizado para identificar usuarios ficticios
    alias: Mapped[str] = mapped_column(String(50), unique=True)
    # Discriminador de herencia
    tipo_usuario: Mapped[str] = mapped_column(String(30))
    solicitudes: Mapped[list["Solicitud"]] = relationship(back_populates="usuario")
    notificaciones: Mapped[list["Notificacion"]] = relationship(back_populates="destinatario")
    __mapper_args__ = {
        "polymorphic_on": tipo_usuario,
        "polymorphic_identity": "usuario"
    }

# Estudiantes
class Estudiante(Usuario):
    __tablename__ = "estudiantes"
    id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    carrera: Mapped[str] = mapped_column(String)
    anio_cursada: Mapped[int] = mapped_column(Integer)
    tesista_avanzado: Mapped[bool] = mapped_column(Boolean)
    restricciones: Mapped[list["Restriccion"]] = relationship(back_populates="estudiante")
    __mapper_args__ = {
        "polymorphic_identity": "estudiante"
    }

# Docentes
class Docente(Usuario):
    __tablename__ = "docentes"
    id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    es_tutor: Mapped[bool] = mapped_column(Boolean)
    especialidad: Mapped[str] = mapped_column(String)
    asignaciones_materia: Mapped[list["AsignacionDocenteMateria"]] = relationship(back_populates="docente")
    __mapper_args__ = {
        "polymorphic_identity": "docente"
    }

# Personal de laboratorio, que hereda de Usuario y tiene un legajo
class PersonalLaboratorio(Usuario):
    __tablename__ = "personal_laboratorio"
    id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    legajo: Mapped[str] = mapped_column(String)
    __mapper_args__ = {
        "polymorphic_identity": "personal_laboratorio"
    }

# Directora, que hereda de Usuario y representa a la directora del laboratorio
class Directora(Usuario):
    __tablename__ = "directoras"
    id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "directora"
    }

# Tipo de equipamiento, que tiene un codigo, nombre y si es de alta gama o no. Tambien tiene una relacion con la clase equipamiento
class TipoEquipamiento(Base):
    __tablename__ = "tipos_equipamiento"
    codigo: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    alta_gama: Mapped[bool] = mapped_column(Boolean, default=False)
    equipamientos: Mapped[list["Equipamiento"]] = relationship(back_populates="tipo")
    restricciones: Mapped[list["Restriccion"]] = relationship()
    tipo: Mapped["TipoEquipamiento"] = relationship()

# EQUIPAMIENTO
class Equipamiento(Base):
    __tablename__ = "equipamientos"
    id: Mapped[int] = mapped_column(primary_key=True)
    numero_inventario: Mapped[str] = mapped_column(String(50), unique=True)
    tipo_codigo: Mapped[str] = mapped_column(ForeignKey("tipos_equipamiento.codigo"))
    estado: Mapped[str] = mapped_column(String(30))
    tipo: Mapped["TipoEquipamiento"] = relationship(back_populates="equipamientos")
    detalles_prestamo: Mapped[list["DetallePrestamo"]] = relationship(back_populates="equipamiento")


# MATERIAS
class MateriaProyecto(Base):
    __tablename__ = "materias_proyecto"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True),primary_key=True,default=uuid4)
    nombre: Mapped[str] = mapped_column(String(100))
    prioridad: Mapped[int] = mapped_column(Integer)
    solicitudes: Mapped[list["SolicitudPrestamo"]] = relationship(back_populates="materia")
    asignaciones_docentes: Mapped[list["AsignacionDocenteMateria"]] = relationship(back_populates="materia")


# Asignacion de un docente a una materia, con un booleano que indica si el docente esta habilitado para avalar solicitudes de esa materia
class AsignacionDocenteMateria(Base):
    __tablename__ = "asignaciones_docente_materia"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    desde: Mapped[date] = mapped_column(Date)
    hasta: Mapped[date] = mapped_column(Date)
    habilita_aval: Mapped[bool] = mapped_column(Boolean)
    docente_id: Mapped[UUID] = mapped_column(ForeignKey("docentes.id"))
    materia_id: Mapped[UUID] = mapped_column(ForeignKey("materias_proyecto.id"))
    docente: Mapped["Docente"] = relationship(back_populates="asignaciones_materia")
    materia: Mapped["MateriaProyecto"] = relationship(back_populates="asignaciones_docentes")


# RESTRICCIONES
class Restriccion(Base):
    __tablename__ = "restricciones"
    id: Mapped[int] = mapped_column(primary_key=True)
    estudiante_id: Mapped[UUID] = mapped_column(ForeignKey("estudiantes.id"))
    tipo_codigo: Mapped[str] = mapped_column(ForeignKey("tipos_equipamiento.codigo"))
    motivo: Mapped[str] = mapped_column(String(200))
    desde: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    hasta: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estudiante: Mapped["Estudiante"] = relationship(back_populates="restricciones")


# SOLICITUDES
class Solicitud(Base):
    __tablename__ = "solicitudes"
    numero: Mapped[str] = mapped_column(String, primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    estado: Mapped[str] = mapped_column(String(40),default="PENDIENTE_SOLICITADA")
    tipo_solicitud: Mapped[str] = mapped_column(String(30))
    usuario: Mapped["Usuario"] = relationship(back_populates="solicitudes")
    cambios_estado: Mapped[list["CambioEstado"]] = relationship(back_populates="solicitud", cascade="all, delete-orphan")
    __mapper_args__ = {
        "polymorphic_on": tipo_solicitud,
        "polymorphic_identity": "solicitud"
    }


# SOLICITUD DE PRESTAMO
class SolicitudPrestamo(Solicitud):
    __tablename__ = "solicitudes_prestamo"
    numero: Mapped[str] = mapped_column(ForeignKey("solicitudes.numero"), primary_key=True)
    tipo_codigo: Mapped[str] = mapped_column(ForeignKey("tipos_equipamiento.codigo"))
    cantidad: Mapped[int] = mapped_column(Integer)
    desde: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    hasta: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    materia_id: Mapped[UUID] = mapped_column(ForeignKey("materias_proyecto.id"))
    requiere_aval: Mapped[bool] = mapped_column(Boolean, default=False)
    materia: Mapped["MateriaProyecto"] = relationship(back_populates="solicitudes")
    __mapper_args__ = {
        "polymorphic_identity": "prestamo"
    }
    tipo: Mapped["TipoEquipamiento"] = relationship()



# CAMBIOS DE ESTADO
class CambioEstado(Base):
    __tablename__ = "cambios_estado"
    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_numero: Mapped[str] = mapped_column(ForeignKey("solicitudes.numero"))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    anterior: Mapped[str | None] = mapped_column(String(40), nullable=True)
    nuevo: Mapped[str] = mapped_column(String(40))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    solicitud: Mapped["Solicitud"] = relationship(back_populates="cambios_estado")
    actor: Mapped["Usuario"] = relationship()


# PRESTAMOS
class Prestamo(Base):
    __tablename__ = "prestamos"
    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_numero: Mapped[str] = mapped_column(ForeignKey("solicitudes_prestamo.numero"), unique=True)
    desde: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    hasta: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    detalles: Mapped[list["DetallePrestamo"]] = relationship(back_populates="prestamo", cascade="all, delete-orphan")



# DETALLES DE PRESTAMO
class DetallePrestamo(Base):
    __tablename__ = "detalles_prestamo"
    id: Mapped[int] = mapped_column(primary_key=True)
    prestamo_id: Mapped[int] = mapped_column(ForeignKey("prestamos.id"))
    equipamiento_id: Mapped[int] = mapped_column(ForeignKey("equipamientos.id"))
    prestamo: Mapped["Prestamo"] = relationship(back_populates="detalles")
    equipamiento: Mapped["Equipamiento"] = relationship(back_populates="detalles_prestamo")


# NOTIFICACIONES
class Notificacion(Base):
    __tablename__ = "notificaciones"
    id: Mapped[int] = mapped_column(primary_key=True)
    destinatario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    solicitud_numero: Mapped[str | None] = mapped_column(ForeignKey("solicitudes.numero"), nullable=True)
    mensaje: Mapped[str] = mapped_column(String(250))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    destinatario: Mapped["Usuario"] = relationship(back_populates="notificaciones")
    solicitud: Mapped["Solicitud | None"] = relationship()
