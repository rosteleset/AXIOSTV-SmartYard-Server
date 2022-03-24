from flask import Blueprint, abort, request

from smartyard.utils import access_verification

frs_branch = Blueprint("frs", __name__, url_prefix="/frs")


@frs_branch.route("/disLike", methods=["POST"])
def dislike() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@frs_branch.route("/like", methods=["POST"])
def like() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@frs_branch.route("/listFaces", methods=["POST"])
def list_faces() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"
