from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(role):
    """
    Restricts a route to users whose `role` matches the given value.
    Must be used together with @login_required (stack it below).
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator