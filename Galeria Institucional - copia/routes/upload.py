from flask import Blueprint, render_template, request, redirect, url_for, flash


from services.upload_service import UploadService

from utils.auth import login_required



upload = Blueprint("upload", __name__)


@upload.route("/subir", methods=["GET", "POST"])
@login_required
def subir():

    if request.method == "POST":

        fecha = request.form.get("fecha")
        actividad = request.form.get("actividad")
        fotos = request.files.getlist("fotos")
        print("Cantidad de fotos:", len(fotos))

        if not fecha or not actividad:
            flash("Debe completar la fecha y el nombre de la actividad.", "danger")
            return redirect(url_for("upload.subir"))

        UploadService.guardar_actividad(
        actividad,
        fecha,
        fotos
)

        flash("Actividad creada correctamente.", "success")

        return redirect(url_for("upload.subir"))

    return render_template("subir.html")