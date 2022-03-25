import logging
import sys

from flask import Blueprint, Response, current_app, jsonify, request

from smartyard.proxy import Billing
from smartyard.utils import access_verification, json_verification

pay_branch = Blueprint("pay", __name__, url_prefix="/pay")


@pay_branch.route("/prepare", methods=["POST"])
@access_verification
@json_verification
def prepare() -> Response:
    phone = request.environ["USER_PHONE"]
    request_data = request.get_json() or {}

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(repr(request_data["clientId"]))
    logging.debug(repr(request_data["amount"]))

    config = current_app.config["CONFIG"]

    return jsonify(
        Billing(config.BILLING_URL).create_invoice(
            request_data["clientId"], request_data["amount"], phone
        )
    )


@pay_branch.route("/process", methods=["POST"])
@access_verification
@json_verification
def process() -> Response:
    request_data = request.get_json() or {}

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug(request_data["paymentId"])
    logging.debug(request_data["sbId"])

    return jsonify(
        {"code": 200, "name": "OK", "message": "Хорошо", "data": "Платеж в обработке"}
    )
