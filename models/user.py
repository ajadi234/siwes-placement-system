from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    # Companies must be approved by an admin before they can
    # post opportunities. Students and admins are approved
    # by default.
    is_approved = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    student_profile = db.relationship(
        "StudentProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):

        return f"<User {self.email}>"