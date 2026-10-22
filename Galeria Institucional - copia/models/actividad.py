from database.db import db
from datetime import datetime


class Actividad(db.Model):

    __tablename__ = "actividades"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(200), nullable=False)

    descripcion = db.Column(db.Text)

    fecha = db.Column(db.Date, nullable=False)

    anio = db.Column(db.Integer, nullable=False)

    mes = db.Column(db.Integer, nullable=False)

    lugar = db.Column(db.String(200))

    responsable = db.Column(db.String(200))

    portada = db.Column(db.String(300))

    carpeta = db.Column(db.String(255), nullable=False)

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relación con las fotografías
    fotos = db.relationship(
        "Foto",
        backref="actividad",
        lazy=True,
        cascade="all, delete-orphan"
    )