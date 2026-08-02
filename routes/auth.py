from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from extensions import db
from models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        # Check passwords
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.register"))

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered!", "warning")
            return redirect(url_for("auth.register"))

        # Hash password
        hashed_password = generate_password_hash(password)

        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login")
def login():
    return render_template("login.html")