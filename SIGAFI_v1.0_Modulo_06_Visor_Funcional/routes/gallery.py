from flask import Blueprint, render_template

from models.actividad import Actividad
from models.foto import Foto

gallery = Blueprint("gallery", __name__)


@gallery.route("/galeria")
def galeria():

    actividades = (
        Actividad.query
        .order_by(
            Actividad.fecha.desc()
        )
        .all()
    )

    return render_template(
        "galeria.html",
        actividades=actividades
    )


@gallery.route("/album/<int:id>")
def album(id):

    actividad = Actividad.query.get_or_404(id)

    fotos = (
        Foto.query
        .filter_by(actividad_id=id)
        .all()
    )

    fotos = (
    Foto.query
    .filter_by(actividad_id=id)
    .all()
)

    print("======================")
    print("Actividad:", actividad.nombre)
    print("ID:", id)
    print("Cantidad de fotos:", len(fotos))

    for f in fotos:
        print(f.id, f.nombre)

    print("======================")

    return render_template(
        "album.html",
        actividad=actividad,
        fotos=fotos
    )