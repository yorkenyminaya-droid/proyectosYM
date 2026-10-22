from flask import Blueprint, render_template

from services.dashboard_service import DashboardService

main = Blueprint("main", __name__)


@main.route("/")
def dashboard():

    datos = DashboardService.obtener_estadisticas()

    return render_template(
        "dashboard.html",
        datos=datos
    )