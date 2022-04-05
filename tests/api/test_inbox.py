from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from smartyard.logic.user import User
from smartyard.logic.users import Users


def test_alert(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/inbox/alert",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_chat_readed(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/inbox/chatReaded",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_delivered(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/inbox/delivered",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_inbox(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/inbox/inbox",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()


def test_readed(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/inbox/readed",
        headers={"Authorization": "auth"},
        json={"1": "1"},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_unreaded(
    flask_client: FlaskClient, logic_user: User, mocker: MockerFixture
) -> None:
    mocker.patch.object(Users, "user_by_uuid", return_value=logic_user)
    response = flask_client.post(
        "/api/inbox/unreaded",
        headers={"Authorization": "auth"},
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json()
