from models.user import db


class CompanyProfile(db.Model):

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

    organization_name = db.Column(
        db.String(150),
        nullable=False
    )

    organization_type = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    address = db.Column(
        db.String(250),
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

    website = db.Column(
        db.String(200),
        nullable=True
    )

    contact_person = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    def __repr__(self):
        return f"<CompanyProfile {self.organization_name}>"