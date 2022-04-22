"""Модуль описания эндпойнтов ветки /ext API"""
from flask import Blueprint

from smartyard.utils import access_verification, json_verification

ext_branch = Blueprint("ext", __name__, url_prefix="/ext")


@ext_branch.route("/ext", methods=["POST"])
@access_verification
@json_verification
def extension() -> str:
    """Расширение"""
    return "Hello, World!"


@ext_branch.route("/list", methods=["POST"])
@access_verification
@json_verification
def list_extensions() -> str:
    """Список глобальных расширений (меню)"""
    return "Hello, World!"
