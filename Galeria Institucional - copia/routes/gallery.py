from flask import Blueprint, render_template, request

from models.actividad import Actividad
from models.foto import Foto

from datetime import datetime
from utils.auth import login_required

import os
import shutil

import zipfile
import tempfile

from flask import send_file

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
    
)

from database.db import db

gallery = Blueprint("gallery", __name__)


@gallery.route("/galeria")
@login_required
def galeria():

    buscar = request.args.get("buscar", "").strip()
    anio = request.args.get("anio", "").strip()
    mes = request.args.get("mes", "").strip()

    consulta = Actividad.query

    # Buscar por nombre
    if buscar:
        consulta = consulta.filter(
            Actividad.nombre.ilike(f"%{buscar}%")
        )

    # Filtrar por año
    if anio:
        consulta = consulta.filter(
            Actividad.anio == int(anio)
        )

    # Filtrar por mes
    if mes:
        consulta = consulta.filter(
            Actividad.mes == int(mes)
        )

    actividades = (
        consulta
        .order_by(Actividad.fecha.desc())
        .all()
    )

    anios = (
        Actividad.query
        .with_entities(Actividad.anio)
        .distinct()
        .order_by(Actividad.anio.desc())
        .all()
    )

    anios = [a[0] for a in anios]

    return render_template(
        "galeria.html",
        actividades=actividades,
        buscar=buscar,
        anios=anios,
        anio=anio,
        mes=mes
    )

@gallery.route("/album/<int:id>")
@login_required
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

@gallery.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):

    actividad = Actividad.query.get_or_404(id)

    if request.method == "POST":

        actividad.nombre = request.form.get("nombre")

        db.session.commit()

        flash(
            "Actividad actualizada correctamente.",
            "success"
        )

        return redirect(url_for("gallery.galeria"))

    return render_template(
        "editar.html",
        actividad=actividad
    )

@gallery.route("/eliminar/<int:id>")
@login_required
def eliminar(id):

    actividad = Actividad.query.get_or_404(id)

    # Guardamos la ruta antes de borrar
    carpeta_actividad = actividad.carpeta

    if carpeta_actividad and os.path.exists(carpeta_actividad):
        shutil.rmtree(carpeta_actividad)

        # Carpeta del año
        carpeta_anio = os.path.dirname(carpeta_actividad)

        # Si quedó vacía, eliminarla
        if os.path.exists(carpeta_anio) and not os.listdir(carpeta_anio):
            os.rmdir(carpeta_anio)

    db.session.delete(actividad)
    db.session.commit()

    flash(
        "Actividad eliminada correctamente.",
        "success"
    )

    return redirect(url_for("gallery.galeria"))


@gallery.route("/descargar/<int:id>")
@login_required
def descargar(id):

    actividad = Actividad.query.get_or_404(id)

    archivo_temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".zip"
    )

    with zipfile.ZipFile(
        archivo_temp.name,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for foto in actividad.fotos:

            if os.path.exists(foto.ruta):

                zipf.write(
                    foto.ruta,
                    arcname=foto.nombre
                )

    return send_file(
        archivo_temp.name,
        as_attachment=True,
        download_name=f"{actividad.nombre}.zip"
    )