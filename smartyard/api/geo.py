"""Модуль описания эндпойнтов ветки /geo API"""
from flask import Blueprint

from smartyard.utils import access_verification, json_verification

geo_branch = Blueprint("geo", __name__, url_prefix="/geo")


@geo_branch.route("/address", methods=["POST"])
@access_verification
@json_verification
def address() -> str:
    """Адрес дома"""
    return "Hello, World!"


@geo_branch.route("/coder", methods=["POST"])
@access_verification
@json_verification
def coder() -> str:
    """Геокоординаты по адресу"""
    return "Hello, World!"


@geo_branch.route("/getAllLocations", methods=["POST"])
@access_verification
@json_verification
def get_all_locations() -> str:
    """Список населенных пунктов"""
    return "Hello, World!"


@geo_branch.route("/getAllServices", methods=["POST"])
@access_verification
@json_verification
def get_all_services() -> str:
    """Список всех возможных услуг"""
    return "Hello, World!"


@geo_branch.route("/getHouses", methods=["POST"])
@access_verification
@json_verification
def get_houses() -> str:
    """Список домов"""
    return "Hello, World!"


@geo_branch.route("/getServices", methods=["POST"])
@access_verification
@json_verification
def get_services() -> str:
    """Список доступных услуг"""
    return "Hello, World!"


@geo_branch.route("/getStreets", methods=["POST"])
@access_verification
@json_verification
def get_streets() -> str:
    """Список улиц"""
    return "Hello, World!"
