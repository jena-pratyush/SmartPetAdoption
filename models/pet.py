from extensions import db
from datetime import datetime


class Pet(db.Model):
    """Represents a pet listed for adoption on the platform."""
    
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)

    # Basic pet details
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)  # e.g., 'Dog', 'Cat'
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    description = db.Column(db.Text)
    
    # Filename of the uploaded image
    image = db.Column(db.String(255))

    # Adoption status: 'available' or 'adopted'
    status = db.Column(
        db.String(20),
        nullable=False,
        default="available"
    )

    # Owner/Lister of the pet (usually a User of role 'user' or 'shelter')
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Timestamp of when the pet was listed
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationship back to the owner/lister
    owner = db.relationship(
        "User",
        backref="pets"
    )

    def __repr__(self):
        return f"<Pet {self.name}>"