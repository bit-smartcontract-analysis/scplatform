from flask import g, redirect, url_for
from functools import wraps


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if hasattr(g, "user"):
            return func(*args, **kwargs)
        else:
            return redirect(url_for("front.login"))
    return inner