from functools import wraps

from flask import session, redirect, url_for


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        print("LOGIN_REQUIRED EJECUTADO")

        if "usuario" not in session:
            return redirect(url_for("login.login_view"))

        return func(*args, **kwargs)

    return wrapper