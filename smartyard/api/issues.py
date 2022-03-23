from flask import Blueprint, Response, abort, request

from smartyard.utils import access_verification

issues_branch = Blueprint(url_prefix="/issues")


@issues_branch.route("/api/issues/action", methods=["POST"])
def issues_action():
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


@issues_branch.route("/api/issues/comment", methods=["POST"])
def issues_comment():
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


@issues_branch.route("/api/issues/create", methods=["POST"])
def issues_create():
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


@issues_branch.route("/api/issues/listConnect", methods=["POST"])
def issues_listConnect():
    access_verification(request.headers)
    return Response(status=204, mimetype="application/json")
