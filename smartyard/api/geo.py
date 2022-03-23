from flask import Blueprint, abort, request

from smartyard.utils import access_verification

geo_branch = Blueprint("geo", __name__, url_prefix="/geo")


@geo_branch.route("/address", methods=["POST"])
def address():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request.get_json():
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@geo_branch.route("/coder", methods=["POST"])
def coder():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request.get_json():
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@geo_branch.route("/getAllLocations", methods=["POST"])
def get_all_locations():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request.get_json():
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@geo_branch.route("/getAllServices", methods=["POST"])
def get_all_services():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request.get_json():
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@geo_branch.route("/getHouses", methods=["POST"])
def get_houses():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request.get_json():
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@geo_branch.route("/getServices", methods=["POST"])
def get_services():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request.get_json():
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@geo_branch.route("/getStreets", methods=["POST"])
def get_streets():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request.get_json():
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"
