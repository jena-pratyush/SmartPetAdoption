from datetime import datetime

from extensions import db


class Message(db.Model):

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    adoption_request_id = db.Column(
        db.Integer,
        db.ForeignKey("adoption_requests.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )


    # Sender
    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        backref="sent_messages"
    )


    # Receiver
    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        backref="received_messages"
    )


    # Adoption application
    adoption_request = db.relationship(
        "AdoptionRequest",
        backref="messages"
    )