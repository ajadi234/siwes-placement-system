import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf import CSRFProtect

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

# SECRET_KEY comes from the environment in production (set this in
# Render's dashboard). The fallback is only for local development.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-secret-key-change-me"
)

# DATABASE_URL is provided automatically by Render when you attach a
# Postgres instance. Falls back to local SQLite when not set (e.g.
# running on your own machine without Postgres).
db_url = os.environ.get("DATABASE_URL", "sqlite:///siwes.db")

# Render (and Heroku) hand back "postgres://", but SQLAlchemy 1.4+/2.x
# requires "postgresql://" for the same connection string.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Database
db.init_app(app)


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
# Note: this only creates missing tables, it does not migrate
# existing ones. If you change a model's columns later, you'll
# need a real migration tool (e.g. Flask-Migrate) or to manually
# alter the table.
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    # debug=True is fine for local development but must never run
    # in production (it exposes the Werkzeug debugger, which allows
    # arbitrary code execution). On Render, gunicorn runs the app
    # instead of this block, so debug mode is never reached there.
    app.run(debug=True)