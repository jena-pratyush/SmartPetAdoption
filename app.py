from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize Flask
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Run the application
if __name__ == "__main__":
    app.run(debug=True)