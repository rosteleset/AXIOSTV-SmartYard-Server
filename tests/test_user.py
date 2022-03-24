import itertools
import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard import create_app
from smartyard.config import Config, get_config
from smartyard.exceptions import NotFoundCodeAndPhone, NotFoundCodesForPhone
from smartyard.logic.users_bank import UsersBank
from smartyard.proxy.kannel import Kannel
from smartyard.proxy.billing import Billing


@pytest.fixture
def env_file() -> str:
    return os.path.join(os.path.dirname(__file__), "data", "test.env")


@pytest.fixture
def test_config(env_file: str) -> Config:
    return get_config(env_file)


@pytest.fixture
def app(test_config: Config) -> Flask:
    app, _ = create_app(test_config)
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


add_my_phone_required_fields = {"login", "password"}
add_my_phone_optional_fields = {"comment", "notification"}


@pytest.mark.parametrize(
    "fields",
    (
        combination
        for length in range(1, len(add_my_phone_required_fields))
        for combination in itertools.combinations(add_my_phone_required_fields, length)
    ),
)
def test_add_my_phone_not_enough_params(
    client: FlaskClient, fields: tuple, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/addMyPhone",
        headers={"Authorization": "auth"},
        json={field: field for field in fields},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


@pytest.mark.parametrize(
    "fields",
    (
        combination + tuple(add_my_phone_required_fields)
        for length in range(0, len(add_my_phone_optional_fields) + 1)
        for combination in itertools.combinations(add_my_phone_optional_fields, length)
    ),
)
def test_add_my_phone_full_required_params(
    client: FlaskClient, fields: tuple, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/addMyPhone",
        headers={"Authorization": "auth"},
        json={field: field for field in fields},
        content_type="application/json",
    )
    assert response.status_code == 204
    assert response.content_type == "application/json"


app_version_required_fields = {"version", "platform"}


@pytest.mark.parametrize(
    "fields",
    (
        combination
        for length in range(1, len(app_version_required_fields))
        for combination in itertools.combinations(app_version_required_fields, length)
    ),
)
def test_app_version_not_enough_params(
    client: FlaskClient, fields: tuple, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/appVersion",
        headers={"Authorization": "auth"},
        json={field: field for field in fields},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


def test_app_version_wrong_platform(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/appVersion",
        headers={"Authorization": "auth"},
        json={"version": "1.0", "platform": "symbian"},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


@pytest.mark.parametrize(
    "platform",
    ("android", "ios"),
)
def test_app_version_allowed_platform(
    client: FlaskClient, platform: tuple, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/appVersion",
        headers={"Authorization": "auth"},
        json={"version": "1.0", "platform": platform},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


confirm_code_required_fields = {"userPhone", "smsCode"}


@pytest.mark.parametrize(
    "fields",
    (
        combination
        for length in range(1, len(confirm_code_required_fields))
        for combination in itertools.combinations(confirm_code_required_fields, length)
    ),
)
def test_confirm_code_not_enough_params(
    client: FlaskClient, fields: tuple, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/confirmCode",
        headers={"Authorization": "auth"},
        json={field: field for field in fields},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


@pytest.mark.parametrize(
    "fields",
    (
        (("userPhone", ""), ("smsCode", "")),
        (("userPhone", "1234567890"), ("smsCode", "")),
        (("userPhone", "12345678901"), ("smsCode", "")),
        (("userPhone", "123456789012"), ("smsCode", "")),
        (("userPhone", "12345678901"), ("smsCode", "123")),
        (("userPhone", "12345678901"), ("smsCode", "12345")),
        (("userPhone", ""), ("smsCode", "123")),
        (("userPhone", ""), ("smsCode", "1234")),
        (("userPhone", "1234567890"), ("smsCode", "1234")),
        (("userPhone", "123456789012"), ("smsCode", "1234")),
        (("userPhone", ""), ("smsCode", "12345")),
        (("userPhone", "abcdefghijk"), ("smsCode", "abcd")),
        (("userPhone", "-=+/),.@#'$"), ("smsCode", "$#/)")),
        (("userPhone", "           "), ("smsCode", "    ")),
    ),
)
def test_confirm_code_wrong_required_params(
    client: FlaskClient, fields: tuple, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/confirmCode",
        headers={"Authorization": "auth"},
        json={field[0]: field[1] for field in fields},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


@pytest.mark.parametrize(
    "exception,exception_args,excpected",
    (
        (
            NotFoundCodesForPhone,
            {
                "phone": 12345678901,
            },
            {
                "status_code": 404,
                "content_type": "application/json",
                "content": {"code": 404, "name": "Not Found", "message": "Не найдено"},
            },
        ),
        (
            NotFoundCodeAndPhone,
            {
                "phone": 12345678901,
                "code": 1234,
            },
            {
                "status_code": 403,
                "content_type": "application/json",
                "content": {
                    "code": 403,
                    "name": "Пин-код введен неверно",
                    "message": "Пин-код введен неверно",
                },
            },
        ),
    ),
)
def test_confirm_code_wrong_required_params(
    client: FlaskClient,
    exception: Exception,
    exception_args: dict,
    excpected: dict,
    mocker: MockerFixture,
) -> None:
    def __save_user(*args, **kwargs):
        raise exception(**exception_args)

    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(UsersBank, "save_user", __save_user)

    response = client.post(
        "/api/user/confirmCode",
        headers={"Authorization": "auth"},
        json={
            "userPhone": "12345678901",
            "smsCode": "1234",
            "name": "name",
            "patronymic": "patronymic",
            "email": "email",
        },
        content_type="application/json",
    )
    assert response.status_code == excpected["status_code"]
    assert response.content_type == excpected["content_type"]
    assert response.get_json() == excpected["content"]


def test_confirm_code(client: FlaskClient, mocker: MockerFixture) -> None:
    token = "token"
    json_data = {
        "userPhone": "12345678901",
        "smsCode": "1234",
        "name": "name",
        "patronymic": "patronymic",
        "email": "email",
    }

    def __save_user(*args, **kwargs):
        return token

    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(UsersBank, "save_user", __save_user)

    response = client.post(
        "/api/user/confirmCode",
        headers={"Authorization": "auth"},
        json=json_data,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()
    assert response.get_json() == {
        "code": 200,
        "name": "OK",
        "message": "Хорошо",
        "data": {
            "accessToken": token,
            "names": {
                "name": json_data["name"],
                "patronymic": json_data["patronymic"],
            },
        },
    }


def test_get_payments_list(
    client: FlaskClient, test_config: Config, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(Billing, "get_list", return_value={"response": "response"})

    response = client.post(
        "/api/user/getPaymentsList",
        headers={"Authorization": "auth"},
    )

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {"response": "response"}


def test_notification(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/notification",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_ping(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/ping",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 204
    assert response.content_type == "application/json"


def test_push_tokens(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/pushTokens",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


@pytest.mark.parametrize(
    "send_data,expected",
    (
        (
            {},
            {
                "status_code": 422,
                "content_type": "application/json",
                "content": {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "message": "Необрабатываемый экземпляр",
                },
            },
        ),
        (
            {"platform": "android"},
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {"platform": "ios"},
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {"platform": "android", "pushToken": "pushToken"},
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {
                "platform": "android",
                "pushToken": "pushToken",
                "voipToken": "voipToken",
            },
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {
                "platform": "android",
                "pushToken": "pushToken",
                "voipToken": "voipToken",
                "production": "production",
            },
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
    ),
)
def test_register_push_token(
    client: FlaskClient, send_data: dict, expected: dict, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/registerPushToken",
        headers={"Authorization": "auth"},
        json=send_data,
        content_type="application/json",
    )
    assert response.status_code == expected["status_code"]
    assert response.content_type == expected["content_type"]
    if expected["content"]:
        assert response.get_json() == expected["content"]


@pytest.mark.parametrize(
    "send_data,expected",
    (
        (
            {},
            {
                "status_code": 422,
                "content_type": "application/json",
                "content": {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "message": "Необрабатываемый экземпляр",
                },
            },
        ),
        (
            {
                "userPhone": "",
            },
            {
                "status_code": 422,
                "content_type": "application/json",
                "content": {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "message": "Необрабатываемый экземпляр",
                },
            },
        ),
        (
            {
                "userPhone": "7900123456",
            },
            {
                "status_code": 422,
                "content_type": "application/json",
                "content": {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "message": "Необрабатываемый экземпляр",
                },
            },
        ),
        (
            {
                "userPhone": "790012345678",
            },
            {
                "status_code": 422,
                "content_type": "application/json",
                "content": {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "message": "Необрабатываемый экземпляр",
                },
            },
        ),
        (
            {
                "userPhone": "79001234567",
            },
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
    ),
)
def test_request_code(
    client: FlaskClient, send_data: dict, expected: dict, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(UsersBank, "generate_code", return_value=1234)
    mocker.patch.object(Kannel, "send_code", return_value=None)

    response = client.post(
        "/api/user/requestCode",
        headers={"Authorization": "auth"},
        json=send_data,
        content_type="application/json",
    )
    assert response.status_code == expected["status_code"]
    assert response.content_type == expected["content_type"]
    if expected["content"]:
        assert response.get_json() == expected["content"]


@pytest.mark.parametrize(
    "send_data,expected",
    (
        (
            {},
            {
                "status_code": 422,
                "content_type": "application/json",
                "content": {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "message": "Необрабатываемый экземпляр",
                },
            },
        ),
        (
            {
                "contract": "contract",
            },
            {
                "status_code": 200,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {
                "contract": "contract",
                "contactId": "contactId",
            },
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {
                "contract": "contract",
                "code": "code",
            },
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {
                "contract": "contract",
                "contactId": "contactId",
                "code": "code",
            },
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
    ),
)
def test_restore(
    client: FlaskClient, send_data: dict, expected: dict, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/restore",
        headers={"Authorization": "auth"},
        json=send_data,
        content_type="application/json",
    )
    assert response.status_code == expected["status_code"]
    assert response.content_type == expected["content_type"]
    if expected["content"]:
        assert response.get_json() == expected["content"]


@pytest.mark.parametrize(
    "send_data,expected",
    (
        (
            {},
            {
                "status_code": 422,
                "content_type": "application/json",
                "content": {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "message": "Необрабатываемый экземпляр",
                },
            },
        ),
        (
            {"name": "name"},
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
        (
            {"name": "name", "patronymic": "patronymic"},
            {
                "status_code": 204,
                "content_type": "application/json",
                "content": {},
            },
        ),
    ),
)
def test_send_name(
    client: FlaskClient, send_data: dict, expected: dict, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/user/sendName",
        headers={"Authorization": "auth"},
        json=send_data,
        content_type="application/json",
    )
    assert response.status_code == expected["status_code"]
    assert response.content_type == expected["content_type"]
    if expected["content"]:
        assert response.get_json() == expected["content"]


def test_get_billing_list(
    client: FlaskClient, test_config: Config, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(Billing, "get_list", return_value={"response": "response"})

    response = client.post(
        "/api/user/getBillingList",
        headers={"Authorization": "auth"},
    )

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {"response": "response"}
