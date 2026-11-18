
from sqlalchemy.orm import Session
from app.models import Notificacion

class NotificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear_notificacion(self, destinatario_id, mensaje, solicitud_numero=None):
        notificacion = Notificacion( destinatario_id=destinatario_id, mensaje=mensaje, solicitud_numero=solicitud_numero)
        self.session.add(notificacion)
        self.session.commit()
        return notificacion

    def listar_por_destinatario(self, destinatario_id):
        return (self.session.query(Notificacion)
        .filter(Notificacion.destinatario_id == destinatario_id)
        .order_by(Notificacion.fecha_creacion.desc()).all())
