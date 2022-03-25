"""Модуль описания эндпойнтов ветки /sip API"""
from flask import Blueprint

from smartyard.utils import access_verification, json_verification

sip_branch = Blueprint("sip", __name__, url_prefix="/sip")


@sip_branch.route("/helpMe", methods=["POST"])
@access_verification
@json_verification
def help_me() -> str:
    """Звонок в техподержку"""
    return "Hello, World!"
