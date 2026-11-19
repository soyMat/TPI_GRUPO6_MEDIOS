from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ==========================================
# USUARIOS Y HERENCIA DE USUARIOS
# ==========================================

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nombre_completo: Mapped[str] = mapped_column(String(150))
    dni: Mapped[str] = mapped_column(String(20), unique=True)
    correo: Mapped[str] = mapped_column(String(150), unique=True)
    alias: Mapped[str] = mapped_column(String(50), unique=True)
    tipo_usuario: Mapped[str] = mapped_column(String(30))

    solicitudes: Mapped[list["Solicitud"]] = relationship(back_populates="usuario")
    notificaciones: Mapped[list["Notificacion"]] = relationship(back_populates="destinatario")

    __mapper_args__ = {
        "polymorphic_on": tipo_usuario,
        "polymorphic_identity": "usuario",
    }

    @property
    def rol(self) -> str:
        """Alias compatible con contrato compartido y PoliticaPrestamo."""
        return self.tipo_usuario


class Estudiante(Usuario):
    __tablename__ = "estudiantes"

    id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    elegible_alta_gama: Mapped[bool] = mapped_column(Boolean, default=False)

    restricciones: Mapped[list["Restriccion"]] = relationship(back_populates="estudiante")

    __mapper_args__ = {
        "polymorphic_identity": "estudiante",
    }


class Docente(Usuario):
    __tablename__ = "docentes"

    id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    es_tutor: Mapped[bool] = mapped_column(Boolean, default=True)

    __mapper_args__ = {
        "polymorphic_identity": "docente",
    }


class PersonalLaboratorio(Usuario):
    """Rol operativo no habilitado para crear solicitudes en CU_01 (TC-13)."""

    __mapper_args__ = {
        "polymorphic_identity": "PersonalLaboratorio",
    }


# ==========================================
# EQUIPAMIENTO
# ==========================================

class TipoEquipamiento(Base):
    __tablename__ = "tipos_equipamiento"

    codigo: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    alta_gama: Mapped[bool] = mapped_column(Boolean, default=False)

    equipamientos: Mapped[list["Equipamiento"]] = relationship(back_populates="tipo")

    @property
    def id(self) -> str:
        """Alias compatible con TipoEquipamientoSalida y PoliticaPrestamo."""
        return self.codigo


class Equipamiento(Base):
    __tablename__ = "equipamientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_inventario: Mapped[str] = mapped_column(String(50), unique=True)
    tipo_codigo: Mapped[str] = mapped_column(ForeignKey("tipos_equipamiento.codigo"))
    estado: Mapped[str] = mapped_column(String(30), default="OPERATIVO")

    tipo: Mapped["TipoEquipamiento"] = relationship(back_populates="equipamientos")
    detalles_prestamo: Mapped[list["DetallePrestamo"]] = relationship(back_populates="equipamiento")


# ==========================================
# MATERIAS Y RESTRICCIONES
# ==========================================

class MateriaProyecto(Base):
    __tablename__ = "materias_proyecto"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(100))
    prioridad: Mapped[int] = mapped_column(Integer, default=1)
    habilita_alta_gama: Mapped[bool] = mapped_column(Boolean, default=False)

    solicitudes: Mapped[list["SolicitudPrestamo"]] = relationship(back_populates="materia")


class Restriccion(Base):
    __tablename__ = "restricciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    estudiante_id: Mapped[UUID] = mapped_column(ForeignKey("estudiantes.id"))
    tipo_codigo: Mapped[str | None] = mapped_column(
        ForeignKey("tipos_equipamiento.codigo"), nullable=True
    )
    motivo: Mapped[str] = mapped_column(String(200))
    desde: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    hasta: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    estudiante: Mapped["Estudiante"] = relationship(back_populates="restricciones")

    @property
    def tipo_id(self) -> str | None:
        return self.tipo_codigo


# ==========================================
# SOLICITUDES Y AUDITORÍA
# ==========================================

class Solicitud(Base):
    __tablename__ = "solicitudes"

    numero: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    estado: Mapped[str] = mapped_column(String(40), default="PENDIENTE_SOLICITADA")
    tipo_solicitud: Mapped[str] = mapped_column(String(30))

    usuario: Mapped["Usuario"] = relationship(back_populates="solicitudes")
    cambios_estado: Mapped[list["CambioEstado"]] = relationship(
        back_populates="solicitud", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_on": tipo_solicitud,
        "polymorphic_identity": "solicitud",
    }


class SolicitudPrestamo(Solicitud):
    __tablename__ = "solicitudes_prestamo"

    numero: Mapped[int] = mapped_column(ForeignKey("solicitudes.numero"), primary_key=True)
    tipo_codigo: Mapped[str] = mapped_column(ForeignKey("tipos_equipamiento.codigo"))
    cantidad: Mapped[int] = mapped_column(Integer)
    desde: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    hasta: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    materia_id: Mapped[UUID] = mapped_column(ForeignKey("materias_proyecto.id"))
    requiere_aval: Mapped[bool] = mapped_column(Boolean, default=False)

    tipo: Mapped["TipoEquipamiento"] = relationship()
    materia: Mapped["MateriaProyecto"] = relationship(back_populates="solicitudes")

    __mapper_args__ = {
        "polymorphic_identity": "prestamo",
    }


class CambioEstado(Base):
    __tablename__ = "cambios_estado"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_numero: Mapped[int] = mapped_column(ForeignKey("solicitudes.numero"))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    anterior: Mapped[str | None] = mapped_column(String(40), nullable=True)
    nuevo: Mapped[str] = mapped_column(String(40))
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    solicitud: Mapped["Solicitud"] = relationship(back_populates="cambios_estado")
    actor: Mapped["Usuario"] = relationship()


# ==========================================
# PRÉSTAMOS EFECTIVOS Y NOTIFICACIONES
# ==========================================

class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_numero: Mapped[int] = mapped_column(
        ForeignKey("solicitudes_prestamo.numero"), unique=True
    )
    desde: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    hasta: Mapped[datetime] = mapped_column(DateTime(timezone=False))

    detalles: Mapped[list["DetallePrestamo"]] = relationship(
        back_populates="prestamo", cascade="all, delete-orphan"
    )


class DetallePrestamo(Base):
    __tablename__ = "detalles_prestamo"

    id: Mapped[int] = mapped_column(primary_key=True)
    prestamo_id: Mapped[int] = mapped_column(ForeignKey("prestamos.id"))
    equipamiento_id: Mapped[int] = mapped_column(ForeignKey("equipamientos.id"))

    prestamo: Mapped["Prestamo"] = relationship(back_populates="detalles")
    equipamiento: Mapped["Equipamiento"] = relationship(back_populates="detalles_prestamo")


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    destinatario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    solicitud_numero: Mapped[int | None] = mapped_column(
        ForeignKey("solicitudes.numero"), nullable=True
    )
    mensaje: Mapped[str] = mapped_column(String(250))
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    destinatario: Mapped["Usuario"] = relationship(back_populates="notificaciones")
    solicitud: Mapped["Solicitud | None"] = relationship()