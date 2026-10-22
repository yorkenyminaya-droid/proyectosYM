from flask import Blueprint, render_template

from utils.auth import login_required

about = Blueprint("about", __name__)


@about.route("/acerca")
@login_required
def acerca():

    return render_template("acerca.html")