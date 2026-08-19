from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session
)
from extensions import db

from models.user import User
from models.pet import Pet
from models.adoption_request import AdoptionRequest


admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return False

    if session.get("role") != "admin":
        flash("Admin access required.", "danger")
        return False

    return True


@admin.route("/")
def admin_dashboard():

    if not admin_required():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return redirect(url_for("dashboard"))

    user_count = User.query.count()
    pet_count = Pet.query.count()
    application_count = AdoptionRequest.query.count()

    available_pets = Pet.query.filter_by(
        status="available"
    ).count()

    adopted_pets = Pet.query.filter_by(
        status="adopted"
    ).count()

    pending_applications = AdoptionRequest.query.filter_by(
        status="Pending"
    ).count()

    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        pet_count=pet_count,
        application_count=application_count,
        available_pets=available_pets,
        adopted_pets=adopted_pets,
        pending_applications=pending_applications
    )

@admin.route("/users")
def manage_users():

    if not admin_required():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return redirect(url_for("dashboard"))

    users = (
        User.query
        .order_by(User.id.asc())
        .all()
    )

    return render_template(
        "admin/users.html",
        users=users
    )

@admin.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):

    if not admin_required():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return redirect(url_for("dashboard"))

    user = User.query.get_or_404(user_id)

    # Admin cannot delete their own account
    if user.id == session["user_id"]:
        flash("You cannot delete your own admin account.", "danger")
        return redirect(url_for("admin.manage_users"))

    db.session.delete(user)
    db.session.commit()

    flash(
        f"User {user.full_name} deleted successfully.",
        "success"
    )

    return redirect(url_for("admin.manage_users"))

@admin.route("/pets")
def manage_pets():

    if not admin_required():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return redirect(url_for("dashboard"))

    pets = (
        Pet.query
        .order_by(Pet.id.desc())
        .all()
    )

    return render_template(
        "admin/pets.html",
        pets=pets
    )

@admin.route("/pets/<int:pet_id>/delete", methods=["POST"])
def delete_pet(pet_id):

    if not admin_required():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return redirect(url_for("dashboard"))

    pet = Pet.query.get_or_404(pet_id)

    db.session.delete(pet)
    db.session.commit()

    flash(
        f"{pet.name} deleted successfully.",
        "success"
    )

    return redirect(url_for("admin.manage_pets"))

@admin.route("/applications")
def manage_applications():

    if not admin_required():

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return redirect(url_for("dashboard"))

    requests = (
        AdoptionRequest.query
        .order_by(AdoptionRequest.created_at.desc())
        .all()
    )

    return render_template(
        "admin/applications.html",
        requests=requests
    )