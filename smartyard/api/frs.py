"""Модуль описания эндпойнтов ветки /ext API"""
from flask import Blueprint

from smartyard.utils import access_verification, json_verification

frs_branch = Blueprint("frs", __name__, url_prefix="/frs")


@frs_branch.route("/disLike", methods=["POST"])
@access_verification
@json_verification
def dislike() -> str:
    """Дизлайкнуть фото (чужое, ложное срабатывание, разонравилось)"""
    return "Hello, World!"


@frs_branch.route("/like", methods=["POST"])
@access_verification
@json_verification
def like() -> str:
    """Лайкнуть фото для использования при распозновании"""
    return "Hello, World!"


@frs_branch.route("/listFaces", methods=["POST"])
@access_verification
@json_verification
def list_faces() -> str:
    """Список фотографий"""
    return "Hello, World!"
