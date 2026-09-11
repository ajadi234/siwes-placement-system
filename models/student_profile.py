from models.user import db


class StudentProfile(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    matric_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    university = db.Column(
        db.String(150),
        nullable=False
    )

    faculty = db.Column(
        db.String(150),
        nullable=False
    )

    department = db.Column(
        db.String(150),
        nullable=False
    )

    programme = db.Column(
        db.String(150),
        nullable=False
    )

    level = db.Column(
        db.String(20),
        nullable=False
    )

    cgpa = db.Column(
        db.Float,
        nullable=True
    )

    skills = db.Column(
        db.Text,
        nullable=True
    )

    preferred_state = db.Column(
        db.String(100),
        nullable=True
    )

    preferred_city = db.Column(
        db.String(100),
        nullable=True
    )

    def __repr__(self):

        return f"<StudentProfile {self.matric_number}>"