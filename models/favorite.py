from extensions import db
from datetime import datetime


class Favorite(db.Model):

    __tablename__ = "favorites"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey("pets.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="favorites"
    )

    pet = db.relationship(
        "Pet",
        backref="favorited_by"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "pet_id",
            name="unique_user_pet_favorite"
        ),
    )