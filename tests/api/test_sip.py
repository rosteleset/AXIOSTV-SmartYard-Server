from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.users_bank import UsersBank


def test_help_me(flask_client: FlaskClient, mocker: MockerFixture) -> None:
    mocker.patch.object(UsersBank, "search_by_uuid", return_value=(79001234567,))
    response = flask_client.post(
        "/api/sip/helpMe",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200
