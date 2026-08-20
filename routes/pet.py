from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

import os
import uuid

from extensions import db
from models.pet import Pet
from models.adoption_request import AdoptionRequest
from models.favorite import Favorite

# Blueprint for handling all pet-related interactions
pets = Blueprint("pets", __name__)


def allowed_file(filename):
    """Verify if the uploaded file has a permitted extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


# =========================================================
# BROWSE PETS
# =========================================================

@pets.route("/pets")
def pet_list():
    """Display all pets currently available for adoption."""
    all_pets = Pet.query.filter_by(status="available").all()

    return render_template(
        "pets/list.html",
        pets=all_pets
    )


# =========================================================
# PET DETAILS
# =========================================================

@pets.route("/pets/<int:pet_id>")
def pet_details(pet_id):
    """Display comprehensive information about a specific pet."""
    pet = Pet.query.get_or_404(pet_id)

    return render_template(
        "pets/details.html",
        pet=pet
    )


# =========================================================
# FAVORITE / UNFAVORITE PET
# =========================================================

@pets.route("/pets/<int:pet_id>/favorite", methods=["POST"])
def toggle_favorite(pet_id):
    """Add or remove a pet from the user's favorites list."""
    if "user_id" not in session:
        flash("Please login to favorite a pet.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Ensure users cannot bookmark their own listings
    if pet.owner_id == session["user_id"]:
        flash("You cannot favorite your own pet.", "warning")
        return redirect(
            url_for("pets.pet_details", pet_id=pet.id)
        )

    existing_favorite = Favorite.query.filter_by(
        user_id=session["user_id"],
        pet_id=pet.id
    ).first()

    if existing_favorite:
        # If already favorited, remove bookmark
        db.session.delete(existing_favorite)
        db.session.commit()

        flash(
            f"{pet.name} removed from your favorites.",
            "info"
        )
    else:
        # Otherwise, add a new bookmark
        new_favorite = Favorite(
            user_id=session["user_id"],
            pet_id=pet.id
        )

        db.session.add(new_favorite)
        db.session.commit()

        flash(
            f"{pet.name} added to your favorites! ❤️",
            "success"
        )

    return redirect(
        url_for("pets.pet_details", pet_id=pet.id)
    )


# =========================================================
# MY FAVORITES
# =========================================================

@pets.route("/my-favorites")
def my_favorites():
    """Display a list of all pets favorited by the logged-in user."""
    if "user_id" not in session:
        flash(
            "Please login to view your favorites.",
            "warning"
        )
        return redirect(url_for("auth.login"))

    favorites = (
        Favorite.query
        .filter_by(user_id=session["user_id"])
        .order_by(Favorite.created_at.desc())
        .all()
    )

    return render_template(
        "pets/my_favorites.html",
        favorites=favorites
    )


# =========================================================
# MY PETS
# =========================================================

@pets.route("/my-pets")
def my_pets():
    """Display a list of pets posted/owned by the logged-in user."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pets_owned = (
        Pet.query
        .filter_by(owner_id=session["user_id"])
        .order_by(Pet.created_at.desc())
        .all()
    )

    return render_template(
        "pets/my_pets.html",
        pets=pets_owned
    )


# =========================================================
# APPLY FOR ADOPTION
# =========================================================

@pets.route(
    "/pets/<int:pet_id>/apply",
    methods=["GET", "POST"]
)
def apply_for_adoption(pet_id):
    """Handle the submission of an adoption request for a pet."""
    if "user_id" not in session:
        flash(
            "Please login to apply for adoption.",
            "warning"
        )
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Validate that user is not listing their own pet for adoption to themselves
    if pet.owner_id == session["user_id"]:
        flash(
            "You cannot apply to adopt your own pet.",
            "danger"
        )
        return redirect(
            url_for("pets.pet_details", pet_id=pet.id)
        )

    # Ensure pet status is still open for adoption
    if pet.status != "available":
        flash(
            "This pet is no longer available for adoption.",
            "warning"
        )
        return redirect(
            url_for("pets.pet_details", pet_id=pet.id)
        )

    if request.method == "POST":
        reason = request.form["reason"]
        experience = request.form.get("experience")
        home_type = request.form.get("home_type")
        family_members = request.form.get("family_members")
        other_pets = request.form.get("other_pets")
        working_hours = request.form.get("working_hours")
        phone = request.form["phone"]

        new_request = AdoptionRequest(
            pet_id=pet.id,
            adopter_id=session["user_id"],
            reason=reason,
            experience=experience,
            home_type=home_type,
            family_members=family_members,
            other_pets=other_pets,
            working_hours=working_hours,
            phone=phone
        )

        db.session.add(new_request)
        db.session.commit()

        flash(
            "Adoption request submitted successfully!",
            "success"
        )

        return redirect(
            url_for("pets.pet_details", pet_id=pet.id)
        )

    return render_template(
        "pets/apply.html",
        pet=pet
    )


# =========================================================
# ADOPTION APPLICATIONS FOR MY PETS
# =========================================================

@pets.route("/applications")
def applications():
    """Display incoming adoption applications for the user's listed pets."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    requests = (
        AdoptionRequest.query
        .join(Pet)
        .filter(
            Pet.owner_id == session["user_id"]
        )
        .order_by(
            AdoptionRequest.created_at.desc()
        )
        .all()
    )

    return render_template(
        "pets/applications.html",
        requests=requests
    )


# =========================================================
# APPROVE / REJECT APPLICATION
# =========================================================

@pets.route(
    "/applications/<int:request_id>/<action>",
    methods=["POST"]
)
def update_application(request_id, action):
    """Process an adoption application by approving or rejecting it."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    adoption_request = (
        AdoptionRequest.query.get_or_404(request_id)
    )

    pet = Pet.query.get_or_404(
        adoption_request.pet_id
    )

    # Security check: Only the pet owner can manage its applications
    if pet.owner_id != session["user_id"]:
        flash(
            "You are not allowed to manage this application.",
            "danger"
        )
        return redirect(
            url_for("pets.applications")
        )

    # Ensure application has not been processed yet
    if adoption_request.status != "Pending":
        flash(
            "This application has already been processed.",
            "warning"
        )
        return redirect(
            url_for("pets.applications")
        )

    if action == "approve":
        adoption_request.status = "Approved"

        # Update pet status to adopted when request is approved
        pet.status = "adopted"
        db.session.commit()

        flash(
            f"Adoption request for {pet.name} approved!",
            "success"
        )

    elif action == "reject":
        adoption_request.status = "Rejected"
        db.session.commit()

        flash(
            "Adoption request rejected.",
            "info"
        )
    else:
        flash(
            "Invalid action.",
            "danger"
        )

    return redirect(
        url_for("pets.applications")
    )


# =========================================================
# MY APPLICATIONS
# =========================================================

@pets.route("/my-applications")
def my_applications():
    """Display applications submitted by the logged-in user."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    requests = (
        AdoptionRequest.query
        .filter_by(
            adopter_id=session["user_id"]
        )
        .order_by(
            AdoptionRequest.created_at.desc()
        )
        .all()
    )

    return render_template(
        "pets/my_applications.html",
        requests=requests
    )


# =========================================================
# EDIT PET
# =========================================================

@pets.route(
    "/pets/<int:pet_id>/edit",
    methods=["GET", "POST"]
)
def edit_pet(pet_id):
    """Modify details of an existing pet listing (owner only)."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Security check: Ensure only the creator of the listing can edit
    if pet.owner_id != session["user_id"]:
        flash(
            "You are not allowed to edit this pet.",
            "danger"
        )
        return redirect(
            url_for(
                "pets.pet_details",
                pet_id=pet.id
            )
        )

    if request.method == "POST":
        pet.name = request.form["name"]
        pet.species = request.form["species"]
        pet.breed = request.form["breed"]
        pet.age = request.form["age"]
        pet.gender = request.form["gender"]
        pet.description = request.form["description"]

        db.session.commit()

        flash(
            "Pet updated successfully!",
            "success"
        )

        return redirect(
            url_for(
                "pets.pet_details",
                pet_id=pet.id
            )
        )

    return render_template(
        "pets/edit.html",
        pet=pet
    )


# =========================================================
# DELETE PET
# =========================================================

@pets.route(
    "/pets/<int:pet_id>/delete",
    methods=["POST"]
)
def delete_pet(pet_id):
    """Delete a pet listing from the platform (owner only)."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Security check: Ensure only the listing creator can delete
    if pet.owner_id != session["user_id"]:
        flash(
            "You are not allowed to delete this pet.",
            "danger"
        )
        return redirect(
            url_for(
                "pets.pet_details",
                pet_id=pet.id
            )
        )

    db.session.delete(pet)
    db.session.commit()

    flash(
        "Pet deleted successfully.",
        "success"
    )

    return redirect(
        url_for("pets.pet_list")
    )


# =========================================================
# ADD PET
# =========================================================

@pets.route(
    "/pets/add",
    methods=["GET", "POST"]
)
def add_pet():
    """Create and publish a new pet listing with optional image upload."""
    if "user_id" not in session:
        flash(
            "Please login to add a pet.",
            "warning"
        )
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form["name"]
        species = request.form["species"]
        breed = request.form["breed"]
        age = request.form["age"]
        gender = request.form["gender"]
        description = request.form["description"]

        # Handle file upload for the pet image
        image = request.files.get("image")
        image_filename = None

        if image and image.filename:
            if not allowed_file(image.filename):
                flash(
                    "Invalid image type. Please upload JPG, JPEG, PNG, or WEBP.",
                    "danger"
                )
                return redirect(
                    url_for("pets.add_pet")
                )

            # Generate unique filename using UUID to prevent collisions
            extension = (
                image.filename
                .rsplit(".", 1)[1]
                .lower()
            )
            image_filename = (
                f"{uuid.uuid4().hex}.{extension}"
            )

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

        flash(
            "Pet added successfully!",
            "success"
        )

        return redirect(
            url_for("pets.pet_list")
        )

    return render_template(
        "pets/add.html"
    )