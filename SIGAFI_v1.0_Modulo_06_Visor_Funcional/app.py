from flask import Flask

from config import Config
from database.db import db
from models.actividad import Actividad
from routes.main import main
from routes.upload import upload
from routes.gallery import gallery
from routes.foto import foto

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

import models

app.register_blueprint(main)
app.register_blueprint(upload)
app.register_blueprint(gallery)
app.register_blueprint(foto)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)