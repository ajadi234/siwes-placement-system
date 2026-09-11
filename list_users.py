"""
Run this to see exactly what's in your User table right now:

    python list_users.py
"""

from app import app
from models.user import User


with app.app_context():

    users = User.query.all()

    if not users:
        print("No users found in the database at all.")

    else:
        print(f"Found {len(users)} user(s):\n")

        for u in users:
            print(
                f"id={u.id}  "
                f"name={u.full_name!r}  "
                f"email={u.email!r}  "
                f"role={u.role!r}  "
                f"is_approved={u.is_approved}"
            )