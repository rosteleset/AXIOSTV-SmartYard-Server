import json
import os

import pytest
import requests
from flask import Flask
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard import config, create_app
from smartyard.logic.users_bank import UsersBank


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
    assert response.get_json() == mock.json()
    assert mock.args == (test_config.BILLING_URL + "createinvoice",)
    assert mock.kwargs == {
        "headers": {"Content-Type": "application/json"},
        "data": json.dumps(
            {
                "login": "clientId",
                "amount": "amount",
                "phone": 79001234567,
            }
        ),
    }


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
