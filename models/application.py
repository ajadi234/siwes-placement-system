from models.user import db


class Application(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    opportunity_id = db.Column(
        db.Integer,
        db.ForeignKey("opportunity.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    # Set by the student once they are accepted, to record
    # the actual start and end dates of their SIWES / internship
    # placement (3 months, 6 months, etc.)
    start_date = db.Column(
        db.Date,
        nullable=True
    )

    end_date = db.Column(
        db.Date,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # Relationship with Opportunity
    opportunity = db.relationship(
        "Opportunity",
        foreign_keys=[opportunity_id]
    )

    # Relationship with Student/User
    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )

    # Prevent same student from applying twice
    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "opportunity_id",
            name="unique_student_opportunity"
        ),
    )