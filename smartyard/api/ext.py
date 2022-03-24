from flask import Blueprint, abort, request

from smartyard.utils import access_verification

ext_branch = Blueprint("ext", __name__, url_prefix="/ext")


@ext_branch.route("/ext", methods=["POST"])
def ext() -> str:
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


@ext_branch.route("/list", methods=["POST"])
def list() -> str:
    access_verification(request.headers)

    request_data = request.get_json()
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
