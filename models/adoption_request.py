from extensions import db
from datetime import datetime


class AdoptionRequest(db.Model):
    """Represents an application made by a user to adopt a specific pet."""

    __tablename__ = "adoption_requests"

    id = db.Column(db.Integer, primary_key=True)

    # Pet being requested
    pet_id = db.Column(
        db.Integer,
        db.ForeignKey("pets.id"),
        nullable=False
    )

    # User applying for adoption
    adopter_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Application answers and questionnaires
    reason = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text)
    home_type = db.Column(db.String(100))
    family_members = db.Column(db.String(255))
    other_pets = db.Column(db.String(255))
    working_hours = db.Column(db.String(255))
    phone = db.Column(db.String(20))

    # Application status: 'Pending', 'Approved', 'Rejected'
    status = db.Column(
        db.String(20),
        default="Pending",
        nullable=False
    )

    # Timestamp of when the request was made
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Database relationships linking to related Pet and User objects
    pet = db.relationship(
        "Pet",
        backref="adoption_requests"
    )

    adopter = db.relationship(
        "User",
        backref="adoption_requests"
    )