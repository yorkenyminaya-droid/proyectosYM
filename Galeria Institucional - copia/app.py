import os
import sys
from flask import Flask, render_template, send_from_directory

from config import Config
from database.db import db
from models.actividad import Actividad
from routes.main import main
from routes.upload import upload
from routes.gallery import gallery
from routes.foto import foto
from routes.inicio import inicio
from routes.login import login
from routes.about import about

# Detectar si se ejecuta desde PyInstaller
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_PATH, "templates"),
    static_folder=os.path.join(BASE_PATH, "static")
)

app.config.from_object(Config)

db.init_app(app)

import models

app.register_blueprint(about)
app.register_blueprint(login)
app.register_blueprint(inicio)
app.register_blueprint(main)
app.register_blueprint(upload)
app.register_blueprint(gallery)
app.register_blueprint(foto)

with app.app_context():
    db.create_all()


from flask import render_template

@app.errorhandler(404)
def pagina_no_encontrada(error):

    return render_template("404.html"), 404

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.static_folder, "img"),
        "logo.ico",
        mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    app.run(debug=True)