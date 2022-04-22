"""Пакет описания API сервиса"""
import json

from flask import Blueprint, Response

from .address import address_branch
from .cctv import cctv_branch
from .ext import ext_branch
from .frs import frs_branch
from .geo import geo_branch
from .inbox import inbox_branch
from .issues import issues_branch
from .pay import pay_branch
from .root import root_branch
from .sip import sip_branch
from .user import user_branch

__all__ = ["api"]

api = Blueprint("api", __name__, url_prefix="/api")

for branch in (
    root_branch,
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
):
    api.register_blueprint(branch)


@api.errorhandler(401)
def unauthorized(error) -> Response:
    """Обработчик ошибки Unauthorized, HTTP код 401"""
    return Response(
        response=json.dumps(error.description),
        status=401,
        content_type="application/json",
    )


@api.errorhandler(403)
def forbidden(error):
    """Обработчик ошибки Forbidden, HTTP код 403"""
    return Response(
        response=json.dumps(error.description),
        status=403,
        content_type="application/json",
    )


@api.errorhandler(404)
def not_found(error):
    """Обработчик ошибки Not Found, HTTP код 404"""
    return Response(
        response=json.dumps(error.description),
        status=404,
        content_type="application/json",
    )


@api.errorhandler(410)
def gone(_):
    """Обработчик ошибки Gone, HTTP код 410"""
    return Response(
        response=json.dumps({"error": "авторизация отозвана"}),
        status=410,
        content_type="application/json",
    )


@api.errorhandler(422)
def unprocessable_entity(error):
    """Обработчик ошибки Unprocessable Entity, HTTP код 422"""
    return Response(
        response=json.dumps(error.description),
        status=422,
        content_type="application/json",
    )


@api.errorhandler(424)
def failed_dependency(_):
    """Обработчик ошибки Failed Dependency, HTTP код 424"""
    return Response(
        response=json.dumps({"error": "неверный токен"}),
        status=424,
        content_type="application/json",
    )


@api.errorhandler(429)
def too_many_requests(_):
    """Обработчик ошибки Too Many Requests, HTTP код 429"""
    return Response(
        response=json.dumps(
            {
                "code": 429,
                "name": "Too Many Requests",
                "message": "Слишком много запросов",
            }
        ),
        status=429,
        content_type="application/json",
    )
