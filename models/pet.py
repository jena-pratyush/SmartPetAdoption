from extensions import db


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=False)

    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)

    description = db.Column(db.Text)

    image = db.Column(
        db.String(255),
        default="default_pet.jpg"
    )

    status = db.Column(
        db.String(20),
        default="Available"
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    owner = db.relationship(
        "User",
        backref="pets",
        lazy=True
    )

    def __repr__(self):
        return f"<Pet {self.name}>"