"""Модуль описания эндпойнтов ветки /address API"""
from flask import Blueprint, Response, current_app, jsonify, request

from smartyard.proxy import Billing
from smartyard.utils import access_verification, json_verification

address_branch = Blueprint("address", __name__, url_prefix="/address")


@address_branch.route("/access", methods=["POST"])
@access_verification
@json_verification(("guestPhone", "flatId", "clientId", "expire"))
def access() -> Response:
    """Управление доступами"""
    return Response(status=204, mimetype="application/json")


@address_branch.route("/getAddressList", methods=["POST"])
@access_verification
def get_address_list() -> Response:
    """Список адресов на главный экран"""
    config = current_app.config["CONFIG"]
    return jsonify(
        Billing(config.BILLING_URL).get_address_list(request.environ["USER_PHONE"])
    )


@address_branch.route("/getSettingsList", methods=["POST"])
@access_verification
def get_settings_list() -> Response:
    """Список адресов для настроек"""
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": [
                {
                    "hasPlog": "t",
                    "contractName": "ФЛ-85973/20",
                    "clientId": "91052",
                    "contractOwner": "t",
                    "clientName": "Бивард-00011 (Чемодан 2)",
                    "services": ["internet", "cctv", "domophone"],
                    "lcab": (
                        "https://lc.lanta.me/?auth="
                        "Zjg1OTczOmY5NzkzNTQzM2U5YmQ5ZThkYTJiZmU2MWMwNDlkZGMy"
                    ),
                    "houseId": "19260",
                    "flatId": "136151",
                    "flatNumber": "1",
                    "flatOwner": "t",
                    "address": "Тамбов, ул. Верховая, дом 17, кв 1",
                    "hasGates": "f",
                    "roommates": [
                        {
                            "phone": "79051202936",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79106599009",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79156730435",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79641340000",
                            "expire": "3000-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79641340000",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                    ],
                },
                {
                    "hasPlog": "t",
                    "services": ["cctv", "domophone"],
                    "houseId": "19260",
                    "flatId": "136162",
                    "flatNumber": "12",
                    "flatOwner": "f",
                    "address": "Тамбов, ул. Верховая, дом 17, кв 12",
                    "hasGates": "f",
                    "roommates": [
                        {
                            "phone": "79176194895",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79202313789",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                    ],
                },
                {
                    "hasPlog": "t",
                    "services": ["cctv", "domophone"],
                    "houseId": "6694",
                    "flatId": "306",
                    "flatNumber": "69",
                    "flatOwner": "f",
                    "address": "Тамбов, ул. Пионерская, дом 5'б', кв 69",
                    "hasGates": "t",
                    "roommates": [
                        {
                            "phone": "79069202020",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79641349232",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79091215044",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79127600769",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79106500155",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79514470944",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79107567265",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79203409810",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79227063593",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79220144401",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79114688286",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79661840298",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79641340000",
                            "expire": "3001-01-01 00:00:00",
                            "type": "owner",
                        },
                        {
                            "phone": "79275807272",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                        {
                            "phone": "79107567249",
                            "expire": "3001-01-01 00:00:00",
                            "type": "inner",
                        },
                    ],
                },
                {
                    "hasPlog": "t",
                    "services": ["cctv", "domophone"],
                    "houseId": "6694",
                    "flatId": "307",
                    "flatNumber": "70",
                    "flatOwner": "f",
                    "address": "Тамбов, ул. Пионерская, дом 5'б', кв 70",
                    "hasGates": "t",
                },
            ],
        }
    )


@address_branch.route("/intercom", methods=["POST"])
@access_verification
@json_verification(("flatId",))
def intercom() -> Response:
    """Настройки домофона (квартиры)"""
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": {
                "allowDoorCode": "t",
                "doorCode": "22438",
                "CMS": "t",
                "VoIP": "t",
                "autoOpen": "2020-06-03 18:32:10",
                "whiteRabbit": "0",
                "FRSDisabled": "f",
            },
        }
    )


@address_branch.route("/offices", methods=["POST"])
@access_verification
@json_verification
def offices() -> Response:
    """Адреса офисов"""
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": [
                {
                    "lat": 52.730641,
                    "lon": 41.45234,
                    "address": "Мичуринская улица, 2А",
                    "opening": "09:00-19:00 (без выходных)",
                },
                {
                    "lat": 52.767248,
                    "lon": 41.40488,
                    "address": "улица Чичерина, 48А (ТЦ Апельсин)",
                    "opening": "09:00-19:00 (без выходных)",
                },
                {
                    "lat": 52.707399,
                    "lon": 41.397374,
                    "address": "улица Сенько, 25А (Магнит)",
                    "opening": "09:00-19:00 (без выходных)",
                },
                {
                    "lat": 52.675463,
                    "lon": 41.465411,
                    "address": "Астраханская улица, 189А (ТЦ МЖК)",
                    "opening": "09:00-19:00 (без выходных)",
                },
                {
                    "lat": 52.586785,
                    "lon": 41.497009,
                    "address": "Октябрьская улица, 13 (ДК)",
                    "opening": "09:00-19:00 (вс, пн - выходной)",
                },
            ],
        }
    )


@address_branch.route("/openDoor", methods=["POST"])
@access_verification
@json_verification(("domophoneId",))
def open_door() -> Response:
    """Открыть дверь (калитку, ворота, шлагбаум)"""
    return Response(status=204, mimetype="application/json")


@address_branch.route("/plog", methods=["POST"])
@access_verification
@json_verification(("flatId",))
def plog() -> Response:
    """Журнал событий объекта за день"""
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": [
                {
                    "date": "2021-12-15 13:03:23",
                    "uuid": "4d5082d2-f8a1-48ac-819e-c16f1f81a1e0",
                    "image": "3f99bdf6-96ef-4300-b709-1f557806c65b",
                    "objectId": "79",
                    "objectType": "0",
                    "objectMechanizma": "0",
                    "mechanizmaDescription": "Пионерская 5 б п 3 [Подъезд]",
                    "event": "1",
                    "detail": "1",
                    "preview": (
                        "https://static.dm.lanta.me/2021-12-15/3/"
                        "f/9/9/3f99bdf6-96ef-4300-b709-1f557806c65b.jpg"
                    ),
                    "previewType": 2,
                    "detailX": {
                        "opened": "f",
                        "face": {
                            "left": "614",
                            "top": "38",
                            "width": "174",
                            "height": "209",
                        },
                        "flags": ["canLike"],
                    },
                },
                {
                    "date": "2021-12-15 00:16:20",
                    "uuid": "bc1671b4-e01b-487e-b175-745e82be0ca9",
                    "image": "86ddb8e1-1122-4946-8495-a251b6320b99",
                    "objectId": "75",
                    "objectType": "0",
                    "objectMechanizma": "0",
                    "mechanizmaDescription": "Пионерская 5 б [Калитка]",
                    "event": "4",
                    "detail": "89103523377",
                    "preview": (
                        "https://static.dm.lanta.me/2021-12-15/8"
                        "/6/d/d/86ddb8e1-1122-4946-8495-a251b6320b99.jpg"
                    ),
                    "previewType": 1,
                    "detailX": {"phone": "89103523377"},
                },
                {
                    "date": "2021-12-15 00:14:21",
                    "uuid": "32fd7c27-0d35-4d98-ab29-2544c3d0b9a7",
                    "image": "ad14c83a-126a-4f09-a659-f412fb11007e",
                    "objectId": "75",
                    "objectType": "0",
                    "objectMechanizma": "0",
                    "mechanizmaDescription": "Пионерская 5 б [Калитка]",
                    "event": "4",
                    "detail": "89103523377",
                    "preview": (
                        "https://static.dm.lanta.me/2021-12-15/a"
                        "/d/1/4/ad14c83a-126a-4f09-a659-f412fb11007e.jpg"
                    ),
                    "previewType": 1,
                    "detailX": {"phone": "89103523377"},
                },
                {
                    "date": "2021-12-15 00:03:56",
                    "uuid": "ff42c747-3216-4fa7-8b68-128207d1a9ab",
                    "image": "0b335948-864f-41d6-b9a7-465f88f20ef1",
                    "objectId": "75",
                    "objectType": "0",
                    "objectMechanizma": "0",
                    "mechanizmaDescription": "Пионерская 5 б [Калитка]",
                    "event": "4",
                    "detail": "89103523377",
                    "preview": (
                        "https://static.dm.lanta.me/2021-12-15/0"
                        "/b/3/3/0b335948-864f-41d6-b9a7-465f88f20ef1.jpg"
                    ),
                    "previewType": 1,
                    "detailX": {"phone": "89103523377"},
                },
                {
                    "date": "2021-12-15 00:01:28",
                    "uuid": "0e57d2c7-9e73-4083-98bb-2b140622be93",
                    "image": "8fc3224e-ef46-4ec6-9d5d-04e249ec2e31",
                    "objectId": "75",
                    "objectType": "0",
                    "objectMechanizma": "0",
                    "mechanizmaDescription": "Пионерская 5 б [Калитка]",
                    "event": "4",
                    "detail": "89103523377",
                    "preview": (
                        "https://static.dm.lanta.me/2021-12-15/8"
                        "/f/c/3/8fc3224e-ef46-4ec6-9d5d-04e249ec2e31.jpg"
                    ),
                    "previewType": 1,
                    "detailX": {"phone": "89103523377"},
                },
                {
                    "date": "2021-12-15 00:00:02",
                    "uuid": "3bcac0af-677b-49d8-ba65-c18c3bcc8668",
                    "image": "c28c7e58-7797-4143-a2b8-2c513e216bb8",
                    "objectId": "75",
                    "objectType": "0",
                    "objectMechanizma": "0",
                    "mechanizmaDescription": "Пионерская 5 б [Калитка]",
                    "event": "4",
                    "detail": "89103523377",
                    "preview": (
                        "https://static.dm.lanta.me/2021-12-15/c"
                        "/2/8/c/c28c7e58-7797-4143-a2b8-2c513e216bb8.jpg"
                    ),
                    "previewType": 1,
                    "detailX": {"phone": "89103523377"},
                },
            ],
        }
    )


@address_branch.route("/plogDays", methods=["POST"])
@access_verification
@json_verification(("flatId",))
def plog_days() -> Response:
    """Список дат (дней) на которые есть записи в журнале событий объекта"""
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": [
                {"day": "2021-12-15", "events": "6"},
                {"day": "2021-12-13", "events": "2"},
                {"day": "2021-12-11", "events": "3"},
                {"day": "2021-12-09", "events": "3"},
                {"day": "2021-12-07", "events": "1"},
                {"day": "2021-12-06", "events": "4"},
                {"day": "2021-12-05", "events": "1"},
                {"day": "2021-12-04", "events": "1"},
                {"day": "2021-11-30", "events": "1"},
                {"day": "2021-11-29", "events": "6"},
                {"day": "2021-11-27", "events": "7"},
                {"day": "2021-11-26", "events": "13"},
                {"day": "2021-11-25", "events": "5"},
                {"day": "2021-11-23", "events": "2"},
                {"day": "2021-11-22", "events": "2"},
                {"day": "2021-11-20", "events": "2"},
                {"day": "2021-11-17", "events": "3"},
                {"day": "2021-11-16", "events": "1"},
                {"day": "2021-11-15", "events": "1"},
                {"day": "2021-11-13", "events": "1"},
                {"day": "2021-11-12", "events": "6"},
                {"day": "2021-11-11", "events": "2"},
                {"day": "2021-11-09", "events": "3"},
                {"day": "2021-11-05", "events": "1"},
                {"day": "2021-10-30", "events": "1"},
                {"day": "2021-10-29", "events": "3"},
                {"day": "2021-10-28", "events": "3"},
                {"day": "2021-10-27", "events": "3"},
                {"day": "2021-10-26", "events": "2"},
                {"day": "2021-10-23", "events": "2"},
                {"day": "2021-10-22", "events": "3"},
                {"day": "2021-10-21", "events": "4"},
                {"day": "2021-10-19", "events": "3"},
                {"day": "2021-10-18", "events": "2"},
                {"day": "2021-10-16", "events": "4"},
                {"day": "2021-10-15", "events": "1"},
                {"day": "2021-10-14", "events": "3"},
                {"day": "2021-10-09", "events": "1"},
                {"day": "2021-10-08", "events": "6"},
                {"day": "2021-10-07", "events": "4"},
                {"day": "2021-10-06", "events": "7"},
                {"day": "2021-10-05", "events": "6"},
                {"day": "2021-10-03", "events": "1"},
                {"day": "2021-10-02", "events": "7"},
                {"day": "2021-10-01", "events": "12"},
                {"day": "2021-09-30", "events": "5"},
                {"day": "2021-09-29", "events": "6"},
                {"day": "2021-09-28", "events": "17"},
                {"day": "2021-09-27", "events": "7"},
                {"day": "2021-09-25", "events": "2"},
                {"day": "2021-09-22", "events": "1"},
                {"day": "2021-09-20", "events": "1"},
                {"day": "2021-09-18", "events": "4"},
                {"day": "2021-09-17", "events": "3"},
                {"day": "2021-09-16", "events": "5"},
                {"day": "2021-09-15", "events": "1"},
                {"day": "2021-09-13", "events": "12"},
                {"day": "2021-09-11", "events": "1"},
                {"day": "2021-09-06", "events": "2"},
                {"day": "2021-09-05", "events": "2"},
            ],
        }
    )


@address_branch.route("/registerQR", methods=["POST"])
@access_verification
@json_verification(("QR",))
def register_qr() -> Response:
    """Зарегистрировать QR код"""
    request_data = request.get_json()
    qr_code = request_data.get("QR")

    qr_current = qr_code + "1"
    # TODO: Проверить: с условием что-то не то
    if qr_code == qr_current:
        response = {
            "code": 520,
            "message": "Этот пользователь уже зарегистрирован в системе",
        }
    # TODO: Проверить: со следующими условиями что-то не то
    # if qr_code != qr_code:
    #     response = {"code": 520, "message": "Некорректный QR-код!"}
    # if qr_code != qr_code:
    #     response = {
    #         "code": 200,
    #         "name": "OK",
    #         "message": "Хорошо",
    #         "data": "QR-код не является кодом для доступа к квартире",
    #     }
    # if qr_code == qr_code:
    #     response = {
    #         "code": 200,
    #         "name": "OK",
    #         "message": "Хорошо",
    #         "data": (
    #             "Ваш запрос принят и будет обработан "
    #             "в течение одной минуты, пожалуйста подождите"
    #         ),
    #     }
    response = {
        "code": 200,
        "name": "OK",
        "message": "Хорошо",
        "data": (
            "Ваш запрос принят и будет обработан "
            "в течение одной минуты, пожалуйста подождите"
        ),
    }
    return jsonify(response)


@address_branch.route("/resend", methods=["POST"])
@access_verification
@json_verification
def resend() -> str:
    """Повторная отправка информации для гостя"""
    return "Hello, World!"


@address_branch.route("/resetCode", methods=["POST"])
@access_verification
@json_verification
def reset_code() -> str:
    """Перегенерировать код открытия двери"""
    return "Hello, World!"


@address_branch.route("/getHcsList", methods=["POST"])
@access_verification
def get_hcs_list():
    """????"""
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": [
                {"houseId": "19260", "address": "Липецк, ул. Катукова, дом 36 кв 18"},
                {"houseId": "6694", "address": "Липецк, ул. Московская, дом 145 кв 3"},
            ],
        }
    )
