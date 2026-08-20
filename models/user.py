from extensions import db
from datetime import datetime


class User(db.Model):
    """Represents a registered user in the application."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    # Email used as unique username/login credential
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Password stored as a secure hashed string
    password = db.Column(db.String(255), nullable=False)

    # Role of the user: 'admin', 'adopter', or 'shelter'
    role = db.Column(
        db.String(20),
        nullable=False,
        default="adopter"
    )

    phone = db.Column(db.String(20))

    # Timestamp of user registration
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.email}>"