import json
import uuid
from random import randint

import requests
from flask import Blueprint, Response, abort, jsonify, request
from requests.exceptions import HTTPError

from smartyard.config import get_config
from smartyard.db import Temps, Users, create_db_connection
from smartyard.utils import access_verification

user_branch = Blueprint(url_prefix="/user")
db = create_db_connection()


@user_branch.route("/api/user/addMyPhone", methods=["POST"])
def add_my_phone():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    login = request_data.get("login")
    password = request_data.get("password")
    comment = request_data.get("comment", "")
    notification = request_data.get("notification", "")

    if not login or not password:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return Response(status=204, mimetype="application/json")


@user_branch.route("/api/user/appVersion", methods=["POST"])
def app_version():
    access_verification(request.headers)
    request_data = request.get_json() or {}
    version = request_data.get("version")
    platform = request_data.get("platform")

    if version and platform and (platform == "android" or platform == "ios"):
        return jsonify(
            {"code": 200, "name": "OK", "message": "Хорошо", "data": "upgrade"}
        )
    else:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )


@user_branch.route("/api/user/confirmCode", methods=["POST"])
def confirm_code():
    request_data = request.get_json() or {}
    userPhone = request_data.get("userPhone", "")
    smsCode = request_data.get("smsCode", "")

    if len(userPhone) != 11 or len(smsCode) != 4:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    if not db.session.query(
        db.session.query(Temps).filter_by(userphone=int(userPhone)).exists()
    ).scalar():
        abort(404, {"code": 404, "name": "Not Found", "message": "Не найдено"})

    if not db.session.query(
        db.exists().where(
            Temps.userphone == int(userPhone) and Temps.smscode == int(smsCode)
        )
    ).scalar():
        abort(
            403,
            {
                "code": 403,
                "name": "Пин-код введен неверно",
                "message": "Пин-код введен неверно",
            },
        )

    accessToken = str(uuid.uuid4())
    if not "name" in request_data:
        request_data["name"] = None
    if not "patronymic" in request_data:
        request_data["patronymic"] = None
    if not "email" in request_data:
        request_data["email"] = None
    if db.session.query(
        db.session.query(Users).filter_by(userphone=int(userPhone)).exists()
    ).scalar():
        db.session.query(Users).filter_by(userphone=int(userPhone)).update(
            {"uuid": accessToken}
        )
    else:
        new_user = Users(
            uuid=accessToken,
            userphone=int(request_data["userPhone"]),
            name=request_data["name"],
            patronymic=request_data["patronymic"],
            email=request_data["email"],
        )
        db.session.add(new_user)
    db.session.query(Temps).filter_by(userphone=int(userPhone)).delete()
    db.session.commit()
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {
                "accessToken": accessToken,
                "names": {
                    "name": request_data["name"],
                    "patronymic": request_data["patronymic"],
                },
            },
        }
    )


@user_branch.route("/api/user/getPaymentsList", methods=["POST"])
def get_payments_list():
    phone = access_verification(request.headers)
    config = get_config()
    response = requests.post(
        config.BILLING_URL + "getlist",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"phone": phone}),
    ).json()
    return jsonify(response)


@user_branch.route("/api/user/notification", methods=["POST"])
def notification():
    access_verification(request.headers)
    money = "t"
    enable = "t"
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {"money": money, "enable": enable},
        }
    )


@user_branch.route("/api/user/ping", methods=["POST"])
def ping():
    access_verification(request.headers)
    return Response(status=204, mimetype="application/json")


@user_branch.route("/api/user/pushTokens", methods=["POST"])
def push_tokens():
    access_verification(request.headers)
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {
                "pushToken": "fnTGJUfJTIC61WfSKWHP_N:APA91bGbnS3ck-cEWO0aj4kExZLsmGGmhziTu2lfyvjIpbmia5ahfL4WlJrr8DOjcDMUo517HUjxH4yZm0m5tF89CssdSsmO6IjcrS1U_YM3ue2187rc9ow9rS0xL8Q48vwz2e6j42l1",
                "voipToken": "off",
            },
        }
    )


@user_branch.route("/api/user/registerPushToken", methods=["POST"])
def register_push_token():
    access_verification(request.headers)

    request_data = request.get_json() or {}
    platform = request_data.get("platform")
    if not platform:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    pushToken = request_data.get("pushToken")
    voipToken = request_data.get("voipToken")
    production = request_data.get("production")

    return Response(status=204, mimetype="application/json")


@user_branch.route("/api/user/requestCode", methods=["POST"])
def request_code():
    request_data = request.get_json() or {}
    user_phone = request_data.get("userPhone", "")
    if len(user_phone) != 11:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    config = get_config()
    sms_code = int(
        str(randint(1, 9))
        + str(randint(0, 9))
        + str(randint(0, 9))
        + str(randint(0, 9))
    )
    sms_text = f"{config.KANNEL_TEXT}{sms_code}"
    user_phone = int(user_phone)
    temp_user = Temps(userphone=user_phone, smscode=sms_code)
    db.session.add(temp_user)
    db.session.commit()

    try:
        response = requests.get(
            url=f"http://{config.KANNEL_HOST}:{config.KANNEL_PORT}/{config.KANNEL_PATH}",
            params=(
                ("user", config.KANNEL_USER),
                ("pass", config.KANNEL_PASS),
                ("from", config.KANNEL_FROM),
                ("coding", config.KANNEL_CODING),
                ("to", user_phone),
                ("text", sms_text.encode("utf-16-be").decode("utf-8").upper()),
            ),
        )
        response.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    else:
        print(f"Success send sms to {user_phone} and text {sms_text}!")

    return Response(status=204, mimetype="application/json")


@user_branch.route("/api/user/restore", methods=["POST"])
def restore():
    access_verification(request.headers)
    request_data = request.get_json() or {}
    contract = request_data.get("contract")
    if not contract:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    contact_id = request_data.get("contactId")
    code = request_data.get("code")
    if not (contact_id and code):
        return jsonify(
            {
                "code": 200,
                "name": "OK",
                "message": "Хорошо",
                "data": [
                    {
                        "id": "bfe5bc9e5d2b2501767a7589ec3c485c",
                        "contact": "sb**@*********.ru",
                        "type": "email",
                    },
                    {
                        "id": "064601c186c73c5e47e8dedbab90dd11",
                        "contact": "8 (964) ***-*000",
                        "type": "phone",
                    },
                ],
            }
        )
    if contact_id and not code:
        print(f"Кто-то сделал POST запрос contactId и передал {contact_id}")
        return Response(status=204, mimetype="application/json")
    if not contact_id and code:
        if code == code:  # TODO: Проверить странное условие
            print(f"Кто-то сделал POST запрос code и передал {code}")
            return Response(status=204, mimetype="application/json")
        else:
            abort(403, {"code": 403, "name": "Forbidden", "message": "Запрещено"})
    comment = request_data.get("comment")
    notification = request_data.get("notification")


@user_branch.route("/api/user/sendName", methods=["POST"])
def send_name():
    access_verification(request.headers)
    request_data = request.get_json() or {}
    name = request_data.get("name")

    if not name:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )
    if not "patronymic" in request_data:
        request_data["patronymic"] = None
    return Response(status=204, mimetype="application/json")


@user_branch.route("/api/user/getBillingList", methods=["POST"])
def get_billing_list():
    phone = access_verification(request.headers)
    config = get_config()
    sub_response = requests.post(
        config.BILLING_URL + "getlist",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"phone": phone}),
    ).json()
    return jsonify(sub_response)
