from flask import Blueprint

from smartyard.utils import access_verification, json_verification

geo_branch = Blueprint("geo", __name__, url_prefix="/geo")


@geo_branch.route("/address", methods=["POST"])
@access_verification
@json_verification
def address() -> str:
    return "Hello, World!"


@geo_branch.route("/coder", methods=["POST"])
@access_verification
@json_verification
def coder() -> str:
    return "Hello, World!"


@geo_branch.route("/getAllLocations", methods=["POST"])
@access_verification
@json_verification
def get_all_locations() -> str:
    return "Hello, World!"


@geo_branch.route("/getAllServices", methods=["POST"])
@access_verification
@json_verification
def get_all_services() -> str:
    return "Hello, World!"


@geo_branch.route("/getHouses", methods=["POST"])
@access_verification
@json_verification
def get_houses() -> str:
    return "Hello, World!"


@geo_branch.route("/getServices", methods=["POST"])
@access_verification
@json_verification
def get_services() -> str:
    return "Hello, World!"


@geo_branch.route("/getStreets", methods=["POST"])
@access_verification
@json_verification
def get_streets() -> str:
    return "Hello, World!"
