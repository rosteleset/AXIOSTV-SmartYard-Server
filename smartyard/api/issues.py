from flask import Blueprint, Response, abort, request

from smartyard.utils import access_verification

issues_branch = Blueprint("issues", __name__, url_prefix="/issues")


@issues_branch.route("/action", methods=["POST"])
def action():
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


@issues_branch.route("/comment", methods=["POST"])
def comment():
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


@issues_branch.route("/create", methods=["POST"])
def create():
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


@issues_branch.route("/listConnect", methods=["POST"])
def list_connect():
    access_verification(request.headers)
    return Response(status=204, mimetype="application/json")
