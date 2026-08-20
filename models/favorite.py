from extensions import db
from datetime import datetime


class Favorite(db.Model):
    """Represents a pet that has been bookmarked/favorited by a user."""

    __tablename__ = "favorites"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Reference to the user who favorited the pet
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Reference to the pet being favorited
    pet_id = db.Column(
        db.Integer,
        db.ForeignKey("pets.id"),
        nullable=False
    )

    # Timestamp of when the favorite was created
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Database relationships linking to related User and Pet objects
    user = db.relationship(
        "User",
        backref="favorites"
    )

    pet = db.relationship(
        "Pet",
        backref="favorited_by"
    )

    # Ensure a user can only favorite a specific pet once
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "pet_id",
            name="unique_user_pet_favorite"
        ),
    )