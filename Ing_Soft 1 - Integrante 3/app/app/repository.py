
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Solicitud, SolicitudPrestamo, CambioEstado

class SolicitudRepository:
    def __init__(self, session: Session):
        self.session = session
    # Crear una solicitud de préstamo
    def crear_solicitud(self, usuario_id, tipo_codigo, cantidad, desde, hasta, materia_id, requiere_aval=False):
        try:
            solicitud = SolicitudPrestamo(usuario_id=usuario_id, tipo_codigo=tipo_codigo, cantidad=cantidad, desde=desde, hasta=hasta, materia_id=materia_id, requiere_aval=requiere_aval, estado="PENDIENTE_SOLICITADA")
            self.session.add(solicitud)
            self.session.flush()
            cambio = CambioEstado(solicitud_numero=solicitud.numero, actor_id=usuario_id, anterior=None, nuevo="PENDIENTE_SOLICITADA")
            self.session.add(cambio)
            self.session.commit()
            return solicitud
        except Exception:
            self.session.rollback()
            raise
    # Buscar una solicitud por su número
    def buscar_por_numero(self, numero):
        consulta = select(Solicitud).where(Solicitud.numero == numero)
        return self.session.scalar(consulta)

    # Consultar todas las solicitudes de un usuario
    def listar_por_usuario(self, usuario_id):
        consulta = (select(Solicitud).where(Solicitud.usuario_id == usuario_id).order_by(Solicitud.creada_en.desc()))
        return list(self.session.scalars(consulta).all())
