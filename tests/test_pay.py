import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard import config, create_app
from smartyard.logic.users_bank import UsersBank
from smartyard.proxy.billing import Billing


@pytest.fixture
def env_file() -> str:
    return os.path.join(os.path.dirname(__file__), "data", "test.env")


@pytest.fixture
def test_config(env_file: str) -> config.Config:
    return config.get_config(env_file)


@pytest.fixture
def app(test_config: config.Config) -> Flask:
    app, _ = create_app(test_config)
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


def test_prepare(
    client: FlaskClient, test_config: config.Config, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    mocker.patch.object(Billing, "create_invoice", return_value={"response": "response"})

    response = client.post(
        "/api/pay/prepare",
        headers={"Authorization": "auth"},
        json={
            "clientId": "clientId",
            "amount": "amount",
        },
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {"response": "response"}


def test_process(client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = client.post(
        "/api/pay/process",
        headers={"Authorization": "auth"},
        json={"paymentId": "paymentId", "sbId": "sbId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()
