from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for
)

from services.dashboard_service import DashboardService

main = Blueprint("main", __name__)


@main.route("/dashboard")
def dashboard():

    if "usuario" not in session:

        return redirect(url_for("login.login_view"))

    datos = DashboardService.obtener_estadisticas()

    return render_template(
        "dashboard.html",
        datos=datos
    )