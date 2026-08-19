from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session
)

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