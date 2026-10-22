import os

from flask import Blueprint, abort, send_file, render_template

from models.foto import Foto
from utils.auth import login_required

foto = Blueprint("foto", __name__)


@foto.route("/foto/<int:id>")
def ver_foto(id):

    imagen = Foto.query.get_or_404(id)

    if not os.path.exists(imagen.ruta):
        abort(404)

    return send_file(imagen.ruta)


@foto.route("/visor/<int:id>")
def visor(id):

    imagen = Foto.query.get_or_404(id)

    fotos = (
        Foto.query
        .filter_by(actividad_id=imagen.actividad_id)
        .order_by(Foto.id)
        .all()
    )

    anterior = None
    siguiente = None

    for i, f in enumerate(fotos):

        if f.id == imagen.id:

            if i > 0:
                anterior = fotos[i - 1]

            if i < len(fotos) - 1:
                siguiente = fotos[i + 1]

            break

    return render_template(
        "visor.html",
        foto=imagen,
        anterior=anterior,
        siguiente=siguiente
    )