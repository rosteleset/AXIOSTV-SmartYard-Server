import logging
import sys

from flask import Blueprint, Response, abort, current_app, jsonify, request

from smartyard.utils import access_verification
from smartyard.proxy.billing import Billing

pay_branch = Blueprint("pay", __name__, url_prefix="/pay")


@pay_branch.route("/prepare", methods=["POST"])
def prepare() -> Response:
    phone = access_verification(request.headers)
    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data["clientId"]))
    logging.debug(repr(request_data["amount"]))

    config = current_app.config["CONFIG"]

    return jsonify(Billing(config.BILLING_URL).create_invoice(request_data["clientId"], request_data["amount"], phone))


@pay_branch.route("/process", methods=["POST"])
def process() -> Response:
    access_verification(request.headers)
    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data["paymentId"]))
    logging.debug(repr(request_data["sbId"]))

    return jsonify(
        {"code": 200, "name": "OK", "message": "Хорошо", "data": "Платеж в обработке"}
    )
