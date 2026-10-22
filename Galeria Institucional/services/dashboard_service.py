from sqlalchemy import extract

from models.actividad import Actividad
from models.foto import Foto


class DashboardService:

    @staticmethod
    def obtener_estadisticas():

        actividades = Actividad.query.count()

        fotos = Foto.query.count()

        anios = Actividad.query.with_entities(
            Actividad.anio
        ).distinct().count()

        recientes = (
            Actividad.query
            .order_by(Actividad.fecha.desc())
            .limit(5)
            .all()
        )

        return {
            "actividades": actividades,
            "fotos": fotos,
            "anios": anios,
            "recientes": recientes
        }