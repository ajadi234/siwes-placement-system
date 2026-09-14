from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import db, User
from extensions import mail


auth = Blueprint("auth", __name__)

# Tokens expire after 1 hour (in seconds)
RESET_TOKEN_MAX_AGE = 3600


def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _send_reset_email(user):
    serializer = _get_serializer()
    token = serializer.dumps(user.email, salt="password-reset")

    reset_url = url_for("auth.reset_password", token=token, _external=True)

    msg = Message(
        subject="Reset your SIWES Connect password",
        recipients=[user.email],
        body=(
            f"Hi {user.full_name},\n\n"
            f"We received a request to reset your password. Click the link "
            f"below to set a new one. This link expires in 1 hour.\n\n"
            f"{reset_url}\n\n"
            f"If you didn't request this, you can safely ignore this email."
        ),
    )

    mail.send(msg)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        is_approved = False if role == "company" else True

        new_user = User(
            full_name=full_name,
            email=email,
            password=hashed_password,
            role=role,
            is_approved=is_approved
        )

        db.session.add(new_user)
        db.session.commit()

        if role == "company":
            flash(
                "Registration successful! Your company account "
                "is pending admin approval before you can post "
                "opportunities."
            )
        else:
            flash("Registration successful! Please login.")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            if user.role == "student":
                return redirect(url_for("student.dashboard"))
            elif user.role == "company":
                return redirect(url_for("company.dashboard"))
            elif user.role == "admin":
                return redirect(url_for("admin.dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))


# =========================
# FORGOT PASSWORD
# =========================

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        user = User.query.filter_by(email=email).first()

        # Always show the same message whether or not the account
        # exists, so we don't reveal which emails are registered.
        if user:
            try:
                _send_reset_email(user)
            except Exception:
                # Email sending failed (e.g. bad SMTP config). Don't
                # crash the request or leak the error to the user.
                current_app.logger.exception("Failed to send reset email")

        flash(
            "If an account with that email exists, a password reset "
            "link has been sent."
        )
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


# =========================
# RESET PASSWORD
# =========================

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    serializer = _get_serializer()

    try:
        email = serializer.loads(
            token, salt="password-reset", max_age=RESET_TOKEN_MAX_AGE
        )
    except SignatureExpired:
        flash("That password reset link has expired. Please request a new one.")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("That password reset link is invalid.")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("That password reset link is invalid.")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("reset_password.html", token=token)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return render_template("reset_password.html", token=token)

        user.password = generate_password_hash(password)
        db.session.commit()

        flash("Your password has been reset. You can now log in.")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)