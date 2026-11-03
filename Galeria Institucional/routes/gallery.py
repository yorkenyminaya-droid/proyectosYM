
import os
import shutil
import zipfile
import tempfile
import uuid

from datetime import datetime

from PIL import Image
from werkzeug.utils import secure_filename

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
from models.actividad import Actividad
from models.foto import Foto
from utils.auth import login_required


gallery = Blueprint("gallery", __name__)

EXTENSIONES_PERMITIDAS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"
}


@gallery.route("/galeria")
@login_required
def galeria():

    buscar = request.args.get("buscar", "").strip()
    anio = request.args.get("anio", "").strip()
    mes = request.args.get("mes", "").strip()

    consulta = Actividad.query

    if buscar:
        consulta = consulta.filter(
            Actividad.nombre.ilike(f"%{buscar}%")
        )

    if anio:
        consulta = consulta.filter(
            Actividad.anio == int(anio)
        )

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

    fotos = Foto.query.filter_by(
        actividad_id=id
    ).all()

    return render_template(
        "album.html",
        actividad=actividad,
        fotos=fotos
    )


# NUEVA RUTA PARA MOSTRAR FOTOGRAFIAS
@gallery.route("/editar/foto/<int:foto_id>")
@login_required
def foto_edicion(foto_id):

    foto = Foto.query.get_or_404(foto_id)

    if not foto.ruta or not os.path.isfile(foto.ruta):
        flash("La fotografía no está disponible.", "danger")
        return redirect(
            url_for("gallery.editar", id=foto.actividad_id)
        )

    return send_file(foto.ruta)


# EDITAR ACTIVIDAD Y ADMINISTRAR FOTOGRAFIAS
@gallery.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):

    actividad = Actividad.query.get_or_404(id)

    if request.method == "POST":

        archivos_nuevos = []
        rutas_nuevas = []
        rutas_eliminadas = []

        try:

            nombre = request.form.get("nombre", "").strip()
            fecha = request.form.get("fecha", "").strip()

            if not nombre or not fecha:
                flash(
                    "Debe completar el nombre y la fecha.",
                    "danger"
                )
                return redirect(
                    url_for("gallery.editar", id=id)
                )

            fecha_obj = datetime.strptime(
                fecha, "%Y-%m-%d"
            ).date()

            actividad.nombre = nombre
            actividad.fecha = fecha_obj
            actividad.anio = fecha_obj.year
            actividad.mes = fecha_obj.month

            # FOTOGRAFIAS QUE SE DESEAN ELIMINAR

            ids_eliminar = set(
                request.form.getlist("eliminar_fotos")
            )

            for foto in list(actividad.fotos):

                if str(foto.id) in ids_eliminar:

                    rutas_eliminadas.append(foto.ruta)

                    db.session.delete(foto)

            # AGREGAR NUEVAS FOTOGRAFIAS

            carpeta = actividad.carpeta

            os.makedirs(carpeta, exist_ok=True)

            archivos = request.files.getlist("fotos_nuevas")

            for archivo in archivos:

                if not archivo or not archivo.filename:
                    continue

                extension = os.path.splitext(
                    archivo.filename
                )[1].lower()

                if extension not in EXTENSIONES_PERMITIDAS:
                    raise ValueError(
                        "Formato de fotografía no permitido: "
                        + extension
                    )

                # Verificar que realmente sea una imagen

                try:
                    archivo.stream.seek(0)

                    with Image.open(archivo.stream) as imagen:
                        imagen.verify()

                    archivo.stream.seek(0)

                    with Image.open(archivo.stream) as imagen:
                        ancho, alto = imagen.size

                except Exception:
                    raise ValueError(
                        "Uno de los archivos seleccionados "
                        "no es una imagen válida."
                    )

                nombre_original = secure_filename(
                    archivo.filename
                )

                nombre_base = os.path.splitext(
                    nombre_original
                )[0]

                nombre_archivo = (
                    nombre_base + "_" + uuid.uuid4().hex[:8]
                    + extension
                )

                ruta_archivo = os.path.join(
                    carpeta,
                    nombre_archivo
                )

                archivo.stream.seek(0)
                archivo.save(ruta_archivo)

                rutas_nuevas.append(ruta_archivo)

                tamano = os.path.getsize(ruta_archivo)

                foto = Foto(
                    actividad_id=actividad.id,
                    nombre=nombre_archivo,
                    ruta=ruta_archivo,
                    tamano=tamano,
                    ancho=ancho,
                    alto=alto
                )

                db.session.add(foto)

            # ACTUALIZAR PORTADA SI FUE ELIMINADA

            db.session.flush()

            if (
                not actividad.portada
                or actividad.portada in rutas_eliminadas
                or not os.path.isfile(actividad.portada)
            ):

                actividad.portada = (
                    actividad.fotos[0].ruta
                    if actividad.fotos
                    else None
                )

            # GUARDAR TODOS LOS CAMBIOS

            db.session.commit()

            # ELIMINAR DEL DISCO LAS FOTOGRAFIAS SELECCIONADAS

            for ruta in rutas_eliminadas:

                try:
                    if ruta and os.path.isfile(ruta):

                        carpeta_real = os.path.realpath(
                            actividad.carpeta
                        )

                        ruta_real = os.path.realpath(ruta)

                        if os.path.commonpath(
                            [carpeta_real, ruta_real]
                        ) == carpeta_real:

                            os.remove(ruta)

                except (OSError, ValueError):
                    pass

            flash(
                "Álbum actualizado correctamente.",
                "success"
            )

            return redirect(
                url_for("gallery.album", id=id)
            )

        except ValueError as error:

            db.session.rollback()

            for ruta in rutas_nuevas:
                try:
                    if os.path.isfile(ruta):
                        os.remove(ruta)
                except OSError:
                    pass

            flash(str(error), "danger")

            return redirect(
                url_for("gallery.editar", id=id)
            )

        except Exception:

            db.session.rollback()

            for ruta in rutas_nuevas:
                try:
                    if os.path.isfile(ruta):
                        os.remove(ruta)
                except OSError:
                    pass

            flash(
                "Ocurrió un error al actualizar el álbum. "
                "No se pudieron guardar los cambios.",
                "danger"
            )

            return redirect(
                url_for("gallery.editar", id=id)
            )

    return render_template(
        "editar.html",
        actividad=actividad
    )


@gallery.route("/eliminar/<int:id>")
@login_required
def eliminar(id):

    actividad = Actividad.query.get_or_404(id)

    carpeta_actividad = actividad.carpeta

    if carpeta_actividad and os.path.exists(carpeta_actividad):

        shutil.rmtree(carpeta_actividad)

        carpeta_anio = os.path.dirname(carpeta_actividad)

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

    archivo_temp.close()

    return send_file(
        archivo_temp.name,
        as_attachment=True,
        download_name=f"{actividad.nombre}.zip"
    )
