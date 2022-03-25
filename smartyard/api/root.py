"""Модуль описания корневой ветки эндпойнтов API сервиса"""
from datetime import datetime, timedelta

from flask import Blueprint, Response, abort, current_app, request

from smartyard.logic.users_bank import UsersBank

root_branch = Blueprint("accessfl", __name__)


@root_branch.route("/")
def index() -> str:
    """Корневой эндпойнт"""
    return "Hello, World!"


@root_branch.route("/accessfl", methods=["GET"])
def accessfl() -> Response:
    """Проверка доступа к Flussonic"""
    token = request.args.get("token")
    name = request.args.get("name", 0)
    if not token:
        abort(403, {"code": 403, "name": "Forbidden", "message": "Нет токена"})

    extime = datetime.now() - timedelta(
        minutes=int(current_app.config["CONFIG"].EXPIRE)
    )
    users = [
        user
        for user in UsersBank().get_users_by_videotoken(token)
        if user and user.vttime >= extime and name in user.strims
    ]

    if not users:
        abort(403, {"code": 403, "name": "Forbidden", "message": "Неверный токен"})
    return Response(status=200)
