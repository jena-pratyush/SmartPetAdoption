from extensions import db
from datetime import datetime


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    species = db.Column(db.String(50), nullable=False)

    breed = db.Column(db.String(100))

    age = db.Column(db.Integer)

    gender = db.Column(db.String(20))

    description = db.Column(db.Text)

    image = db.Column(db.String(255))

    status = db.Column(
        db.String(20),
        nullable=False,
        default="available"
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    owner = db.relationship(
        "User",
        backref="pets"
    )

    def __repr__(self):
        return f"<Pet {self.name}>"