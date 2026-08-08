from flask import Flask, render_template, session, redirect
from config import Config
from extensions import db
from models import User
from models.pet import Pet

from routes.auth import auth
from routes.pet import pets


app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(pets)

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


# Create database tables
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)