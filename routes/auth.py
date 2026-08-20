from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db
from models.user import User


# Blueprint for authentication-related routes
auth = Blueprint("auth", __name__)


# =========================================================
# REGISTER
# =========================================================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # Basic validation
        if not full_name or not email or not password:

            flash(
                "Please fill in all required fields.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # Ensure passwords match
        if password != confirm_password:

            flash(
                "Passwords do not match!",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # Prevent duplicate email registration
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered!",
                "warning"
            )

            return redirect(
                url_for("auth.register")
            )

        # Generate secure password hash
        hashed_password = generate_password_hash(
            password
        )

        # Every new account is a normal user
        # Admin accounts are created separately
        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password=hashed_password,
            role="user"
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful! Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            # Clear any previous session data
            session.clear()

            # Create fresh session
            session["user_id"] = user.id
            session["user_name"] = user.full_name
            session["role"] = user.role

            flash(
                "Login successful!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password!",
            "danger"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )