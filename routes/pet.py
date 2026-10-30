from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
    send_from_directory
)

import os
import uuid

from extensions import db
from models.pet import Pet
from models.pet_document import PetDocument
from models.adoption_request import AdoptionRequest
from models.favorite import Favorite
from models.message import Message

# Blueprint for handling all pet-related interactions
pets = Blueprint("pets", __name__)


def allowed_file(filename):
    """Verify if the uploaded file has a permitted image extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def allowed_doc_file(filename):
    """Verify if the uploaded document has a permitted extension."""
    allowed = current_app.config.get(
        "ALLOWED_DOC_EXTENSIONS",
        {"pdf", "png", "jpg", "jpeg", "webp"}
    )
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed
    )


# =========================================================
# BROWSE PETS
# =========================================================

@pets.route("/pets")
def pet_list():
    """Display available pets with search and filtering options."""
    query = Pet.query.filter_by(status="available")

    q = request.args.get("q", "").strip()
    species = request.args.get("species", "").strip()
    gender = request.args.get("gender", "").strip()
    age_group = request.args.get("age_group", "").strip()
    city = request.args.get("city", "").strip()
    has_doc = request.args.get("has_doc", "").strip()

    if q:
        query = query.filter(
            db.or_(
                Pet.name.ilike(f"%{q}%"),
                Pet.breed.ilike(f"%{q}%"),
                Pet.city.ilike(f"%{q}%"),
                Pet.description.ilike(f"%{q}%")
            )
        )

    if species and species != "All":
        query = query.filter(Pet.species == species)

    if gender and gender != "All":
        query = query.filter(Pet.gender == gender)

    if city and city != "All":
        query = query.filter(Pet.city.ilike(f"%{city}%"))

    if age_group and age_group != "All":
        if age_group == "baby":
            # Under 1 year old
            query = query.filter(
                db.or_(
                    Pet.age_unit == "Months",
                    db.and_(Pet.age_unit == "Years", Pet.age == 0)
                )
            )
        elif age_group == "young":
            # 1 to 3 years
            query = query.filter(
                Pet.age_unit == "Years",
                Pet.age >= 1,
                Pet.age <= 3
            )
        elif age_group == "adult":
            # 4 to 7 years
            query = query.filter(
                Pet.age_unit == "Years",
                Pet.age >= 4,
                Pet.age <= 7
            )
        elif age_group == "senior":
            # 8+ years
            query = query.filter(
                Pet.age_unit == "Years",
                Pet.age >= 8
            )

    if has_doc == "1":
        query = query.filter(Pet.documents.any())

    all_pets = query.order_by(Pet.created_at.desc()).all()

    # Get distinct available cities for quick filter dropdown
    distinct_cities = [
        c[0] for c in db.session.query(Pet.city)
        .filter(Pet.status == "available", Pet.city.isnot(None), Pet.city != "")
        .distinct()
        .order_by(Pet.city.asc())
        .all()
    ]

    has_filters = bool(
        q
        or (species and species != "All")
        or (gender and gender != "All")
        or (age_group and age_group != "All")
        or (city and city != "All")
        or has_doc == "1"
    )

    return render_template(
        "pets/list.html",
        pets=all_pets,
        q=q,
        species=species,
        gender=gender,
        age_group=age_group,
        city=city,
        cities=distinct_cities,
        has_doc=has_doc,
        has_filters=has_filters
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
            f"Adoption request for {pet.name} approved! You can now chat with the adopter. If the adoption falls through, you can put {pet.name} back for adoption at any time.",
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
# RELIST PET FOR ADOPTION
# =========================================================

@pets.route("/pets/<int:pet_id>/relist", methods=["POST"])
def relist_pet(pet_id):
    """Put an adopted or pending pet back up for adoption."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Security check: Only the pet owner or admin can relist
    if pet.owner_id != session["user_id"] and session.get("role") != "admin":
        flash("You are not allowed to manage this pet.", "danger")
        return redirect(url_for("pets.my_pets"))

    pet.status = "available"
    db.session.commit()

    flash(
        f"{pet.name} is now back up for adoption and visible to all adopters!",
        "success"
    )

    return redirect(request.referrer or url_for("pets.my_pets"))


# =========================================================
# CANCEL ADOPTION APPLICATION
# =========================================================

@pets.route(
    "/applications/<int:request_id>/cancel-adoption",
    methods=["POST"]
)
def cancel_adoption(request_id):
    """Cancel an approved adoption application and put the pet back up for adoption."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    adoption_request = AdoptionRequest.query.get_or_404(request_id)
    pet = Pet.query.get_or_404(adoption_request.pet_id)

    # Security check: Only the pet owner or admin can cancel the adoption
    if pet.owner_id != session["user_id"] and session.get("role") != "admin":
        flash("You are not allowed to manage this application.", "danger")
        return redirect(url_for("pets.applications"))

    adoption_request.status = "Cancelled"
    pet.status = "available"
    db.session.commit()

    flash(
        f"Adoption for {pet.name} has been cancelled. {pet.name} is now back up for adoption!",
        "info"
    )

    return redirect(url_for("pets.applications"))



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
        pet.city = request.form.get("city", "").strip()
        age_val = request.form.get("age", "").strip()
        pet.age = int(age_val) if age_val.isdigit() else None
        pet.age_unit = request.form.get("age_unit", "Years")
        pet.gender = request.form["gender"]
        pet.description = request.form["description"]
        pet.pet_source = request.form.get("pet_source", pet.pet_source or "Not Specified")
        pet.vaccination_status = request.form.get("vaccination_status", pet.vaccination_status or "Not Specified")

        # Optional new image upload
        image = request.files.get("image")
        if image and image.filename:
            if allowed_file(image.filename):
                if pet.image:
                    old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], pet.image)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except OSError:
                            pass
                ext = image.filename.rsplit(".", 1)[1].lower()
                image_filename = f"{uuid.uuid4().hex}.{ext}"
                image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], image_filename))
                pet.image = image_filename

        # Optional new document(s) upload
        doc_files = request.files.getlist("documents")
        single_doc = request.files.get("document")
        if single_doc and single_doc.filename and single_doc not in doc_files:
            doc_files.append(single_doc)

        doc_type = request.form.get("doc_type", "General Document")
        for doc_file in doc_files:
            if doc_file and doc_file.filename:
                if not allowed_doc_file(doc_file.filename):
                    flash(
                        f"Skipped document '{doc_file.filename}': invalid type. Allowed: PDF, JPG, PNG, WEBP.",
                        "warning"
                    )
                    continue
                ext = doc_file.filename.rsplit(".", 1)[1].lower()
                doc_filename = f"doc_{uuid.uuid4().hex}.{ext}"
                doc_path = os.path.join(current_app.config["UPLOAD_FOLDER"], doc_filename)
                doc_file.save(doc_path)

                new_doc = PetDocument(
                    pet_id=pet.id,
                    filename=doc_filename,
                    original_filename=doc_file.filename,
                    doc_type=doc_type
                )
                db.session.add(new_doc)

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
    """Delete a pet listing and its uploaded files (owner only)."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)

    # Security check: Only the listing creator or admin can delete
    if pet.owner_id != session["user_id"] and session.get("role") != "admin":
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

    # Remove image file if it exists
    if pet.image:
        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            pet.image
        )
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass

    # Remove all uploaded document files for this pet
    for doc in pet.documents:
        doc_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            doc.filename
        )
        if os.path.exists(doc_path):
            try:
                os.remove(doc_path)
            except OSError:
                pass

    db.session.delete(pet)
    db.session.commit()

    flash(
        "Pet deleted successfully.",
        "success"
    )

    # Redirect admin back to admin panel, owner back to their pets
    if session.get("role") == "admin":
        return redirect(url_for("admin.manage_pets"))

    return redirect(
        url_for("pets.my_pets")
    )


# =========================================================
# PET DOCUMENTS (DOWNLOAD & DELETE)
# =========================================================

@pets.route(
    "/pets/<int:pet_id>/document/<int:doc_id>/delete",
    methods=["POST"]
)
def delete_document(pet_id, doc_id):
    """Delete an individual document attached to a pet (owner only)."""
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    pet = Pet.query.get_or_404(pet_id)
    if pet.owner_id != session["user_id"]:
        flash("You are not allowed to delete documents for this pet.", "danger")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))

    doc = PetDocument.query.filter_by(id=doc_id, pet_id=pet.id).first_or_404()
    doc_path = os.path.join(current_app.config["UPLOAD_FOLDER"], doc.filename)
    if os.path.exists(doc_path):
        try:
            os.remove(doc_path)
        except OSError:
            pass

    db.session.delete(doc)
    db.session.commit()

    flash(f"Document '{doc.original_filename}' deleted.", "info")
    return redirect(url_for("pets.edit_pet", pet_id=pet.id))


@pets.route("/pets/document/<int:doc_id>/download")
def download_document(doc_id):
    """Download an uploaded pet document with its original filename."""
    doc = PetDocument.query.get_or_404(doc_id)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        doc.filename,
        as_attachment=True,
        download_name=doc.original_filename
    )


# =========================================================
# ADD PET
# =========================================================

@pets.route(
    "/pets/add",
    methods=["GET", "POST"]
)
def add_pet():
    """Create and publish a new pet listing with optional image and documents."""
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
        city = request.form.get("city", "").strip()
        age_val = request.form.get("age", "").strip()
        age = int(age_val) if age_val.isdigit() else None
        age_unit = request.form.get("age_unit", "Years")
        gender = request.form["gender"]
        description = request.form["description"]
        pet_source = request.form.get("pet_source", "Not Specified")
        vaccination_status = request.form.get("vaccination_status", "Not Specified")

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
            city=city,
            age=age,
            age_unit=age_unit,
            gender=gender,
            description=description,
            pet_source=pet_source,
            vaccination_status=vaccination_status,
            image=image_filename,
            owner_id=session["user_id"]
        )

        db.session.add(new_pet)
        db.session.flush()

        # Handle optional document uploads (certificates, paperwork)
        doc_files = request.files.getlist("documents")
        single_doc = request.files.get("document")
        if single_doc and single_doc.filename and single_doc not in doc_files:
            doc_files.append(single_doc)

        doc_type = request.form.get("doc_type", "General Document")
        for doc_file in doc_files:
            if doc_file and doc_file.filename:
                if not allowed_doc_file(doc_file.filename):
                    flash(
                        f"Skipped document '{doc_file.filename}': invalid type. Allowed: PDF, JPG, PNG, WEBP.",
                        "warning"
                    )
                    continue
                ext = doc_file.filename.rsplit(".", 1)[1].lower()
                doc_filename = f"doc_{uuid.uuid4().hex}.{ext}"
                doc_path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    doc_filename
                )
                doc_file.save(doc_path)

                new_doc = PetDocument(
                    pet_id=new_pet.id,
                    filename=doc_filename,
                    original_filename=doc_file.filename,
                    doc_type=doc_type
                )
                db.session.add(new_doc)

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


# =========================================================
# CHAT
# =========================================================

@pets.route("/chat/<int:request_id>")
def chat(request_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    adoption_request = AdoptionRequest.query.get_or_404(request_id)

    pet = Pet.query.get_or_404(
        adoption_request.pet_id
    )

    current_user_id = session["user_id"]

    # Chat is available after approval or if previously approved/cancelled
    if adoption_request.status not in ["Approved", "Cancelled"]:
        flash(
            "Chat is available only after the adoption is approved.",
            "warning"
        )
        return redirect(
            url_for("pets.my_applications")
        )

    # Only the pet owner or approved adopter can access chat
    if (
        current_user_id != adoption_request.adopter_id
        and current_user_id != pet.owner_id
    ):
        flash(
            "You are not allowed to access this chat.",
            "danger"
        )
        return redirect(
            url_for("pets.pet_list")
        )

    messages = (
        Message.query
        .filter_by(
            adoption_request_id=adoption_request.id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    # Mark received messages as read
    for message in messages:

        if (
            message.receiver_id == current_user_id
            and not message.is_read
        ):
            message.is_read = True

    db.session.commit()

    return render_template(
        "pets/chat.html",
        adoption_request=adoption_request,
        pet=pet,
        messages=messages
    )


@pets.route(
    "/chat/<int:request_id>/send",
    methods=["POST"]
)
def send_message(request_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    adoption_request = AdoptionRequest.query.get_or_404(
        request_id
    )

    pet = Pet.query.get_or_404(
        adoption_request.pet_id
    )

    current_user_id = session["user_id"]

    # Chat only after approval
    if adoption_request.status != "Approved":
        flash(
            "Chat is closed because this adoption is no longer active.",
            "warning"
        )
        return redirect(
            url_for(
                "pets.chat",
                request_id=request_id
            )
        )

    # Only owner or adopter can send messages
    if (
        current_user_id != adoption_request.adopter_id
        and current_user_id != pet.owner_id
    ):
        flash(
            "You are not allowed to send messages here.",
            "danger"
        )
        return redirect(
            url_for("pets.pet_list")
        )

    message_text = request.form.get(
        "message",
        ""
    ).strip()

    if not message_text:

        flash(
            "Message cannot be empty.",
            "warning"
        )

        return redirect(
            url_for(
                "pets.chat",
                request_id=request_id
            )
        )

    # Determine the other person
    if current_user_id == pet.owner_id:

        receiver_id = adoption_request.adopter_id

    else:

        receiver_id = pet.owner_id

    new_message = Message(
        sender_id=current_user_id,
        receiver_id=receiver_id,
        adoption_request_id=adoption_request.id,
        message=message_text
    )

    db.session.add(new_message)
    db.session.commit()

    return redirect(
        url_for(
            "pets.chat",
            request_id=request_id
        )
    )