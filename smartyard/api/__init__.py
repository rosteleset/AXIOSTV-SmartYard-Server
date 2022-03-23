from flask import Blueprint, jsonify, make_response

from .address import address_branch
from .cctv import cctv_branch
from .ext import ext_branch
from .frs import frs_branch
from .geo import geo_branch
from .inbox import inbox_branch
from .issues import issues_branch
from .pay import pay_branch
from .sip import sip_branch
from .user import user_branch

__all__ = ["api"]

api = Blueprint(url_prefix="/api")

for branch in {
    address_branch,
    cctv_branch,
    ext_branch,
    frs_branch,
    geo_branch,
    inbox_branch,
    issues_branch,
    pay_branch,
    sip_branch,
    user_branch,
}:
    api.register_blueprint(branch, url_prefix="/api")


@api.route("/")
def index():
    return "Hello, World!"


@api.errorhandler(401)
def not_found(error):
    return make_response(jsonify(error), 401)


@api.errorhandler(403)
def not_found(error):
    return make_response(jsonify(error), 403)


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "пользователь не найден"}), 404)


@api.errorhandler(410)
def not_found(error):
    return make_response(jsonify({"error": "авторизация отозвана"}), 410)


@api.errorhandler(422)
def not_found(error):
    return make_response(jsonify(error), 422)


@api.errorhandler(424)
def not_found(error):
    return make_response(jsonify({"error": "неверный токен"}), 424)


@api.errorhandler(429)
def not_found(error):
    return make_response(
        jsonify(
            {
                "code": 429,
                "name": "Too Many Requests",
                "message": "Слишком много запросов",
            }
        ),
        429,
    )
