from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import db, User


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.")
            return redirect(url_for("auth.register"))

        # Create secure password hash
        hashed_password = generate_password_hash(password)

        # Companies need admin approval before they can post
        # opportunities. Students are approved automatically.
        is_approved = False if role == "company" else True

        # Create user
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

            # Send user to the correct dashboard
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