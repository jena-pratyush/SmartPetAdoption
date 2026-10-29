from extensions import db
from datetime import datetime, timezone
import os


class PetDocument(db.Model):
    """Represents a legal document, certificate, or medical paperwork for a pet."""

    __tablename__ = "pet_documents"

    id = db.Column(db.Integer, primary_key=True)

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey("pets.id"),
        nullable=False
    )

    # Stored unique filename on disk
    filename = db.Column(db.String(255), nullable=False)

    # Human-friendly original filename provided by user during upload
    original_filename = db.Column(db.String(255), nullable=False)

    # Category of document, e.g. "Vaccination Certificate", "Ownership / Transfer Papers"
    doc_type = db.Column(db.String(100), default="General Document")

    uploaded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    pet = db.relationship(
        "Pet",
        backref=db.backref(
            "documents",
            cascade="all, delete-orphan",
            order_by="PetDocument.uploaded_at.desc()"
        )
    )

    @property
    def is_pdf(self):
        """Check if the document is a PDF."""
        return self.filename.lower().endswith(".pdf")

    @property
    def file_extension(self):
        """Get file extension without dot."""
        _, ext = os.path.splitext(self.filename)
        return ext.lstrip(".").lower()

    def __repr__(self):
        return f"<PetDocument {self.original_filename} ({self.doc_type})>"
