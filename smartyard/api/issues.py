"""Модуль описания эндпойнтов ветки /issues API"""
from flask import Blueprint, Response

from smartyard.utils import access_verification, json_verification

issues_branch = Blueprint("issues", __name__, url_prefix="/issues")


@issues_branch.route("/action", methods=["POST"])
@access_verification
@json_verification
def action() -> str:
    """Выполнить переход"""
    return "Hello, World!"


@issues_branch.route("/comment", methods=["POST"])
@access_verification
@json_verification
def comment() -> str:
    """Оставить комментарий в заявке"""
    return "Hello, World!"


@issues_branch.route("/create", methods=["POST"])
@access_verification
@json_verification
def create() -> str:
    """Создать заявку"""
    return "Hello, World!"


@issues_branch.route("/listConnect", methods=["POST"])
@access_verification
def list_connect() -> Response:
    """Получить список заявок на подключение"""
    return Response(status=204, mimetype="application/json")
