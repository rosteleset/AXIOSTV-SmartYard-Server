from flask import Blueprint, Response, jsonify

from smartyard.utils import access_verification, json_verification

inbox_branch = Blueprint("inbox", __name__, url_prefix="/inbox")


@inbox_branch.route("/alert", methods=["POST"])
@access_verification
@json_verification
def alert() -> str:
    return "Hello, World!"


@inbox_branch.route("/chatReaded", methods=["POST"])
@access_verification
@json_verification
def chat_readed() -> str:
    return "Hello, World!"


@inbox_branch.route("/delivered", methods=["POST"])
@access_verification
@json_verification
def delivered() -> str:
    return "Hello, World!"


@inbox_branch.route("/inbox", methods=["POST"])
@access_verification
def inbox() -> Response:
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {"count": 0, "chat": 0},
        }
    )


@inbox_branch.route("/readed", methods=["POST"])
@access_verification
@json_verification
def readed() -> str:
    return "Hello, World!"


@inbox_branch.route("/unreaded", methods=["POST"])
@access_verification
def unreaded() -> Response:
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {"count": 0, "chat": 0},
        }
    )
