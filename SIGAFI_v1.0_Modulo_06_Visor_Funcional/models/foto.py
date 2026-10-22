from database.db import db
from datetime import datetime


class Foto(db.Model):

    __tablename__ = "fotos"

    id = db.Column(db.Integer, primary_key=True)

    actividad_id = db.Column(
        db.Integer,
        db.ForeignKey("actividades.id"),
        nullable=False
    )

    nombre = db.Column(db.String(255), nullable=False)

    ruta = db.Column(db.String(500), nullable=False)

    tamano = db.Column(db.Integer)

    ancho = db.Column(db.Integer)

    alto = db.Column(db.Integer)

    fecha_subida = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )