"""Модуль тестирования API, ветка /api/address"""

import itertools

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users
from smartyard.proxy import Billing

access_fields = {"clientId", "expire", "flatId", "guestPhone"}


@pytest.mark.parametrize(
    "fields",
    (
        combination
        for length in range(1, len(access_fields))
        for combination in itertools.combinations(access_fields, length)
    ),
)
def test_access_not_enough_params(
    flask_client: FlaskClient, fields: tuple, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест попытки аутентификации с нехваткой данных"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/access",
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


def test_access_full_params(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест попытки аутентификации с полными данными"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/access",
        headers={"Authorization": "auth"},
        json={field: field for field in access_fields},
        content_type="application/json",
    )
    assert response.status_code == 204
    assert response.content_type == "application/json"


def test_get_address_list(
    flask_client: FlaskClient,
    logic_user: User,
    mocker: MockerFixture,
) -> None:
    """Тест запроса списка адресов пользователя"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    mocker.patch.object(
        Billing, "get_address_list", return_value={"response": "response"}
    )
    response = flask_client.post(
        "/api/address/getAddressList",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {"response": "response"}


def test_get_settings_list(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса списка настроек"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/getSettingsList",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_intercom_without_flat_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса настроек домофона без указания квартиры"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/intercom",
        headers={"Authorization": "auth"},
        json={},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


def test_intercom_with_flat_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса настроек домофона с указанием квартиры"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/intercom",
        headers={"Authorization": "auth"},
        json={"flatId": "flatId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_offices(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса списка офисов"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/offices",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_open_door_without_domophone_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса открытия двери без указания идентификатора домофона"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/openDoor",
        headers={"Authorization": "auth"},
        json={},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


def test_open_door_with_domophone_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса открытия двери с указанием идентификатора домофона"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/openDoor",
        headers={"Authorization": "auth"},
        json={"domophoneId": "domophoneId"},
        content_type="application/json",
    )
    assert response.status_code == 204
    assert response.content_type == "application/json"


def test_plog_without_flat_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса записей событий без указания идентификатора квартиры"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/plog",
        headers={"Authorization": "auth"},
        json={},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


def test_plog_with_flat_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса записей событий с указанием идентификатора квартиры"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/plog",
        headers={"Authorization": "auth"},
        json={"flatId": "flatId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_plog_days_without_flat_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса дней записей событий без указания идентификатора квартиры"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/plogDays",
        headers={"Authorization": "auth"},
        json={},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


def test_plog_days_with_flat_id(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса дней записей событий с указанием идентификатора квартиры"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/plogDays",
        headers={"Authorization": "auth"},
        json={"flatId": "flatId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_register_qr_without_qr(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса регистрации qr-кода без его передачи"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/registerQR",
        headers={"Authorization": "auth"},
        json={},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "code": 422,
        "name": "Unprocessable Entity",
        "message": "Необрабатываемый экземпляр",
    }


def test_register_qr_with_qr(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса регистрации qr-кода"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/registerQR",
        headers={"Authorization": "auth"},
        json={"QR": "QR"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_resend(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса повторной отправки для гостя"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/resend",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_reset_code(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест запроса сброса кода открытия двери"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/resetCode",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_get_hcs_list(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест ????"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/address/getHcsList",
        headers={"Authorization": "auth"},
        json={},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()
