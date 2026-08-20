import os
from dotenv import load_dotenv

# Load environment variables from a local .env file
load_dotenv()

class Config:
    """Application configuration settings parsed from environment variables."""
    
    # Secret key for signing sessions and cookies
    SECRET_KEY = os.getenv("SECRET_KEY")

    # SQLAlchemy database connection string for MySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    # Disable modification tracking overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directory path to store uploaded pet photos
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "uploads"
    )

    # Limit file upload size to 5MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Allowed file extensions for pet image uploads
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}