from flask import Blueprint, Response, abort, request

from smartyard.utils import access_verification

sip_branch = Blueprint("sip", __name__, url_prefix="/sip")


@sip_branch.route("/helpMe", methods=["POST"])
def help_me():
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
