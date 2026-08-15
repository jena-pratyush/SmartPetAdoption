from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app

import os
import uuid
from werkzeug.utils import secure_filename

from extensions import db
from models.pet import Pet


pets = Blueprint("pets", __name__)
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )

@pets.route("/pets")
def pet_list():

    all_pets = Pet.query.filter_by(status="available").all()

    return render_template(
        "pets/list.html",
        pets=all_pets
    )

@pets.route("/pets/<int:pet_id>")
def pet_details(pet_id):

    pet = Pet.query.get_or_404(pet_id)

    return render_template(
        "pets/details.html",
        pet=pet
    )

@pets.route("/pets/<int:pet_id>/edit", methods=["GET", "POST"])
def edit_pet(pet_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Only the owner who created the pet can edit it
    if pet.owner_id != session["user_id"]:
        flash("You are not allowed to edit this pet.", "danger")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))

    if request.method == "POST":

        pet.name = request.form["name"]
        pet.species = request.form["species"]
        pet.breed = request.form["breed"]
        pet.age = request.form["age"]
        pet.gender = request.form["gender"]
        pet.description = request.form["description"]

        db.session.commit()

        flash("Pet updated successfully!", "success")

        return redirect(
            url_for("pets.pet_details", pet_id=pet.id)
        )

    return render_template(
        "pets/edit.html",
        pet=pet
    )

@pets.route("/pets/<int:pet_id>/delete", methods=["POST"])
def delete_pet(pet_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Only the owner can delete the pet
    if pet.owner_id != session["user_id"]:
        flash("You are not allowed to delete this pet.", "danger")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))

    db.session.delete(pet)
    db.session.commit()

    flash("Pet deleted successfully.", "success")

    return redirect(url_for("pets.pet_list"))

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

        # Get uploaded image
        image = request.files.get("image")

        image_filename = None

        if image and image.filename:

            if not allowed_file(image.filename):
                flash(
                    "Invalid image type. Please upload JPG, JPEG, PNG, or WEBP.",
                    "danger"
                )
                return redirect(url_for("pets.add_pet"))

            extension = image.filename.rsplit(".", 1)[1].lower()

            image_filename = f"{uuid.uuid4().hex}.{extension}"

            image_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                image_filename
            )

            image.save(image_path)

        new_pet = Pet(
            name=name,
            species=species,
            breed=breed,
            age=age,
            gender=gender,
            description=description,
            image=image_filename,
            owner_id=session["user_id"]
        )

        db.session.add(new_pet)
        db.session.commit()

        flash("Pet added successfully!", "success")

        return redirect(url_for("pets.pet_list"))

    return render_template("pets/add.html")