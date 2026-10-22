import os
from datetime import datetime

from PIL import Image
from werkzeug.utils import secure_filename

from config import Config
from database.db import db
from models.actividad import Actividad
from models.foto import Foto


class UploadService:

    @staticmethod
    def guardar_actividad(nombre, fecha, archivos):

        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")

        anio = fecha_obj.year
        numero_mes = fecha_obj.month

        meses = [
            "",
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]

        mes = meses[numero_mes]

        carpeta = os.path.join(
            Config.UPLOAD_FOLDER,
            str(anio),
            mes,
            fecha,
            secure_filename(nombre)
        )

        os.makedirs(carpeta, exist_ok=True)

        actividad = Actividad(
            nombre=nombre,
            fecha=fecha_obj,
            anio=anio,
            mes=numero_mes,
            carpeta=carpeta
        )

        db.session.add(actividad)
        db.session.commit()

                # Guardar fotografías
        primera_foto = None

        for archivo in archivos:

            if archivo.filename == "":
                continue

            nombre_archivo = secure_filename(archivo.filename)

            ruta_archivo = os.path.join(
                carpeta,
                nombre_archivo
            )

            archivo.save(ruta_archivo)

            tamano = os.path.getsize(ruta_archivo)

            with Image.open(ruta_archivo) as img:
                ancho, alto = img.size

            foto = Foto(
                actividad_id=actividad.id,
                nombre=nombre_archivo,
                ruta=ruta_archivo,
                tamano=tamano,
                ancho=ancho,
                alto=alto
            )

            db.session.add(foto)

            # Guardar la ruta de la primera foto como portada
            if primera_foto is None:
                primera_foto = ruta_archivo

        # Guardar la portada en la actividad
        actividad.portada = primera_foto

        db.session.commit()

        return actividad