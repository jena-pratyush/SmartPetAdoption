from flask import Flask, render_template, session, redirect, send_from_directory
from config import Config
from extensions import db
from models import User
from models.pet import Pet

from routes.auth import auth
from routes.pet import pets
from routes.admin import admin

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(pets)
app.register_blueprint(admin)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


# Serve uploaded pet images
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# Create database tables
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)