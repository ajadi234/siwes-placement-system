"""
Run this ONCE to create your first admin account:

    python create_admin.py

Edit the email/password/name below before running,
then you can delete this file (or keep it for later use).
"""

from werkzeug.security import generate_password_hash

from app import app
from models.user import db, User


ADMIN_FULL_NAME = "System Admin"
ADMIN_EMAIL = "admin@siwesconnect.com"
ADMIN_PASSWORD = "ChangeThisPassword123"


with app.app_context():

    existing = User.query.filter_by(email=ADMIN_EMAIL).first()

    if existing:
        print(f"An account with {ADMIN_EMAIL} already exists.")

    else:

        admin_user = User(
            full_name=ADMIN_FULL_NAME,
            email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD),
            role="admin",
            is_approved=True
        )

        db.session.add(admin_user)
        db.session.commit()

        print(f"Admin account created: {ADMIN_EMAIL}")
        print("You can now log in with this email and the password "
              "you set in this script.")