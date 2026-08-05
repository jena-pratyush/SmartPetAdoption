from flask import Blueprint, render_template

pets = Blueprint("pets", __name__)

@pets.route("/pets")
def list_pets():
    return render_template("pets/list.html")


@pets.route("/pets/add")
def add_pet():
    return render_template("pets/add.html")