from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.users_bank import UsersBank
from smartyard.proxy import Billing


def test_prepare(
    flask_client: FlaskClient, mocker: MockerFixture
) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
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


def test_process(flask_client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = flask_client.post(
        "/api/pay/process",
        headers={"Authorization": "auth"},
        json={"paymentId": "paymentId", "sbId": "sbId"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()
