from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

login = Blueprint("login", __name__)


@login.route("/login", methods=["GET", "POST"])
def login_view():

    if request.method == "POST":

        usuario = request.form.get("usuario")
        password = request.form.get("password")

        if (
            usuario == current_app.config["ADMIN_USER"]
            and
            password == current_app.config["ADMIN_PASSWORD"]
        ):

            session["usuario"] = usuario

            return redirect(url_for("main.dashboard"))

        flash(
            "Usuario o contraseña incorrectos.",
            "danger"
        )

    return render_template("login.html")


@login.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("inicio.index"))