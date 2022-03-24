from flask import Blueprint, Response, abort, jsonify, request

from smartyard.utils import access_verification

inbox_branch = Blueprint("inbox", __name__, url_prefix="/inbox")


@inbox_branch.route("/alert", methods=["POST"])
def alert() -> str:
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


@inbox_branch.route("/chatReaded", methods=["POST"])
def chat_readed() -> str:
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


@inbox_branch.route("/delivered", methods=["POST"])
def delivered() -> str:
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


@inbox_branch.route("/inbox", methods=["POST"])
def inbox() -> Response:
    access_verification(request.headers)
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {"count": 0, "chat": 0},
        }
    )


@inbox_branch.route("/readed", methods=["POST"])
def readed() -> str:
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


@inbox_branch.route("/unreaded", methods=["POST"])
def unreaded() -> Response:
    access_verification(request.headers)
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {"count": 0, "chat": 0},
        }
    )
