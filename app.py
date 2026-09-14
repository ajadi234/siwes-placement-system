import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from extensions import mail
from models.user import db, User
from models.student_profile import StudentProfile
from models.company_profile import CompanyProfile
from models.opportunity import Opportunity
from models.application import Application

from routes.auth import auth
from routes.student import student
from routes.company import company
from routes.admin import admin


app = Flask(__name__)

# SECRET_KEY comes from the environment in production. The fallback
# is only for local development.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-secret-key-change-me"
)

# DATABASE_URL is provided automatically by Render/other hosts when
# a Postgres instance is attached. Falls back to local SQLite.
db_url = os.environ.get("DATABASE_URL", "sqlite:///siwes.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Email configuration (for password reset) ---
# Set these as real environment variables on your server (PythonAnywhere/
# Render). Never commit real credentials to GitHub.
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")  # your Gmail address
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")  # the 16-char App Password
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")


# Database
db.init_app(app)

# Mail
mail.init_app(app)

# CSRF protection
csrf = CSRFProtect(app)

# Login manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(student)
app.register_blueprint(company)
app.register_blueprint(admin)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Create database tables if they don't exist yet.
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)