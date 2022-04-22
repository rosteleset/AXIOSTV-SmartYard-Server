"""Модуль описания корневой ветки эндпойнтов API сервиса"""
from datetime import datetime, timedelta

from flask import Blueprint, Response, abort, current_app, request

from smartyard.logic.users import Users

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
    session = current_app.extensions["sqlalchemy"].db.create_scoped_session()
    user = Users(session).user_by_video_token(token)

    if (
        not user
        or not user.vttime
        or extime > user.vttime
        or not user.strims
        or name not in user.strims
    ):
        abort(403, {"code": 403, "name": "Forbidden", "message": "Неверный токен"})
    return Response(status=200)
