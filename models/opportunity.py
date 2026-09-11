from models.user import db


class Opportunity(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    requirements = db.Column(
        db.Text,
        nullable=True
    )

    location = db.Column(
        db.String(150),
        nullable=False
    )

    state = db.Column(
        db.String(100),
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )

    duration = db.Column(
        db.String(100),
        nullable=False
    )

    opportunity_type = db.Column(
        db.String(50),
        nullable=False
    )

    application_deadline = db.Column(
        db.String(50),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f"<Opportunity {self.title}>"