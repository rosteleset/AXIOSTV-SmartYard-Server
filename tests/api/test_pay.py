"""Модуль тестирования API, ветка /api/pay"""

from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users
from smartyard.proxy import Billing


def test_prepare(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест подготовка к проведению платежа"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    mocker.patch.object(
        Billing, "create_invoice", return_value={"response": "response"}
    )

    response = flask_client.post(
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


def test_process(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    """Тест проведения платежа"""
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/pay/process",
        headers={"Authorization": "auth"},
        json={"paymentId": "paymentId", "sbId": "sbId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()
