from extensions import db
from datetime import datetime, timezone


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
        default=lambda: datetime.now(timezone.utc)
    )

    # Database relationships linking to related User and Pet objects
    user = db.relationship(
        "User",
        backref=db.backref("favorites", cascade="all, delete-orphan")
    )

    pet = db.relationship(
        "Pet",
        backref=db.backref("favorited_by", cascade="all, delete-orphan")
    )

    # Ensure a user can only favorite a specific pet once
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "pet_id",
            name="unique_user_pet_favorite"
        ),
    )