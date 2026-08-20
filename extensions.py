from flask_sqlalchemy import SQLAlchemy

# Shared database instance to avoid circular imports
db = SQLAlchemy()