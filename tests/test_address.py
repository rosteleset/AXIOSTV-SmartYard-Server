import itertools
import json
import os

import pytest
import requests
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard import create_app
from smartyard.config import Config, get_config
from smartyard.logic.users_bank import UsersBank


@pytest.fixture
def env_file() -> str:
    return os.path.join(os.path.dirname(__file__), "data", "test.env")


@pytest.fixture
def test_config(env_file: str) -> Config:
    return get_config(env_file)


@pytest.fixture
def app(test_config) -> Flask:
    app, _ = create_app(test_config)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


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
    client: FlaskClient, fields: tuple, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
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


def test_access_full_params(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/access",
        headers={"Authorization": "auth"},
        json={field: field for field in access_fields},
        content_type="application/json",
    )
    assert response.status_code == 204
    assert response.content_type == "application/json"


def test_get_address_list(
    client: FlaskClient, test_config: Config, mocker: MockerFixture
) -> None:
    class Mock:
        def __init__(self) -> None:
            self.args = []
            self.kwargs = {}

        def __call__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            return self

        def json(self):
            return {"response": "response"}

    mock = Mock()
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(requests, "post", mock)
    response = client.post(
        "/api/address/getAddressList",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == mock.json()
    assert mock.args == (test_config.BILLING_URL + "getaddresslist",)
    assert mock.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "data": json.dumps(
            {
                "phone": 79001234567,
            }
        ),
    }


def test_get_settings_list(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/getSettingsList",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_intercom_without_flat_id(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
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


def test_intercom_with_flat_id(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/intercom",
        headers={"Authorization": "auth"},
        json={"flatId": "flatId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_offices(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/offices",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_open_door_without_domophone_id(
    client: FlaskClient, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
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
    client: FlaskClient, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/openDoor",
        headers={"Authorization": "auth"},
        json={"domophoneId": "domophoneId"},
        content_type="application/json",
    )
    assert response.status_code == 204
    assert response.content_type == "application/json"


def test_plog_without_flat_id(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
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


def test_plog_with_flat_id(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/plog",
        headers={"Authorization": "auth"},
        json={"flatId": "flatId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_plog_days_without_flat_id(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
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


def test_plog_days_with_flat_id(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/plogDays",
        headers={"Authorization": "auth"},
        json={"flatId": "flatId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_register_qr_without_qr(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
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


def test_register_qr_with_qr(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/registerQR",
        headers={"Authorization": "auth"},
        json={"QR": "QR"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_resend(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/resend",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_reset_code(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/resetCode",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_get_hcs_list(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/address/getHcsList",
        headers={"Authorization": "auth"},
        json={},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()
