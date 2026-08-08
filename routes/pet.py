from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from extensions import db
from models.pet import Pet

pets = Blueprint("pets", __name__)


@pets.route("/pets")
def pet_list():

    all_pets = Pet.query.filter_by(status="available").all()

    return render_template(
        "pets/list.html",
        pets=all_pets
    )


@pets.route("/pets/add", methods=["GET", "POST"])
def add_pet():

    # User must be logged in
    if "user_id" not in session:
        flash("Please login to add a pet.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        name = request.form["name"]
        species = request.form["species"]
        breed = request.form["breed"]
        age = request.form["age"]
        gender = request.form["gender"]
        description = request.form["description"]

        new_pet = Pet(
            name=name,
            species=species,
            breed=breed,
            age=age,
            gender=gender,
            description=description,
            owner_id=session["user_id"]
        )

        db.session.add(new_pet)
        db.session.commit()

        flash("Pet added successfully!", "success")

        return redirect(url_for("pets.pet_list"))

    return render_template("pets/add.html")