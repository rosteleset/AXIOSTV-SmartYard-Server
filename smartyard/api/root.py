from datetime import datetime, timedelta

from flask import Blueprint, Response, abort, current_app, request

from smartyard.logic.users_bank import UsersBank

root_branch = Blueprint("accessfl", __name__)


@root_branch.route("/")
def index():
    return "Hello, World!"


@root_branch.route("/accessfl", methods=["GET"])
def accessfl():
    token = request.args.get("token")
    name = request.args.get("name", 0)
    if not token:
        abort(403, {"code": 403, "name": "Forbidden", "message": "Нет токена"})

    extime = datetime.now() - timedelta(
        minutes=int(current_app.config["CONFIG"].EXPIRE)
    )
    for user in UsersBank.get_users_by_videotoken(token):
        if user and user.vttime >= extime and name in user.strims:
            return Response(status=200)

    abort(403, {"code": 403, "name": "Forbidden", "message": "Неверный токен"})
