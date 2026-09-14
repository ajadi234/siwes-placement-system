from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from datetime import timedelta

from models.user import db
from routes.auth import auth_bp
from utils.decorators import role_required

app = Flask(__name__)

# --- Config ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///siwes.db"  # swap for MySQL/Postgres in production
app.config["SECRET_KEY"] = "change-this-too-a-real-secret"  # used for password reset tokens
app.config["JWT_SECRET_KEY"] = "change-this-to-a-real-secret"  # load from .env in real app
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

db.init_app(app)
jwt = JWTManager(app)

# --- Register auth routes ---
app.register_blueprint(auth_bp)

# --- Example protected routes ---

# Any logged-in user (student, company, or admin) can view placements
@app.route("/api/placements", methods=["GET"])
@jwt_required()
def get_placements():
    claims = get_jwt()
    return jsonify({"message": f"Hello {claims.get('role')}, here are the placements."})


# Only admins/coordinators can approve a placement
@app.route("/api/placements/<int:placement_id>/approve", methods=["POST"])
@jwt_required()
@role_required("admin")
def approve_placement(placement_id):
    return jsonify({"message": f"Placement {placement_id} approved."})


# Only companies can post available slots
@app.route("/api/companies/slots", methods=["POST"])
@jwt_required()
@role_required("company")
def post_slot():
    return jsonify({"message": "Slot posted."})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables based on models
    app.run(debug=True)