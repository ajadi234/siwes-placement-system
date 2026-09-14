from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models.user import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

RESET_TOKEN_MAX_AGE = 1800  # 30 minutes, in seconds
RESET_SALT = "password-reset-salt"


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=RESET_SALT)


def verify_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt=RESET_SALT, max_age=RESET_TOKEN_MAX_AGE)
    except (SignatureExpired, BadSignature):
        return None
    return email


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")
    matric_number = data.get("matric_number")
    company_name = data.get("company_name")

    if not name or not email or not password:
        return jsonify({"message": "Name, email and password are required."}), 400

    if role not in ("student", "company", "admin"):
        return jsonify({"message": "Invalid role."}), 400

    existing_user = User.query.filter_by(email=email.lower()).first()
    if existing_user:
        return jsonify({"message": "An account with this email already exists."}), 409

    new_user = User(
        name=name,
        email=email.lower(),
        role=role,
        matric_number=matric_number,
        company_name=company_name,
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(
        identity=str(new_user.id),
        additional_claims={"role": new_user.role},
    )

    return jsonify({
        "message": "Account created successfully.",
        "token": access_token,
        "user": new_user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email.lower()).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password."}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )

    return jsonify({
        "message": "Login successful.",
        "token": access_token,
        "user": user.to_dict(),
    }), 200


# -------------------- FORGOT PASSWORD --------------------
# POST /api/auth/forgot-password
# Body: { "email": "student@example.com" }
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required."}), 400

    user = User.query.filter_by(email=email.lower()).first()

    # Always return the same message whether or not the user exists.
    # This prevents attackers from using this endpoint to check which emails are registered.
    generic_response = {
        "message": "If an account with that email exists, a password reset link has been sent."
    }

    if not user:
        return jsonify(generic_response), 200

    token = generate_reset_token(user.email)
    reset_link = f"https://your-frontend-domain.com/reset-password/{token}"

    # TODO: replace this with real email sending (e.g. Flask-Mail, SendGrid, etc.)
    # send_email(to=user.email, subject="Reset your password", body=f"Click here: {reset_link}")
    current_app.logger.info(f"[DEV ONLY] Password reset link for {user.email}: {reset_link}")

    return jsonify(generic_response), 200


# -------------------- RESET PASSWORD --------------------
# POST /api/auth/reset-password/<token>
# Body: { "new_password": "..." }
@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    data = request.get_json() or {}
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"message": "New password is required."}), 400

    email = verify_reset_token(token)
    if not email:
        return jsonify({"message": "This reset link is invalid or has expired."}), 400

    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        return jsonify({"message": "This reset link is invalid or has expired."}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password has been reset successfully. You can now log in."}), 200