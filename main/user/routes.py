from flask import Blueprint
from flask import current_app as app

from main.user.models import User
from utils.auth_utils import token_required

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/profile", methods=["GET"])
@token_required
def get():
    return User().get()


@user_blueprint.route("/auth", methods=["GET"])
@token_required
def getAuth():
    return User().getAuth()


@user_blueprint.route("/login", methods=["POST"])
def login():
    return User().login()


@user_blueprint.route("/logout", methods=["GET"])
@token_required
def logout():
    return User().logout()


@user_blueprint.route("/create", methods=["POST"])
def add():
    return User().add()
