# Add these to your existing auth routes file (e.g. routes/auth.py),
# alongside your login/register routes. Adjust imports to match your project.

from flask import render_template, request, redirect, url_for, flash, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models.user import db, User  # adjust import path if your model lives elsewhere

RESET_TOKEN_MAX_AGE = 1800  # 30 minutes
RESET_SALT = "password-reset-salt"


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=RESET_SALT)


def verify_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializer.loads(token, salt=RESET_SALT, max_age=RESET_TOKEN_MAX_AGE)
    except (SignatureExpired, BadSignature):
        return None


# -------------------- FORGOT PASSWORD --------------------
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        user = User.query.filter_by(email=email.lower()).first() if email else None

        if user:
            token = generate_reset_token(user.email)
            reset_link = url_for("auth.reset_password", token=token, _external=True)

            # TODO: replace with real email sending (Flask-Mail, SendGrid, etc.)
            current_app.logger.info(f"[DEV ONLY] Reset link for {user.email}: {reset_link}")

        # Same message either way, so people can't probe which emails are registered
        flash("If an account with that email exists, a password reset link has been sent.")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


# -------------------- RESET PASSWORD --------------------
@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = verify_reset_token(token)

    if not email:
        flash("This reset link is invalid or has expired. Please try again.")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or new_password != confirm_password:
            flash("Passwords do not match. Please try again.")
            return render_template("reset_password.html")

        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            flash("This reset link is invalid or has expired.")
            return redirect(url_for("auth.forgot_password"))

        user.set_password(new_password)
        db.session.commit()

        flash("Password reset successfully. You can now log in.")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")