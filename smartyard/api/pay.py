import json
import logging
import sys

import requests
from flask import Blueprint, Response, abort, current_app, jsonify, request

from smartyard.utils import access_verification

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

    sub_response = requests.post(
        config.BILLING_URL + "createinvoice",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "login": request_data["clientId"],
                "amount": request_data["amount"],
                "phone": phone,
            }
        ),
    ).json()

    return jsonify(sub_response)


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
